from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, ProjectData, AuditLog, DeletionLog
from schemas.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    AuditLogResponse,
    DeletionLogResponse
)
from services.audit_service import log_change
from middleware.auth_middleware import (
    get_current_user,
    require_role
)
from typing import List

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

@router.post("", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_roles = ['super-admin', 'admin', 'user']
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role cannot create projects"
        )
    
    project = ProjectData(
        asset       = data.asset,
        serial_no   = data.serial_no,
        location    = data.location,
        assigned_to = data.assigned_to,
        room_no     = data.room_no,
        division    = data.division,
        asset_owner = data.asset_owner,
        model       = data.model,
        created_by  = current_user.id,
        updated_by  = current_user.id,
        network_on  = data.network_on,
        status      = data.status,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


# ─────────────────────────────────────────────
# LIST
# ─────────────────────────────────────────────

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ProjectData).filter(
        ProjectData.is_deleted == False
    ).all()


# ─────────────────────────────────────────────
# GET SINGLE
# ─────────────────────────────────────────────

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(ProjectData).filter(
        ProjectData.id == project_id,
        ProjectData.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Record not found")

    return project


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super-admin"))
):
    project = db.query(ProjectData).filter(
        ProjectData.id == project_id,
        ProjectData.is_deleted == False
    ).with_for_update().first()

    if not project:
        raise HTTPException(status_code=404, detail="Record not found")

    tracked_fields = [
        "asset",
        "serial_no",
        "location",
        "assigned_to",
        "room_no",
        "division",
        "asset_owner",
        "model",
        "network_on",
        "status"
    ]

    for field in tracked_fields:

        new_val = getattr(data, field)

        if new_val is not None:

            old_val = getattr(project, field)

            if str(old_val) != str(new_val):

                log_change(
                    db=db,
                    table_name="project_data",
                    record_id=project_id,
                    field_name=field,
                    old_value=old_val,
                    new_value=new_val,
                    changed_by=current_user.id
                )

                setattr(project, field, new_val)

    project.updated_by = current_user.id

    db.commit()
    db.refresh(project)

    return project


# ─────────────────────────────────────────────
# DELETE (HARD) - Only Super Admin
# ─────────────────────────────────────────────

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super-admin"))
):
    project = db.query(ProjectData).filter(
        ProjectData.id == project_id,
        ProjectData.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Record not found")

    deletion_log = DeletionLog(
        asset=project.asset,
        serial_no=project.serial_no,
        location=project.location,
        assigned_to=project.assigned_to,
        room_no=project.room_no,
        division=project.division,
        asset_owner=project.asset_owner,
        model=project.model,
        network_on=project.network_on,
        status=project.status,
        deleted_by=current_user.id
    )
    
    db.add(deletion_log)
    db.delete(project)
    db.commit()

    return {"message": "Record deleted successfully"}


# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────

@router.get("/{project_id}/history", response_model=List[AuditLogResponse])
def get_project_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == 'user':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users cannot view project history"
        )
    
    logs = db.query(AuditLog).filter(
        AuditLog.table_name == "project_data",
        AuditLog.record_id == project_id
    ).order_by(AuditLog.changed_at.desc()).all()

    result = []

    for log in logs:

        user = db.query(User).filter(User.id == log.changed_by).first()

        result.append({
            "id":         log.id,
            "table_name": log.table_name,
            "record_id":  log.record_id,
            "field_name": log.field_name,
            "old_value":  log.old_value,
            "new_value":  log.new_value,
            "changed_by": user.username if user else "Unknown",
            "changed_at": log.changed_at
        })

    return result


# ─────────────────────────────────────────────
# DELETION LOGS - Admin and Super Admin Only
# ─────────────────────────────────────────────

@router.get("/admin/deletion-logs", response_model=List[DeletionLogResponse])
def get_deletion_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super-admin"))
):
    logs = db.query(DeletionLog).order_by(DeletionLog.deleted_at.desc()).all()

    result = []

    for log in logs:
        user = db.query(User).filter(User.id == log.deleted_by).first()

        result.append({
            "id":          log.id,
            "asset":       log.asset,
            "serial_no":   log.serial_no,
            "location":    log.location,
            "assigned_to": log.assigned_to,
            "room_no":     log.room_no,
            "division":    log.division,
            "asset_owner": log.asset_owner,
            "model":       log.model,
            "network_on":  log.network_on,
            "status":      log.status,
            "deleted_by":  user.username if user else "Unknown",
            "deleted_at":  log.deleted_at
        })

    return result


# ─────────────────────────────────────────────
# AUDIT LOG MANAGEMENT - Super Admin Only
# ─────────────────────────────────────────────

@router.delete("/{project_id}/history/{log_id}")
def delete_audit_log(
    project_id: int,
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super-admin"))
):
    log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.record_id == project_id,
        AuditLog.table_name == "project_data"
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")

    db.delete(log)
    db.commit()

    return {"message": "Audit log entry deleted successfully"}


@router.put("/{project_id}/history/{log_id}")
def update_audit_log(
    project_id: int,
    log_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super-admin"))
):
    log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.record_id == project_id,
        AuditLog.table_name == "project_data"
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")

    if "old_value" in data:
        log.old_value = data["old_value"]
    if "new_value" in data:
        log.new_value = data["new_value"]

    db.commit()
    db.refresh(log)

    user = db.query(User).filter(User.id == log.changed_by).first()

    return {
        "id":         log.id,
        "table_name": log.table_name,
        "record_id":  log.record_id,
        "field_name": log.field_name,
        "old_value":  log.old_value,
        "new_value":  log.new_value,
        "changed_by": user.username if user else "Unknown",
        "changed_at": log.changed_at
    }