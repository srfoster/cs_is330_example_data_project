"""
Database Schema Initialization Script
Creates SQLite database with course_prefixes table for Olympic College data
"""

import sqlite3
import os
from datetime import datetime

def create_database_schema(db_path="course_catalog.db"):
    """
    Create the database schema for storing course prefix data
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    
    print("🗄️  Database Schema Initializer")
    print("=" * 40)
    
    # Check if database already exists
    if os.path.exists(db_path):
        response = input(f"⚠️  Database '{db_path}' already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled.")
            return False
        else:
            os.remove(db_path)
            print("🗑️  Existing database removed.")
    
    try:
        # Connect to SQLite database (creates file if doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"📁 Creating database: {db_path}")
        
        # Create course_prefixes table
        create_table_sql = """
        CREATE TABLE course_prefixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prefix_code VARCHAR(10) NOT NULL UNIQUE,
            institution VARCHAR(100) DEFAULT 'Olympic College',
            institution_code VARCHAR(10) DEFAULT 'WA030',
            extracted_at TIMESTAMP,
            source_url TEXT,
            extraction_method VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ Created table: course_prefixes")
        
        # Create index for faster lookups
        create_index_sql = """
        CREATE INDEX idx_prefix_code ON course_prefixes(prefix_code);
        """
        
        cursor.execute(create_index_sql)
        print("✅ Created index: idx_prefix_code")
        
        # Create trigger to update 'updated_at' timestamp
        create_trigger_sql = """
        CREATE TRIGGER update_course_prefixes_updated_at
            AFTER UPDATE ON course_prefixes
        BEGIN
            UPDATE course_prefixes 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END;
        """
        
        cursor.execute(create_trigger_sql)
        print("✅ Created trigger: update_course_prefixes_updated_at")
        
        # Create a view for easy querying
        create_view_sql = """
        CREATE VIEW v_course_prefixes AS
        SELECT 
            prefix_code,
            institution,
            institution_code,
            extracted_at,
            created_at,
            updated_at
        FROM course_prefixes
        ORDER BY prefix_code;
        """
        
        cursor.execute(create_view_sql)
        print("✅ Created view: v_course_prefixes")
        
        # Commit changes
        conn.commit()
        
        # Display table schema
        print("\n📋 Table Schema:")
        cursor.execute("PRAGMA table_info(course_prefixes);")
        columns = cursor.fetchall()
        
        print("   Column Name       | Type        | Constraints")
        print("   " + "-" * 45)
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else ""
            pk = "PRIMARY KEY" if col[5] else ""
            constraints = f"{not_null} {pk}".strip()
            print(f"   {col_name:<17} | {col_type:<11} | {constraints}")
        
        print(f"\n🎉 Database schema created successfully!")
        print(f"📄 Database file: {os.path.abspath(db_path)}")
        print(f"📊 Ready to store course prefix data.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔒 Database connection closed.")

def test_database_connection(db_path="course_catalog.db"):
    """Test that the database was created correctly"""
    
    print(f"\n🔍 Testing database connection...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='course_prefixes';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Table 'course_prefixes' exists and is accessible")
            
            # Test insert/select
            test_prefix = "TEST"
            cursor.execute("""
                INSERT OR IGNORE INTO course_prefixes (prefix_code, extraction_method) 
                VALUES (?, 'test')
            """, (test_prefix,))
            
            cursor.execute("SELECT * FROM course_prefixes WHERE prefix_code = ?", (test_prefix,))
            test_row = cursor.fetchone()
            
            if test_row:
                print("✅ Insert/Select operations working correctly")
                
                # Clean up test data
                cursor.execute("DELETE FROM course_prefixes WHERE prefix_code = ?", (test_prefix,))
                conn.commit()
                print("✅ Test data cleaned up")
            else:
                print("❌ Insert/Select test failed")
                
        else:
            print("❌ Table 'course_prefixes' not found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Create the database schema
    success = create_database_schema()
    
    if success:
        # Test the database
        test_database_connection()
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Run your course prefix extraction script")
        print(f"   2. Run the ingestion script to load JSON data")
        print(f"   3. Query your data with: sqlite3 course_catalog.db")
        
    else:
        print(f"\n💥 Database creation failed. Please check the errors above.")
        
    print(f"\n✨ Done!")