from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, TIMESTAMP, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum('super-admin', 'admin', 'user'), nullable=False, default='user')
    created_at    = Column(TIMESTAMP, server_default=func.now())


class ProjectData(Base):
    __tablename__ = "project_data"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    asset       = Column(
                    Enum('laptop', 'cpu', 'router', 'switch', 'monitor', 'firewall'),
                    nullable=False
                  )
    serial_no   = Column(String(100), unique=True, nullable=False)
    location    = Column(String(200), nullable=True)
    assigned_to = Column(String(100), nullable=True)   # displayed as "User"
    room_no     = Column(String(50),  nullable=True)
    division    = Column(String(100), nullable=False)
    asset_owner = Column(String(100), nullable=False)
    model       = Column(String(100), nullable=False)
    network_on  = Column(
                    Enum('DRONA', 'project', 'internet', 'stand-alone'),
                    nullable=False
                  )
    status      = Column(
                Enum('Inuse', 'put-up for condemnd', 'condemnd'),
                nullable=False,
                default='Inuse'
              )
    procurement = Column(Date, nullable=True)
    is_deleted  = Column(Boolean, default=False)
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(TIMESTAMP, server_default=func.now())
    updated_by  = Column(Integer, ForeignKey("users.id"))
    updated_at  = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class AuditLog(Base):
    __tablename__ = "audit_log"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False)
    record_id  = Column(Integer, nullable=False)
    field_name = Column(String(50), nullable=False)
    old_value  = Column(Text)
    new_value  = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(TIMESTAMP, server_default=func.now())

    changer = relationship("User", foreign_keys=[changed_by])


class DeletionLog(Base):
    __tablename__ = "deletion_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    asset       = Column(String(50), nullable=False)
    serial_no   = Column(String(100), nullable=False)
    location    = Column(String(200), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    room_no     = Column(String(50), nullable=True)
    division    = Column(String(100), nullable=False)
    asset_owner = Column(String(100), nullable=False)
    model       = Column(String(100), nullable=False)
    network_on  = Column(String(50), nullable=False)
    status      = Column(String(50), nullable=False)
    procurement = Column(Date, nullable=True)
    deleted_by  = Column(Integer, ForeignKey("users.id"))
    deleted_at  = Column(TIMESTAMP, server_default=func.now())

    deleter = relationship("User", foreign_keys=[deleted_by])