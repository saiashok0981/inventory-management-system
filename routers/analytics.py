from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, ProjectData
from middleware.auth_middleware import get_current_user, require_role
from sqlalchemy import func
from typing import Dict, List, Any

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ─────────────────────────────────────────────
# HELPER FUNCTION TO CHECK SUPER-ADMIN ACCESS
# ─────────────────────────────────────────────

def check_super_admin(current_user: User = Depends(get_current_user)):
    """Verify current user is super-admin"""
    if current_user.role != 'super-admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super-admin can access analytics dashboard"
        )
    return current_user


# ─────────────────────────────────────────────
# ASSET COUNT STATISTICS
# ─────────────────────────────────────────────

@router.get("/total-assets", dependencies=[Depends(check_super_admin)])
def get_total_assets(db: Session = Depends(get_db)):
    """Get total count of all assets"""
    total = db.query(func.count(ProjectData.id)).filter(
        ProjectData.is_deleted == False
    ).scalar()
    return {"total_assets": total or 0}


@router.get("/assets-by-type", dependencies=[Depends(check_super_admin)])
def get_assets_by_type(db: Session = Depends(get_db)):
    """Get asset count grouped by asset type"""
    results = db.query(
        ProjectData.asset,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.asset).all()
    
    return [
        {"asset_type": row[0], "count": row[1]} 
        for row in results
    ]


@router.get("/assets-by-location", dependencies=[Depends(check_super_admin)])
def get_assets_by_location(db: Session = Depends(get_db)):
    """Get asset count grouped by location"""
    results = db.query(
        ProjectData.location,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False,
        ProjectData.location != None
    ).group_by(ProjectData.location).order_by(
        func.count(ProjectData.id).desc()
    ).all()
    
    return [
        {"location": row[0] or "Unknown", "count": row[1]} 
        for row in results
    ]


@router.get("/assets-by-status", dependencies=[Depends(check_super_admin)])
def get_assets_by_status(db: Session = Depends(get_db)):
    """Get asset count grouped by status"""
    results = db.query(
        ProjectData.status,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.status).all()
    
    return [
        {"status": row[0], "count": row[1]} 
        for row in results
    ]


@router.get("/assets-by-division", dependencies=[Depends(check_super_admin)])
def get_assets_by_division(db: Session = Depends(get_db)):
    """Get asset count grouped by division"""
    results = db.query(
        ProjectData.division,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.division).order_by(
        func.count(ProjectData.id).desc()
    ).all()
    
    return [
        {"division": row[0], "count": row[1]} 
        for row in results
    ]


# ─────────────────────────────────────────────
# COMPREHENSIVE ANALYTICS DASHBOARD DATA
# ─────────────────────────────────────────────

@router.get("/dashboard", dependencies=[Depends(check_super_admin)])
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get all analytics dashboard data in one call"""
    
    # Total assets
    total_assets = db.query(func.count(ProjectData.id)).filter(
        ProjectData.is_deleted == False
    ).scalar() or 0
    
    # Assets by type
    assets_by_type = db.query(
        ProjectData.asset,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.asset).all()
    
    # Assets by location
    assets_by_location = db.query(
        ProjectData.location,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False,
        ProjectData.location != None
    ).group_by(ProjectData.location).order_by(
        func.count(ProjectData.id).desc()
    ).all()
    
    # Assets by status
    assets_by_status = db.query(
        ProjectData.status,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.status).all()
    
    # Assets by division
    assets_by_division = db.query(
        ProjectData.division,
        func.count(ProjectData.id).label("count")
    ).filter(
        ProjectData.is_deleted == False
    ).group_by(ProjectData.division).order_by(
        func.count(ProjectData.id).desc()
    ).all()
    
    return {
        "total_assets": total_assets,
        "by_type": [{"asset_type": row[0], "count": row[1]} for row in assets_by_type],
        "by_location": [{"location": row[0] or "Unknown", "count": row[1]} for row in assets_by_location],
        "by_status": [{"status": row[0], "count": row[1]} for row in assets_by_status],
        "by_division": [{"division": row[0], "count": row[1]} for row in assets_by_division]
    }
