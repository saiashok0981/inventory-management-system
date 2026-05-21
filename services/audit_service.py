from sqlalchemy.orm import Session
from database.models import AuditLog


def log_change(db: Session, table_name: str, record_id: int,
               field_name: str, old_value, new_value, changed_by: int):
    entry = AuditLog(
        table_name=table_name,
        record_id=record_id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        changed_by=changed_by
    )
    db.add(entry)