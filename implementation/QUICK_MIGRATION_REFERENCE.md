# Quick Migration Reference

## TL;DR - Fast Track

### Option A: Automated (Recommended)
```bash
# 1. Install dependencies (one time)
pip install mysql-connector-python python-dotenv

# 2. Run migration
python run_migration.py forward

# 3. Verify
python run_migration.py verify
```

### Option B: Manual SQL
```bash
# Connect to database
mysql -h localhost -u root -p drdo_cabs

# Run migration
source 001_add_asset_columns.sql;

# Verify
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME='project_data' ORDER BY ORDINAL_POSITION;
```

---

## What Gets Changed

| Before | After |
|--------|-------|
| `device_type` | `asset` |
| (no division) | `division` ✨ NEW |
| (no asset_owner) | `asset_owner` ✨ NEW |
| (no model) | `model` ✨ NEW |

---

## Files in This Package

```
📁 Project Root
├── 001_add_asset_columns.sql           ← Forward migration
├── 001_add_asset_columns_ROLLBACK.sql  ← Undo migration
├── run_migration.py                    ← Automated runner
├── MIGRATION_GUIDE.md                  ← Full guide (you are here)
└── QUICK_MIGRATION_REFERENCE.md        ← This file
```

---

## Common Commands

### Run Forward Migration
```bash
python run_migration.py forward
```

### Check Current Schema
```bash
python run_migration.py verify
```

### Undo Changes (if needed)
```bash
python run_migration.py rollback
```

---

## After Migration

1. ✅ Restart your application
2. ✅ Test creating a new asset with all fields
3. ✅ Test editing an existing asset
4. ✅ Check dashboard shows new columns

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection error | Check `.env` file DB credentials |
| Column already exists | Migration already ran, use `verify` |
| Permission denied | Check MySQL user has ALTER TABLE rights |
| Foreign key error | Temporarily disable FK checks |

---

## Rollback Steps

```bash
# If something goes wrong:
python run_migration.py rollback

# Verify it's rolled back:
python run_migration.py verify
```

---

## Need Help?

See `MIGRATION_GUIDE.md` for:
- Detailed explanations
- Backup procedures
- Manual execution steps
- Full troubleshooting guide

---

**Created:** 2026-05-21
