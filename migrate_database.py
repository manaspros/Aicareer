#!/usr/bin/env python3
"""
Database migration script to add questionnaire-related columns to existing database
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add questionnaire columns to existing users table"""
    
    # Database path
    db_path = Path("career_advisor_agents/career_advisor.db")
    
    if not db_path.exists():
        print("Database file not found. No migration needed.")
        return
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if questionnaire_completed column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add missing columns
        columns_to_add = [
            ("questionnaire_completed", "BOOLEAN DEFAULT 0"),
            ("questionnaire_responses", "TEXT"),
            ("personality_insights", "TEXT"),
            ("interest_insights", "TEXT"),
            ("career_goals", "TEXT"),
            ("values", "TEXT"), 
            ("preferred_work_environment", "TEXT")
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                try:
                    sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    print(f"Adding column: {sql}")
                    cursor.execute(sql)
                    print(f"[SUCCESS] Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"[ERROR] Error adding column {column_name}: {e}")
            else:
                print(f"[INFO] Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        print("\n[SUCCESS] Database migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"New columns: {new_columns}")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()