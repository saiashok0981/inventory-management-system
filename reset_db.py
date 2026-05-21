"""
Reset database tables to remove old enum values and recreate with new schema.
Run this once after changing enum values.
"""
from database.connection import engine
from database.models import Base

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables with new schema...")
Base.metadata.create_all(bind=engine)

print("✅ Database reset complete! All tables recreated with new schema.")
print("You can now signup with new roles: super-admin, admin, user")
