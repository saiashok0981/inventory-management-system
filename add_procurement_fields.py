#!/usr/bin/env python3
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

def main():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
    except Error as e:
        print(f"[FAIL] Connection failed: {e}")
        return

    try:
        print("Adding 'procurement' column to project_data...")
        try:
            cursor.execute("ALTER TABLE project_data ADD COLUMN procurement DATE NULL AFTER status")
            print("   [OK] Added 'procurement' column to project_data")
        except Error as e:
            if e.errno == 1060:  # Duplicate column name
                print("   [INFO] 'procurement' column already exists in project_data")
            else:
                raise e

        print("Adding 'procurement' column to deletion_log...")
        try:
            cursor.execute("ALTER TABLE deletion_log ADD COLUMN procurement DATE NULL AFTER status")
            print("   [OK] Added 'procurement' column to deletion_log")
        except Error as e:
            if e.errno == 1060:  # Duplicate column name
                print("   [INFO] 'procurement' column already exists in deletion_log")
            else:
                raise e

        conn.commit()
        print("[OK] Migration completed successfully!")
        
        # Verify
        print("\nChecking project_data structure:")
        cursor.execute("DESCRIBE project_data")
        for row in cursor.fetchall():
            if row[0] == 'procurement':
                print(f"  • {row[0]:20} {row[1]} {row[2]} {row[3]}")
                
        print("\nChecking deletion_log structure:")
        cursor.execute("DESCRIBE deletion_log")
        for row in cursor.fetchall():
            if row[0] == 'procurement':
                print(f"  • {row[0]:20} {row[1]} {row[2]} {row[3]}")
                
    except Error as e:
        print(f"[FAIL] Migration failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Disconnected from database")

if __name__ == "__main__":
    main()
