import sqlite3
import json
import re
from datetime import datetime

DB_NAME = "smart_pantry.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Ensures the table exists with the correct columns."""
    conn = get_db_connection()
    c = conn.cursor()
    # We add a specific 'quantity' integer column now
    c.execute("""
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER DEFAULT 1,
            unit TEXT,
            last_updated TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def clean_quantity(qty_str):
    """
    Extracts a number from a string. 
    e.g. "3 bottles" -> 3
    e.g. "1" -> 1
    """
    try:
        # Find the first number in the string
        match = re.search(r'\d+', str(qty_str))
        if match:
            return int(match.group())
    except:
        pass
    return 1 # Default to 1 if we can't read it

def add_items_to_pantry(items_list):
    init_db() # Make sure table exists
    conn = get_db_connection()
    c = conn.cursor()
    
    print(f"\n💾 Saving items to Database...")
    
    for item in items_list:
        name = item.get('clean_name', 'Unknown')
        category = item.get('category', 'Other')
        raw_qty = item.get('quantity', 1)
        
        # Convert "3 gallons" to just the number 3
        qty_num = clean_quantity(raw_qty)
        
        # 1. Check if item exists (Clustering Logic)
        c.execute("SELECT id, quantity FROM pantry WHERE item_name = ?", (name,))
        existing = c.fetchone()
        
        if existing:
            # UPDATE: Add new quantity to existing quantity
            new_total = existing['quantity'] + qty_num
            print(f"   🔄 Found {name}. Updating count: {existing['quantity']} -> {new_total}")
            c.execute("UPDATE pantry SET quantity = ?, last_updated = ? WHERE id = ?", 
                      (new_total, datetime.now(), existing['id']))
        else:
            # INSERT: Create new row
            print(f"   ✨ Added new: {name} (x{qty_num})")
            c.execute("""
                INSERT INTO pantry (item_name, category, quantity, last_updated)
                VALUES (?, ?, ?, ?)
            """, (name, category, qty_num, datetime.now()))
            
    conn.commit()
    conn.close()

def update_item_count(item_id, delta):
    """
    Used by the UI buttons to +1 or -1 an item.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get current qty
    c.execute("SELECT quantity FROM pantry WHERE id = ?", (item_id,))
    row = c.fetchone()
    
    if row:
        new_qty = row['quantity'] + delta
        if new_qty <= 0:
            # Delete if 0
            c.execute("DELETE FROM pantry WHERE id = ?", (item_id,))
        else:
            c.execute("UPDATE pantry SET quantity = ? WHERE id = ?", (new_qty, item_id))
            
    conn.commit()
    conn.close()

def get_current_inventory():
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM pantry ORDER BY category, item_name")
    items = c.fetchall()
    conn.close()
    return [dict(row) for row in items]