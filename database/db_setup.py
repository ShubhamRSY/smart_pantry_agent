import sqlite3
from datetime import datetime

# We will use a local file for the database (Free & Simple)
DB_NAME = "smart_pantry.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. TABLE: USER PROFILE
    # Stores your taste buds (Hot/Mild) and your Region (American/Asian/etc.)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,             -- e.g., 'North America', 'India'
            spice_tolerance TEXT,    -- e.g., 'Mild', 'Medium', 'Hot'
            dietary_restrictions TEXT -- e.g., 'Vegetarian', 'None'
        )
    ''')

    # 2. TABLE: PANTRY
    # Stores your groceries with the "Fuzzy Logic" we discussed
    c.execute('''
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,           -- e.g., 'Dairy', 'Vegetable'
            quantity_level TEXT,     -- 'High', 'Medium', 'Low'
            status TEXT,             -- 'Unopened', 'Open'
            last_updated DATETIME
        )
    ''')

    # Create a default user if one doesn't exist
    c.execute("SELECT count(*) FROM user_profile")
    if c.fetchone()[0] == 0:
        print("Creating default user profile...")
        c.execute('''
            INSERT INTO user_profile (name, region, spice_tolerance, dietary_restrictions)
            VALUES (?, ?, ?, ?)
        ''', ("User", "North America", "Medium", "None"))
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully.")

if __name__ == "__main__":
    init_db()