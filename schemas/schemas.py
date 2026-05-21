from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    role: str = "user"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── User ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Project ─────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    asset:       str
    serial_no:   str
    location:    Optional[str] = None
    assigned_to: Optional[str] = None
    room_no:     Optional[str] = None
    division:    str
    asset_owner: str
    model:       str
    network_on:  str
    status:      str = "Inuse"

class ProjectUpdate(BaseModel):
    asset:       Optional[str] = None
    serial_no:   Optional[str] = None
    location:    Optional[str] = None
    assigned_to: Optional[str] = None
    room_no:     Optional[str] = None
    division:    Optional[str] = None
    asset_owner: Optional[str] = None
    model:       Optional[str] = None
    network_on:  Optional[str] = None
    status:      Optional[str] = None

class ProjectResponse(BaseModel):
    id:          int
    asset:       str
    serial_no:   str
    location:    Optional[str]
    assigned_to: Optional[str]
    room_no:     Optional[str]
    division:    str
    asset_owner: str
    model:       str
    network_on:  str
    is_deleted:  bool
    created_by:  int
    created_at:  datetime
    updated_by:  Optional[int]
    updated_at:  datetime
    status:      str

    model_config = {"from_attributes": True}


# ─── Audit ───────────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id:         int
    table_name: str
    record_id:  int
    field_name: str
    old_value:  Optional[str]
    new_value:  Optional[str]
    changed_by: str
    changed_at: datetime

    model_config = {"from_attributes": True}


class DeletionLogResponse(BaseModel):
    id:          int
    asset:       str
    serial_no:   str
    location:    Optional[str]
    assigned_to: Optional[str]
    room_no:     Optional[str]
    division:    str
    asset_owner: str
    model:       str
    network_on:  str
    status:      str
    deleted_by:  str
    deleted_at:  datetime

    model_config = {"from_attributes": True}