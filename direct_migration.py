#!/usr/bin/env python3
"""
Direct SQL Execution - Simpler approach that bypasses parsing issues
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Database config
config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'drdo_projects'),
    'port': int(os.getenv('DB_PORT', 3306))
}

print("Connecting to database...")
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

try:
    # Add columns to project_data
    print("\n1. Adding columns to project_data...")
    
    cursor.execute("ALTER TABLE project_data ADD COLUMN division VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'division' column")
    
    cursor.execute("ALTER TABLE project_data ADD COLUMN asset_owner VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'asset_owner' column")
    
    cursor.execute("ALTER TABLE project_data ADD COLUMN model VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'model' column")
    
    # Rename device_type to asset in project_data
    print("\n2. Renaming 'device_type' to 'asset' in project_data...")
    cursor.execute("""
        ALTER TABLE project_data 
        CHANGE COLUMN device_type asset 
        ENUM('laptop', 'cpu', 'router', 'switch', 'monitor', 'firewall') NOT NULL
    """)
    print("   ✅ Renamed column successfully")
    
    # Remove defaults (make truly required)
    print("\n3. Removing defaults from new columns...")
    cursor.execute("ALTER TABLE project_data MODIFY COLUMN division VARCHAR(100) NOT NULL")
    cursor.execute("ALTER TABLE project_data MODIFY COLUMN asset_owner VARCHAR(100) NOT NULL")
    cursor.execute("ALTER TABLE project_data MODIFY COLUMN model VARCHAR(100) NOT NULL")
    print("   ✅ Defaults removed")
    
    # Same for deletion_log
    print("\n4. Adding columns to deletion_log...")
    cursor.execute("ALTER TABLE deletion_log ADD COLUMN division VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'division' column")
    
    cursor.execute("ALTER TABLE deletion_log ADD COLUMN asset_owner VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'asset_owner' column")
    
    cursor.execute("ALTER TABLE deletion_log ADD COLUMN model VARCHAR(100) NOT NULL DEFAULT ''")
    print("   ✅ Added 'model' column")
    
    # Rename device_type to asset in deletion_log
    print("\n5. Renaming 'device_type' to 'asset' in deletion_log...")
    cursor.execute("""
        ALTER TABLE deletion_log 
        CHANGE COLUMN device_type asset VARCHAR(50) NOT NULL
    """)
    print("   ✅ Renamed column successfully")
    
    # Remove defaults
    print("\n6. Removing defaults from deletion_log columns...")
    cursor.execute("ALTER TABLE deletion_log MODIFY COLUMN division VARCHAR(100) NOT NULL")
    cursor.execute("ALTER TABLE deletion_log MODIFY COLUMN asset_owner VARCHAR(100) NOT NULL")
    cursor.execute("ALTER TABLE deletion_log MODIFY COLUMN model VARCHAR(100) NOT NULL")
    print("   ✅ Defaults removed")
    
    conn.commit()
    print("\n✅ MIGRATION COMPLETED SUCCESSFULLY!")
    
    # Verify
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    print("\nproject_data columns:")
    cursor.execute("DESCRIBE project_data")
    for row in cursor.fetchall():
        print(f"  • {row[0]:20} {row[1]}")
    
    print("\ndeletion_log columns:")
    cursor.execute("DESCRIBE deletion_log")
    for row in cursor.fetchall():
        print(f"  • {row[0]:20} {row[1]}")
    
    print("\n✅ Schema verification complete!")
    
except Error as e:
    print(f"\n❌ ERROR: {e}")
    conn.rollback()
    
finally:
    cursor.close()
    conn.close()
    print("\nDisconnected from database")
