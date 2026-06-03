import sys
import os
import sqlite3
import pandas as pd

# Add apps directory to path
sys.path.append(os.path.join(os.getcwd(), 'apps'))

from utils import db

def verify_db():
    print("Initializing DB...")
    db.init_db()
    
    print("Logging test violations...")
    db.log_violation("Test_Live", 0.99, "path/to/live.jpg", "Worker1", True, "Live")
    db.log_violation("Test_Image", 0.88, "path/to/img.jpg", "Unknown", True, "Image Upload")
    db.log_violation("Test_Video", 0.77, "path/to/vid.jpg", "Unknown", True, "Video Upload")
    
    print("Reading history...")
    df = db.get_history()
    
    print("\nXXX DATA DUMP XXX")
    print(df[['violation_type', 'source', 'timestamp']].head())
    print("XXX DATA DUMP XXX")
    
    if 'source' in df.columns:
        print("\nSUCCESS: 'source' column exists.")
        
        sources = df['source'].unique()
        print(f"Sources found: {sources}")
        
        if "Image Upload" in sources and "Video Upload" in sources:
             print("SUCCESS: Image and Video sources logged correctly.")
        else:
             print("FAILURE: Missing expected sources.")
    else:
        print("\nFAILURE: 'source' column MISSING.")

    print("\nCleaning up test data...")
    # Delete test entries
    conn = sqlite3.connect(db.DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM violations WHERE violation_type LIKE 'Test_%'")
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    print(f"Deleted {deleted_count} test entries.")
    
if __name__ == "__main__":
    verify_db()
