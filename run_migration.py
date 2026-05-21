#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migration scripts against the database
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class MigrationRunner:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"✅ Connected to database: {self.database}")
            return True
        except Error as err:
            print(f"❌ Connection failed: {err}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Disconnected from database")
    
    def execute_migration(self, sql_file, rollback=False):
        """Execute a single migration file"""
        if not os.path.exists(sql_file):
            print(f"❌ Migration file not found: {sql_file}")
            return False
        
        try:
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            cursor = self.connection.cursor()
            migration_type = "ROLLBACK" if rollback else "FORWARD"
            
            print(f"\n{'='*60}")
            print(f"Running {migration_type} Migration: {Path(sql_file).name}")
            print(f"{'='*60}")
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            executed = 0
            for statement in statements:
                # Remove line comments
                lines = [line for line in statement.split('\n') 
                        if line.strip() and not line.strip().startswith('--')]
                clean_statement = ' '.join(lines).strip()
                
                # Skip if empty after cleaning
                if not clean_statement:
                    continue
                
                try:
                    cursor.execute(clean_statement)
                    executed += 1
                    print(f"✅ Executed statement {executed}")
                except Error as err:
                    if "No such column" not in str(err) and "1061" not in str(err):
                        print(f"⚠️  Warning: {err}")
                        # Continue with next statement
            
            self.connection.commit()
            print(f"\n✅ Migration completed successfully!")
            print(f"   Total statements executed: {executed}")
            cursor.close()
            return True
            
        except Exception as err:
            print(f"❌ Migration failed: {err}")
            self.connection.rollback()
            return False
    
    def verify_schema(self):
        """Verify the new schema"""
        try:
            cursor = self.connection.cursor()
            
            print("\n" + "="*60)
            print("SCHEMA VERIFICATION")
            print("="*60)
            
            # Check project_data columns
            print("\n📋 PROJECT_DATA Table Columns:")
            print("-" * 60)
            cursor.execute("""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'project_data' AND TABLE_SCHEMA = %s
                ORDER BY ORDINAL_POSITION
            """, (self.database,))
            
            for row in cursor.fetchall():
                col_name, col_type, nullable, default = row
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                print(f"  • {col_name:20} {col_type:30} {nullable_str:10} {default_str}")
            
            # Check deletion_log columns
            print("\n📋 DELETION_LOG Table Columns:")
            print("-" * 60)
            cursor.execute("""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'deletion_log' AND TABLE_SCHEMA = %s
                ORDER BY ORDINAL_POSITION
            """, (self.database,))
            
            for row in cursor.fetchall():
                col_name, col_type, nullable, default = row
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                print(f"  • {col_name:20} {col_type:30} {nullable_str:10} {default_str}")
            
            # Show sample data
            print("\n📊 Sample Data (project_data - first 3 records):")
            print("-" * 60)
            cursor.execute("SELECT id, asset, serial_no, division, asset_owner, model FROM project_data LIMIT 3")
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    print(f"  ID: {row[0]:5} | Asset: {row[1]:15} | Serial: {row[2]:20} | Division: {row[3]:15} | Owner: {row[4]:15} | Model: {row[5]:15}")
            else:
                print("  No records found in project_data table")
            
            cursor.close()
            print("\n✅ Schema verification complete!")
            return True
            
        except Exception as err:
            print(f"❌ Verification failed: {err}")
            return False


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🗄️  DATABASE MIGRATION RUNNER")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python run_migration.py forward   - Run forward migration")
        print("  python run_migration.py rollback  - Rollback migration")
        print("  python run_migration.py verify    - Verify schema only")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    migration_file = "001_add_asset_columns.sql"
    rollback_file = "001_add_asset_columns_ROLLBACK.sql"
    
    runner = MigrationRunner()
    
    if not runner.connect():
        sys.exit(1)
    
    try:
        if command == "forward":
            if runner.execute_migration(migration_file, rollback=False):
                runner.verify_schema()
        elif command == "rollback":
            confirm = input("\n⚠️  WARNING: This will rollback all changes. Continue? (yes/no): ")
            if confirm.lower() == "yes":
                if runner.execute_migration(rollback_file, rollback=True):
                    runner.verify_schema()
            else:
                print("❌ Rollback cancelled")
        elif command == "verify":
            runner.verify_schema()
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    
    finally:
        runner.disconnect()


if __name__ == "__main__":
    main()
