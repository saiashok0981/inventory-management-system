# Database Migration Guide

## Overview

This guide walks you through migrating your database schema to add the new `asset`, `division`, `asset_owner`, and `model` columns.

---

## Migration Files

### 1. **001_add_asset_columns.sql** (Forward Migration)
- Adds three new columns: `division`, `asset_owner`, `model`
- Renames `device_type` to `asset`
- Applies to both `project_data` and `deletion_log` tables

### 2. **001_add_asset_columns_ROLLBACK.sql** (Rollback/Downgrade)
- Removes the three new columns
- Renames `asset` back to `device_type`
- Only use if you need to revert changes

### 3. **run_migration.py** (Python Migration Runner)
- Automated script to execute migrations
- Includes schema verification
- Handles errors gracefully

---

## Method 1: Using Python Migration Runner (Recommended)

### Prerequisites
```bash
pip install mysql-connector-python python-dotenv
```

### Step 1: Verify Database Connection
Ensure your `.env` file has correct database credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=drdo_cabs
DB_USER=root
DB_PASSWORD=your_password
```

### Step 2: Run the Migration

**Forward Migration:**
```bash
python run_migration.py forward
```

Expected output:
```
============================================================
🗄️  DATABASE MIGRATION RUNNER
============================================================
✅ Connected to database: drdo_cabs

============================================================
Running FORWARD Migration: 001_add_asset_columns.sql
============================================================
✅ Executed statement 1
✅ Executed statement 2
✅ Executed statement 3
...
✅ Migration completed successfully!

============================================================
SCHEMA VERIFICATION
============================================================
📋 PROJECT_DATA Table Columns:
...
✅ Schema verification complete!
```

**Verify Schema Only:**
```bash
python run_migration.py verify
```

**Rollback (if needed):**
```bash
python run_migration.py rollback
```

---

## Method 2: Manual SQL Execution

### Using MySQL Command Line

1. **Open MySQL Connection:**
```bash
mysql -h localhost -u root -p drdo_cabs
```

2. **Run the Forward Migration:**
```bash
source 001_add_asset_columns.sql;
```

3. **Verify the Changes:**
```sql
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'project_data' 
ORDER BY ORDINAL_POSITION;
```

### Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your database
3. Open `001_add_asset_columns.sql` file
4. Execute the script (Ctrl+Shift+Enter)
5. Check the results in the Output panel

### Using PHP/Node Admin Tools

1. Upload the SQL file to your web server
2. Use phpMyAdmin or similar tool
3. Select the database: `drdo_cabs`
4. Import/Execute the SQL file

---

## What the Migration Does

### Forward Migration Changes

#### project_data Table:
```sql
-- Before:
- device_type ENUM(...)
- serial_no
- location
- assigned_to
- room_no
- network_on
- status

-- After:
- asset ENUM(...)           -- renamed from device_type
- serial_no
- location
- assigned_to
- room_no
- division VARCHAR(100)     -- NEW
- asset_owner VARCHAR(100)  -- NEW
- model VARCHAR(100)        -- NEW
- network_on
- status
```

#### deletion_log Table:
```sql
-- Before:
- device_type VARCHAR(50)

-- After:
- asset VARCHAR(50)         -- renamed from device_type
- division VARCHAR(100)     -- NEW
- asset_owner VARCHAR(100)  -- NEW
- model VARCHAR(100)        -- NEW
```

### Default Values for Existing Records

For existing records in the `project_data` table:
- `division` = '' (empty string)
- `asset_owner` = '' (empty string)
- `model` = '' (empty string)

**⚠️ Important:** You should update these empty values with appropriate data before users create new records.

---

## Post-Migration Steps

### 1. Verify Data Integrity
```sql
-- Check for records with empty new columns
SELECT id, serial_no, division, asset_owner, model 
FROM project_data 
WHERE division = '' OR asset_owner = '' OR model = '';
```

### 2. Update Existing Records (Optional)
```sql
-- Example: Update existing records with default values
UPDATE project_data 
SET division = 'General', asset_owner = 'IT Department', model = 'N/A'
WHERE division = '' OR asset_owner = '' OR model = '';
```

### 3. Test the Application
1. Start the application
2. Create a new asset with all required fields
3. Edit an existing asset
4. Verify all columns display correctly
5. Check deletion logs show new columns

### 4. Verify API Endpoints
```bash
# Test create endpoint
curl -X POST https://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "asset": "laptop",
    "serial_no": "ABC123",
    "location": "Building A",
    "assigned_to": "John Doe",
    "room_no": "101",
    "division": "IT",
    "asset_owner": "IT Manager",
    "model": "Dell XPS 13",
    "network_on": "DRONA",
    "status": "Inuse"
  }'

# Test list endpoint
curl -X GET https://localhost:8000/projects \
  -H "Authorization: Bearer {token}"
```

---

## Rollback Procedure

If you need to revert the changes:

### Using Python Script:
```bash
python run_migration.py rollback
```

### Manual Rollback:
```bash
mysql -h localhost -u root -p drdo_cabs < 001_add_asset_columns_ROLLBACK.sql
```

**⚠️ Warning:** Rollback will:
- Remove the three new columns
- Rename `asset` back to `device_type`
- Restore the original schema

Any data in the new columns will be lost.

---

## Troubleshooting

### Issue: "Column already exists"
**Solution:** The migration has already been run. Check your schema.
```bash
python run_migration.py verify
```

### Issue: "No such column"
**Solution:** The column names might be different. Check the current schema:
```sql
DESCRIBE project_data;
DESCRIBE deletion_log;
```

### Issue: Connection Error
**Solution:** Verify your database credentials in `.env` file:
```bash
# Test connection
mysql -h localhost -u root -p
```

### Issue: Foreign Key Constraint
**Solution:** If you get foreign key errors, ensure all dependent tables are updated:
```bash
# Temporarily disable foreign keys during migration
SET FOREIGN_KEY_CHECKS=0;
-- Run migration here
SET FOREIGN_KEY_CHECKS=1;
```

### Issue: Migration Failed Midway
**Solution:** Check what was executed:
```sql
-- Show table structure to see which changes applied
DESCRIBE project_data;

-- Rollback if needed
source 001_add_asset_columns_ROLLBACK.sql;
```

---

## Backup Before Migration

**Always backup your database before running migrations:**

### MySQL Dump:
```bash
mysqldump -h localhost -u root -p drdo_cabs > backup_$(date +%Y%m%d_%H%M%S).sql
```

### From MySQL CLI:
```sql
-- Create backup table
CREATE TABLE project_data_backup AS SELECT * FROM project_data;
CREATE TABLE deletion_log_backup AS SELECT * FROM deletion_log;

-- Verify backup
SELECT COUNT(*) FROM project_data_backup;
SELECT COUNT(*) FROM deletion_log_backup;
```

---

## Migration Checklist

- [ ] Database credentials verified in `.env`
- [ ] Database backup created
- [ ] Python dependencies installed (mysql-connector-python, python-dotenv)
- [ ] Forward migration executed successfully
- [ ] Schema verification completed
- [ ] Existing data checked for empty new columns
- [ ] Existing data updated with appropriate values (if needed)
- [ ] Application restarted
- [ ] New asset creation tested
- [ ] Asset editing tested
- [ ] Dashboard displays new columns
- [ ] Deletion logs display new columns
- [ ] API endpoints working correctly

---

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Review the migration script comments
4. Check MySQL error logs
5. Restore from backup and try again

---

**Last Updated:** 2026-05-21
