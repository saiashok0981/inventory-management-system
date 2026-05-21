-- Migration: 001_add_asset_columns
-- Description: Rename device_type to asset, add division, asset_owner, and model columns
-- Created: 2026-05-21
-- Status: FORWARD MIGRATION

-- ============================================================================
-- PROJECT_DATA TABLE MIGRATION
-- ============================================================================

-- Step 1: Add new columns to project_data table
ALTER TABLE project_data 
ADD COLUMN division VARCHAR(100) NOT NULL DEFAULT '' AFTER room_no,
ADD COLUMN asset_owner VARCHAR(100) NOT NULL DEFAULT '' AFTER division,
ADD COLUMN model VARCHAR(100) NOT NULL DEFAULT '' AFTER asset_owner;

-- Step 2: Rename device_type to asset
-- MySQL doesn't have direct RENAME COLUMN in all versions, so we use CHANGE
ALTER TABLE project_data 
CHANGE COLUMN device_type asset 
ENUM('laptop', 'cpu', 'router', 'switch', 'monitor', 'firewall') NOT NULL;

-- Step 3: Remove the default values (make them truly required for new records)
ALTER TABLE project_data 
MODIFY COLUMN division VARCHAR(100) NOT NULL,
MODIFY COLUMN asset_owner VARCHAR(100) NOT NULL,
MODIFY COLUMN model VARCHAR(100) NOT NULL;

-- ============================================================================
-- DELETION_LOG TABLE MIGRATION
-- ============================================================================

-- Step 1: Add new columns to deletion_log table
ALTER TABLE deletion_log 
ADD COLUMN division VARCHAR(100) NOT NULL DEFAULT '' AFTER room_no,
ADD COLUMN asset_owner VARCHAR(100) NOT NULL DEFAULT '' AFTER division,
ADD COLUMN model VARCHAR(100) NOT NULL DEFAULT '' AFTER asset_owner;

-- Step 2: Rename device_type to asset in deletion_log
ALTER TABLE deletion_log 
CHANGE COLUMN device_type asset VARCHAR(50) NOT NULL;

-- Step 3: Remove default values
ALTER TABLE deletion_log 
MODIFY COLUMN division VARCHAR(100) NOT NULL,
MODIFY COLUMN asset_owner VARCHAR(100) NOT NULL,
MODIFY COLUMN model VARCHAR(100) NOT NULL;

-- ============================================================================
-- VERIFICATION QUERIES (uncomment to verify)
-- ============================================================================

-- Verify project_data table structure
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'project_data' AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;

-- Verify deletion_log table structure
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'deletion_log' AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;

-- Show project_data records with new columns
-- SELECT id, asset, serial_no, division, asset_owner, model FROM project_data LIMIT 5;
