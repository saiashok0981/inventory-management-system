from pydantic import BaseModel, computed_field, field_validator
from typing import Optional
from datetime import datetime, date


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
    procurement: Optional[date] = None

    @field_validator('serial_no')
    @classmethod
    def validate_serial_no(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Serial number is required and cannot be empty")
        return v.strip()

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
    procurement: Optional[date] = None

    @field_validator('serial_no')
    @classmethod
    def validate_serial_no(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Serial number cannot be empty")
            return v.strip()
        return v

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
    procurement: Optional[date]

    model_config = {"from_attributes": True}
    
    @computed_field
    @property
    def display_id(self) -> str:
        """Generate display ID in format LAP01, CPU01, etc."""
        asset_prefixes = {
            'laptop': 'LAP',
            'cpu': 'CPU',
            'router': 'ROU',
            'switch': 'SWI',
            'monitor': 'MON',
            'firewall': 'FIR'
        }
        prefix = asset_prefixes.get(self.asset, 'UNK')
        return f"{prefix}{self.id:02d}"


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
    procurement: Optional[date]

    model_config = {"from_attributes": True}