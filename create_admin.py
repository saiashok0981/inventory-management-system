from database.connection import SessionLocal
from database.models import User
from services.auth_service import hash_password

db = SessionLocal()
admin = User(
    username='admin',
    password_hash=hash_password('admin123'),
    role='admin'
)
db.add(admin)
db.commit()
db.refresh(admin)
print(f'Admin created: ID={admin.id}, username={admin.username}, role={admin.role}')
db.close()