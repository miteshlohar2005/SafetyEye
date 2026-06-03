import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "safety_logs.db")

def init_db():
    """Initialize the database with the violations table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # Create violations image directory and subdirectories
    violations_path = os.path.join(os.path.dirname(DB_PATH), "violations")
    os.makedirs(violations_path, exist_ok=True)
    os.makedirs(os.path.join(violations_path, "images"), exist_ok=True)
    os.makedirs(os.path.join(violations_path, "videos"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            violation_type TEXT,
            confidence REAL,
            image_path TEXT,
            person_name TEXT,
            zone_active BOOLEAN,
            source TEXT DEFAULT 'Live'
        )
    ''')
    
    # Migration: Add source column if it doesn't exist
    try:
        c.execute("ALTER TABLE violations ADD COLUMN source TEXT DEFAULT 'Live'")
    except sqlite3.OperationalError:
        # Column likely already exists
        pass
        
    conn.commit()
    conn.close()

def log_violation(violation_type, confidence, image_path, person_name="Unknown", zone_active=True, source="Live"):
    """Log a violation to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO violations (timestamp, violation_type, confidence, image_path, person_name, zone_active, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), violation_type, confidence, image_path, person_name, zone_active, source))
    conn.commit()
    conn.close()

def get_history():
    """Retrieve all violations as a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM violations ORDER BY timestamp DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df
