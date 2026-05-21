-- Rollback Migration: 001_add_asset_columns
-- Description: Revert changes - rename asset back to device_type, remove new columns
-- Created: 2026-05-21
-- Status: ROLLBACK/DOWNGRADE

-- ============================================================================
-- PROJECT_DATA TABLE ROLLBACK
-- ============================================================================

-- Step 1: Rename asset back to device_type
ALTER TABLE project_data 
CHANGE COLUMN asset device_type 
ENUM('laptop', 'cpu', 'router', 'switch', 'monitor', 'firewall') NOT NULL;

-- Step 2: Drop the new columns
ALTER TABLE project_data 
DROP COLUMN division,
DROP COLUMN asset_owner,
DROP COLUMN model;

-- ============================================================================
-- DELETION_LOG TABLE ROLLBACK
-- ============================================================================

-- Step 1: Rename asset back to device_type
ALTER TABLE deletion_log 
CHANGE COLUMN asset device_type VARCHAR(50) NOT NULL;

-- Step 2: Drop the new columns
ALTER TABLE deletion_log 
DROP COLUMN division,
DROP COLUMN asset_owner,
DROP COLUMN model;

-- ============================================================================
-- VERIFICATION (uncomment to verify rollback)
-- ============================================================================

-- Verify project_data table structure is reverted
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'project_data' AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;

-- Verify deletion_log table structure is reverted
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'deletion_log' AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;
