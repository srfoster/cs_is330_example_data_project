"""
JSON Data Ingestion Script
Loads course prefix data from JSON file into SQLite database
"""

import sqlite3
import json
import os
from datetime import datetime

def load_json_data(json_file):
    """Load and validate JSON data"""
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"✅ JSON file loaded: {json_file}")
        print(f"📊 Found {data.get('total_prefixes', 0)} course prefixes")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return None

def ingest_course_prefixes(json_file="olympic_course_prefixes_final.json", db_path="course_catalog.db"):
    """
    Ingest course prefix data from JSON into database
    
    Args:
        json_file (str): Path to the JSON file with course prefix data
        db_path (str): Path to the SQLite database
    """
    
    print("📥 Course Prefix Data Ingestion")
    print("=" * 40)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print(f"   Please run 'python init_course_db.py' first to create the database.")
        return False
    
    # Load JSON data
    data = load_json_data(json_file)
    if not data:
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔗 Connected to database: {db_path}")
        
        # Extract metadata from JSON
        extracted_at = data.get('extracted_at')
        source_url = data.get('source_url')
        institution = data.get('institution', 'Olympic College')
        institution_code = data.get('institution_code', 'WA030')
        extraction_method = data.get('extraction_method', 'Unknown')
        course_prefixes = data.get('course_prefixes', [])
        
        if not course_prefixes:
            print("❌ No course prefixes found in JSON data")
            return False
        
        print(f"📋 Metadata:")
        print(f"   Institution: {institution}")
        print(f"   Extracted: {extracted_at}")
        print(f"   Method: {extraction_method}")
        print(f"   Prefixes: {len(course_prefixes)}")
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM course_prefixes")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing records in database")
            response = input("   Replace all data? (y/N): ")
            if response.lower() == 'y':
                cursor.execute("DELETE FROM course_prefixes")
                print("🗑️  Cleared existing data")
            else:
                print("   Appending new data (duplicates will be ignored)")
        
        # Insert course prefixes
        insert_sql = """
        INSERT OR IGNORE INTO course_prefixes 
        (prefix_code, institution, institution_code, extracted_at, source_url, extraction_method)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        inserted_count = 0
        skipped_count = 0
        
        for prefix in course_prefixes:
            try:
                cursor.execute(insert_sql, (
                    prefix,
                    institution,
                    institution_code,
                    extracted_at,
                    source_url,
                    extraction_method
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                    print(f"   ✅ Inserted: {prefix}")
                else:
                    skipped_count += 1
                    print(f"   ⏭️  Skipped (duplicate): {prefix}")
                    
            except sqlite3.Error as e:
                print(f"   ❌ Error inserting {prefix}: {e}")
                skipped_count += 1
        
        # Commit changes
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM course_prefixes")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 Ingestion Summary:")
        print(f"   Total processed: {len(course_prefixes)}")
        print(f"   Successfully inserted: {inserted_count}")
        print(f"   Skipped/Errors: {skipped_count}")
        print(f"   Total in database: {total_count}")
        
        # Show sample of inserted data
        print(f"\n🔍 Sample Data:")
        cursor.execute("""
            SELECT prefix_code, institution, created_at 
            FROM course_prefixes 
            ORDER BY prefix_code 
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print("   Prefix | Institution    | Created")
        print("   " + "-" * 35)
        for sample in samples:
            prefix, inst, created = sample
            created_short = created[:19] if created else "N/A"  # Just date/time part
            print(f"   {prefix:<6} | {inst[:14]:<14} | {created_short}")
        
        if len(samples) < total_count:
            print(f"   ... and {total_count - len(samples)} more")
        
        print(f"\n🎉 Data ingestion completed successfully!")
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

def query_sample_data(db_path="course_catalog.db"):
    """Query and display sample data from the database"""
    
    print(f"\n🔍 Sample Database Queries:")
    print("=" * 30)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count total prefixes
        cursor.execute("SELECT COUNT(*) FROM course_prefixes")
        count = cursor.fetchone()[0]
        print(f"📊 Total course prefixes: {count}")
        
        # Show prefixes by letter
        cursor.execute("""
            SELECT SUBSTR(prefix_code, 1, 1) as first_letter, COUNT(*) as count
            FROM course_prefixes 
            GROUP BY SUBSTR(prefix_code, 1, 1) 
            ORDER BY first_letter
        """)
        
        letter_counts = cursor.fetchall()
        print(f"\n🔤 Prefixes by first letter:")
        for letter, cnt in letter_counts:
            print(f"   {letter}: {cnt} prefixes")
        
        # Show all prefixes
        cursor.execute("SELECT prefix_code FROM course_prefixes ORDER BY prefix_code")
        all_prefixes = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📚 All Course Prefixes:")
        # Print in columns
        for i in range(0, len(all_prefixes), 6):
            row = all_prefixes[i:i+6]
            print(f"   {' | '.join(f'{p:<6}' for p in row)}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Default file paths
    json_file = "olympic_course_prefixes_final.json"
    db_file = "course_catalog.db"
    
    # Check for JSON file
    if not os.path.exists(json_file):
        print(f"📁 Looking for JSON files...")
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'prefix' in f.lower()]
        
        if json_files:
            print(f"   Found: {json_files}")
            json_file = json_files[0]  # Use first match
            print(f"   Using: {json_file}")
        else:
            print(f"❌ No course prefix JSON files found.")
            print(f"   Please run the extraction script first to generate the JSON file.")
            exit(1)
    
    # Run ingestion
    success = ingest_course_prefixes(json_file, db_file)
    
    if success:
        # Show sample queries
        query_sample_data(db_file)
        
        print(f"\n🚀 Next Steps:")
        print(f"   • Query database: sqlite3 {db_file}")
        print(f"   • View all data: SELECT * FROM course_prefixes;")
        print(f"   • Use the view: SELECT * FROM v_course_prefixes;")
        
    print(f"\n✨ Done!")