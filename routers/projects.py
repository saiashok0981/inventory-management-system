from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO, StringIO
import csv
import re
from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
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
from re import search as regex_search

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

IMPORTABLE_FIELDS = [
    "asset",
    "serial_no",
    "location",
    "assigned_to",
    "room_no",
    "division",
    "asset_owner",
    "model",
    "network_on",
    "status",
]

REQUIRED_IMPORT_FIELDS = [
    "asset",
    "serial_no",
    "division",
    "asset_owner",
    "model",
    "network_on",
]

HEADER_FIELD_MAP = {
    "asset": "asset",
    "serialno": "serial_no",
    "serialnumber": "serial_no",
    "serial": "serial_no",
    "location": "location",
    "assignedto": "assigned_to",
    "assigned_user": "assigned_to",
    "user": "assigned_to",
    "roomno": "room_no",
    "room": "room_no",
    "division": "division",
    "assetowner": "asset_owner",
    "owner": "asset_owner",
    "assetownername": "asset_owner",
    "model": "model",
    "networkon": "network_on",
    "network": "network_on",
    "status": "status",
}


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower().strip())


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(lines: List[str], title: str = "Asset Logs") -> bytes:
    page_width = 792
    page_height = 612
    left = 36
    top = 40
    line_height = 12
    lines_per_page = 36

    chunks = [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)] or [[]]

    objects: List[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{' '.join(f'{4 + i * 2} 0 R' for i in range(len(chunks)))}] /Count {len(chunks)} >>".encode("latin1"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    for page_index, chunk in enumerate(chunks):
        content_lines = [
            "BT",
            "/F1 10 Tf",
            f"{left} {page_height - top} Td",
        ]
        for line_index, line in enumerate(chunk):
            if line_index > 0:
                content_lines.append(f"0 -{line_height} Td")
            content_lines.append(f"({pdf_escape(line)}) Tj")
        content_lines.append("ET")
        content = "\n".join(content_lines).encode("latin1")
        content_obj_num = 5 + page_index * 2
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj_num} 0 R >>".encode("latin1")
        )
        objects.append(b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii"))
    return bytes(pdf)


def extract_pdf_text_lines(file_bytes: bytes) -> List[str]:
    text_lines: List[str] = []
    for stream_match in re.finditer(rb"stream\s*(.*?)\s*endstream", file_bytes, re.S):
        stream = stream_match.group(1)
        for literal in re.finditer(rb"\((?:\\.|[^\\)])*\)", stream, re.S):
            raw = literal.group(0)[1:-1]
            raw = raw.replace(rb"\\", b"\\").replace(rb"\(", b"(").replace(rb"\)", b")")
            try:
                decoded = raw.decode("latin1")
            except UnicodeDecodeError:
                continue
            decoded = decoded.strip()
            if decoded:
                text_lines.append(decoded)
    return text_lines


def normalize_import_value(field_name: str, value: Any):
    if value is None:
        return None

    text = str(value).strip()
    if text == "":
        return None

    if field_name == "asset":
        return text.lower()

    if field_name == "network_on":
        normalized = text.lower().replace(" ", "-").replace("_", "-")
        network_map = {
            "drona": "DRONA",
            "project": "project",
            "internet": "internet",
            "stand-alone": "stand-alone",
            "standalone": "stand-alone",
        }
        return network_map.get(normalized, text)

    if field_name == "status":
        normalized = text.lower().replace(" ", " ")
        status_map = {
            "inuse": "Inuse",
            "put-up for condemnd": "put-up for condemnd",
            "put up for condemnd": "put-up for condemnd",
            "condemnd": "condemnd",
        }
        return status_map.get(normalized, text)

    return text


def row_to_project_data(row: Dict[str, Any]) -> Dict[str, Any]:
    mapped: Dict[str, Any] = {}

    for raw_key, raw_value in row.items():
        if raw_key is None:
            continue

        key = normalize_header(str(raw_key))
        field_name = HEADER_FIELD_MAP.get(key)
        if not field_name:
            continue

        mapped[field_name] = normalize_import_value(field_name, raw_value)

    return mapped


def parse_csv_rows(file_bytes: bytes) -> List[Dict[str, Any]]:
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be encoded as UTF-8"
        ) from exc

    reader = csv.DictReader(StringIO(text))
    return [row_to_project_data(row) for row in reader]


def parse_pdf_rows(file_bytes: bytes) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    lines = extract_pdf_text_lines(file_bytes)
    if not lines:
        return rows

    header_line_index = None
    headers: List[str] = []
    for index, line in enumerate(lines):
        possible_headers = [part.strip() for part in re.split(r"\s{2,}|\t|\|", line) if part.strip()]
        if len(possible_headers) >= 2 and any(normalize_header(part) in HEADER_FIELD_MAP for part in possible_headers):
            headers = possible_headers
            header_line_index = index
            break

    if not headers:
        return rows

    for line in lines[header_line_index + 1:]:
        parts = [part.strip() for part in re.split(r"\s{2,}|\t|\|", line) if part.strip()]
        if len(parts) < 2:
            continue

        record = {headers[i]: parts[i] for i in range(min(len(headers), len(parts)))}
        mapped = row_to_project_data(record)
        if mapped:
            rows.append(mapped)

    return rows


# ─────────────────────────────────────────────
# GENERATE SERIAL NUMBER
# ─────────────────────────────────────────────

@router.get("/serial/next/{asset_type}")
def get_next_serial_number(
    asset_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate the next serial number for a given asset type"""
    
    asset_prefixes = {
        'laptop': 'LAP',
        'cpu': 'CPU',
        'router': 'ROU',
        'switch': 'SWI',
        'monitor': 'MON',
        'firewall': 'FIR'
    }
    
    if asset_type not in asset_prefixes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset type"
        )
    
    prefix = asset_prefixes[asset_type]
    
    # Query all serial numbers for this asset type
    projects = db.query(ProjectData).filter(
        ProjectData.asset == asset_type,
        ProjectData.is_deleted == False
    ).all()
    
    # Extract the numeric part from existing serial numbers
    max_number = 0
    for project in projects:
        match = regex_search(r'(\d+)$', project.serial_no)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    
    # Generate the next serial number
    next_number = max_number + 1
    next_serial = f"{prefix}{next_number:02d}"
    
    return {"serial_no": next_serial}

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
# IMPORT / EXPORT
# ─────────────────────────────────────────────

@router.post("/import")
def import_projects(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename = (file.filename or "").lower()
    if not filename.endswith((".csv", ".pdf")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and PDF files are supported"
        )

    file_bytes = file.file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    rows = parse_csv_rows(file_bytes) if filename.endswith(".csv") else parse_pdf_rows(file_bytes)
    rows = [row for row in rows if row]
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No asset rows were found in the uploaded file"
        )

    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors: List[str] = []

    for index, row in enumerate(rows, start=1):
        if not row:
            skipped_count += 1
            continue

        serial_no = row.get("serial_no")
        if not serial_no:
            errors.append(f"Row {index}: missing serial_no")
            skipped_count += 1
            continue

        existing = db.query(ProjectData).filter(
            ProjectData.serial_no == serial_no
        ).first()

        try:
            if existing:
                for field in IMPORTABLE_FIELDS:
                    if field == "serial_no":
                        continue

                    new_value = row.get(field)
                    if new_value is None:
                        continue

                    old_value = getattr(existing, field)
                    if str(old_value) != str(new_value):
                        log_change(
                            db=db,
                            table_name="project_data",
                            record_id=existing.id,
                            field_name=field,
                            old_value=old_value,
                            new_value=new_value,
                            changed_by=current_user.id
                        )
                        setattr(existing, field, new_value)

                existing.updated_by = current_user.id
                db.commit()
                updated_count += 1
                continue

            missing_fields = [
                field for field in REQUIRED_IMPORT_FIELDS
                if not row.get(field)
            ]
            if "status" not in row or not row.get("status"):
                row["status"] = "Inuse"

            if missing_fields:
                errors.append(
                    f"Row {index}: missing required fields: {', '.join(missing_fields)}"
                )
                skipped_count += 1
                continue

            project = ProjectData(
                asset=row["asset"],
                serial_no=row["serial_no"],
                location=row.get("location"),
                assigned_to=row.get("assigned_to"),
                room_no=row.get("room_no"),
                division=row["division"],
                asset_owner=row["asset_owner"],
                model=row["model"],
                network_on=row["network_on"],
                status=row["status"],
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            db.add(project)
            db.commit()
            created_count += 1
        except IntegrityError:
            db.rollback()
            errors.append(f"Row {index}: database constraint error")
        except HTTPException:
            db.rollback()
            raise

    return {
        "message": "Import completed",
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors,
    }


@router.get("/export")
def export_projects_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = db.query(ProjectData).filter(
        ProjectData.is_deleted == False
    ).order_by(ProjectData.id.asc()).all()

    lines = [
        "Asset Logs",
        "ID  Asset  Serial No  Location  User  Room No  Division  Asset Owner  Model  Network On  Status",
    ]
    for project in projects:
        lines.append(
            f"{project.id}  {project.asset}  {project.serial_no}  {project.location or '-'}  "
            f"{project.assigned_to or '-'}  {project.room_no or '-'}  {project.division}  "
            f"{project.asset_owner}  {project.model}  {project.network_on}  {project.status}"
        )

    buffer = BytesIO(build_simple_pdf(lines))

    headers = {
        "Content-Disposition": 'attachment; filename="asset_logs.pdf"'
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)


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
