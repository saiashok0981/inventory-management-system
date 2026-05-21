# 🔐 DRDO CABS - Project Management System

## 📋 Overview

**DRDO CABS (Computer Asset Base System)** is a secure, role-based project management platform designed for internal DRDO (Defence Research and Development Organisation) operations. It provides comprehensive asset tracking, management, and audit capabilities with full accountability and security features.

### Key Features
- 🔒 **Secure HTTPS** - SSL/TLS encrypted communication
- 👥 **Role-Based Access Control** - Three-tier permission system
- 📊 **Asset Management** - Track IT devices across the organization
- 📝 **Full Audit Trail** - Every change is logged and traceable
- 🗑️ **Deletion Tracking** - Maintains records of deleted assets
- 🔐 **JWT Authentication** - Token-based secure authentication
- 📱 **Responsive UI** - Clean, intuitive web interface
- ⚡ **Fast API** - Built with FastAPI for high performance

---

## 🎯 What This Project Does

### Core Functionality

**DRDO CABS** is an **Asset & Project Management System** for tracking IT equipment and devices across organizational facilities. It enables:

1. **Device Inventory Management**
   - Register and track laptops, CPUs, routers, switches, monitors, firewalls
   - Maintain unique serial numbers for each device
   - Track device locations and room assignments
   - Monitor device status (in-use, pending condemnation, condemned)

2. **Network Assignment Tracking**
   - Assign devices to different networks: DRONA, Project, Internet, Stand-alone
   - Track which network each device is connected to
   - Manage device assignments to users/departments

3. **Audit & Compliance**
   - Complete audit trail of all changes
   - Track who made what changes and when
   - Maintain historical records for compliance
   - Full deletion logs for accountability

4. **Multi-User Management**
   - Create and manage user accounts
   - Assign role-based permissions
   - Secure authentication with JWT tokens

---

## 👥 User Roles & Permissions

The system has **3 distinct roles** with increasing levels of authority:

### 1. **👤 Regular User** 
**Role Code:** `user`

#### Capabilities:
- ✅ View projects/devices (read-only for assigned projects)
- ✅ Create new projects/devices
- ✅ Update projects they have access to
- ✅ View audit logs for their changes
- ✅ Login and access the dashboard

#### Limitations:
- ❌ Cannot create or manage users
- ❌ Cannot delete other users' records
- ❌ Cannot change user roles
- ❌ Limited to their own created records (with admin approval)

#### Use Case:
- IT technicians managing day-to-day device inventory
- Department heads tracking their assigned equipment
- Project leads documenting project resources

---

### 2. **🛡️ Administrator**
**Role Code:** `admin`

#### Capabilities:
- ✅ **All Regular User capabilities** +
- ✅ Create new user accounts
- ✅ List all users in the system
- ✅ Assign user roles (create admins)
- ✅ View all projects/devices (read/write)
- ✅ Update project status and ownership
- ✅ Manage device assignments
- ✅ View complete audit logs
- ✅ Access deletion logs

#### Limitations:
- ❌ Cannot delete users directly (super-admin only)
- ❌ Cannot modify super-admin accounts
- ❌ Cannot change system-level settings

#### Use Case:
- IT Department managers overseeing all device inventory
- System administrators managing user access
- Compliance officers reviewing audit trails
- Department coordinators handling asset allocation

---

### 3. **👑 Super Administrator**
**Role Code:** `super-admin`

#### Capabilities:
- ✅ **All Administrator capabilities** +
- ✅ Full system access without restrictions
- ✅ Create and demote other super-admins
- ✅ Delete user accounts
- ✅ Modify all project records
- ✅ Override any permission
- ✅ Access system logs and reports
- ✅ Manage critical configurations

#### Limitations:
- None - Full system control

#### Use Case:
- DRDO IT Chief overseeing entire asset management
- System administrators with full control
- Chief Information Security Officer (CISO)
- Executive leadership requiring complete oversight

---

## 🔄 Permission Matrix

| Action | User | Admin | Super-Admin |
|--------|------|-------|-------------|
| View own projects | ✅ | ✅ | ✅ |
| Create projects | ✅ | ✅ | ✅ |
| Update own projects | ✅ | ✅ | ✅ |
| View all projects | ❌ | ✅ | ✅ |
| Update any project | ❌ | ✅ | ✅ |
| Delete projects | ❌ | ⚠️ Soft | ✅ |
| Create users | ❌ | ✅ | ✅ |
| List all users | ❌ | ✅ | ✅ |
| Delete users | ❌ | ❌ | ✅ |
| Assign admin role | ❌ | ❌ | ✅ |
| View audit logs | ✅ Limited | ✅ All | ✅ All |

---

## 📱 System Architecture

### Technology Stack
- **Backend:** Python FastAPI
- **Database:** MySQL with SQLAlchemy ORM
- **Authentication:** JWT (JSON Web Tokens)
- **Security:** HTTPS with SSL/TLS certificates
- **Frontend:** HTML/CSS/JavaScript
- **Server:** Uvicorn ASGI server

### Database Schema

#### Users Table
```
- id (Primary Key)
- username (Unique)
- password_hash (Encrypted)
- role (super-admin, admin, user)
- created_at (Timestamp)
```

#### Project Data Table
```
- id (Primary Key)
- asset (laptop, cpu, router, switch, monitor, firewall)
- serial_no (Unique)
- location (Building/Room location)
- assigned_to (User/Department)
- room_no (Physical room number)
- division (Division name)
- asset_owner (Owner name)
- model (Model details)
- network_on (DRONA, project, internet, stand-alone)
- status (Inuse, put-up for condemned, condemned)
- created_by (User ID)
- updated_by (User ID)
- is_deleted (Soft delete flag)
- created_at / updated_at (Timestamps)
```

#### Audit Log Table
```
- id (Primary Key)
- table_name (Which table was modified)
- record_id (Which record)
- field_name (Which field changed)
- old_value / new_value (Before/After values)
- changed_by (User ID)
- changed_at (Timestamp)
```

#### Deletion Log Table
```
- id (Primary Key)
- Complete device information at time of deletion
- deleted_by (User ID)
- deleted_at (Timestamp)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd agents-http-to-https-migration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```


4. **Start the HTTPS server**
   ```bash
   python run_https.py
   ```

5. **Access the application**
   - Web App: `https://localhost:8000`
   - API Docs: `https://localhost:8000/docs`

### Create Initial Admin User

```bash
python create_admin.py
```

Follow the prompts to create your first super-admin account.

---

## 🔌 API Endpoints

### Authentication
```
POST   /auth/login      - User login
POST   /auth/signup     - User registration
```

### Projects
```
POST   /projects        - Create new project (requires auth)
GET    /projects        - List projects
GET    /projects/{id}   - Get project details
PUT    /projects/{id}   - Update project
DELETE /projects/{id}   - Delete project (soft delete)
GET    /projects/history/{id} - View project history
```

### Users
```
POST   /users           - Create user (admin only)
GET    /users           - List all users (admin only)
GET    /users/{id}      - Get user details
PUT    /users/{id}      - Update user
DELETE /users/{id}      - Delete user (super-admin only)
```

### Audit & Logs
```
GET    /audit-logs      - View all audit logs (admin+)
GET    /deletion-logs   - View deletion logs (admin+)
GET    /health          - Health check
```

---

## 🔒 Security Features

### Authentication & Authorization
- JWT-based token authentication
- Secure password hashing with bcrypt
- Role-based access control (RBAC)
- Token expiration: 30 minutes (configurable)

### Data Protection
- HTTPS/SSL encryption for all traffic
- Self-signed certificates for development
- Real CA certificates for production
- Password minimum 6 characters
- Unique username enforcement

### Audit & Compliance
- Complete audit trail of all changes
- Immutable deletion logs
- Timestamp verification
- User identification for all actions
- Soft delete (no data loss)

---

## 📊 Use Cases & Workflows

### Scenario 1: New Device Registration
1. **IT Technician (User)** receives new laptop
2. Logs into dashboard
3. Creates project entry with device details
4. Assigns to network and location
5. System logs the creation automatically
6. **Admin** approves if needed
7. Device is now tracked in system

### Scenario 2: Device Transfer
1. **User** needs to move device to different location
2. Updates project record with new location
3. Changes assigned_to field
4. System creates audit log entry
5. **Admin** can view complete transfer history
6. All changes are timestamped and traceable

### Scenario 3: Device Decommissioning
1. Device becomes obsolete
2. **Admin** marks status as "condemned"
3. Marks is_deleted flag (soft delete)
4. Deletion log captures complete device info
5. Device no longer appears in active list
6. Historical data preserved for compliance

### Scenario 4: Audit & Compliance
1. **Compliance Officer** needs device history
2. Accesses audit logs
3. Views all changes to specific device
4. Sees who made changes, when, and what changed
5. Exports report for compliance documentation

---

## 🛠️ Configuration



### Running Without HTTPS (Development)
```bash
uvicorn main:app --reload
```

### Running on Custom Port
Edit `run_https.py`:
```python
uvicorn.run(..., port=8443, ...)
```

---

## 📚 Documentation Files

- **QUICKSTART.md** - Quick start guide for all platforms
- **HTTPS_MIGRATION.md** - HTTPS setup and SSL details
- **HTTPS_IMPLEMENTATION.md** - Technical implementation details
- **MIGRATION_SUMMARY.md** - Migration summary and changes

---

## 🧪 Testing

### Health Check
```bash
curl -k https://localhost:8000/health
```

### Login Test
```bash
curl -k -X POST https://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

### API Documentation
Visit: `https://localhost:8000/docs` (Swagger UI)

---

## 🔧 Troubleshooting

### Certificate Errors
```bash
# Regenerate certificates
python generate_certs.py
```

### Database Connection Failed
```bash
# Check MySQL is running
# Verify .env configuration
# Ensure database exists
```

### Port Already in Use
```bash
# Kill existing process
taskkill /IM python.exe /F

# Or use different port in run_https.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📞 Support & Contact

For issues, questions, or feature requests:
1. Check documentation files
2. Review API documentation at `/docs`
3. Check application logs in terminal

---



## 🎉 Quick Start Commands

```bash
# Start HTTPS Server
python run_https.py

# Or use batch file (Windows)
run_https.bat

# Or use shell script (macOS/Linux)
./run_https.sh

# Create initial admin user
python create_admin.py

# Reset database
python reset_db.py
```

---

## 📈 Version History

- **v1.0.0** - Initial release with HTTPS support
- Features: User authentication, Project management, Audit logs, Role-based access control

---

**Stay secure! 🔒**
