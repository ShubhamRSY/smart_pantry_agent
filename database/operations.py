import sqlite3
import re
from datetime import datetime
import os
import hashlib

# --- AUTH SYSTEM (Unchanged) ---
def init_auth_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)")
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    init_auth_db()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    init_auth_db()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == hash_password(password)

# --- PANTRY SYSTEM (Updated for Decimals) ---
def get_db_path(username):
    folder = "user_data"
    os.makedirs(folder, exist_ok=True)
    return f"{folder}/{username.lower().strip()}.db"

def init_pantry_db(username):
    db_path = get_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Changed quantity to REAL to support 0.5 bags
    c.execute("""
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            quantity REAL DEFAULT 1.0, 
            unit TEXT,
            last_updated TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    return db_path

def get_db_connection(username):
    return sqlite3.connect(get_db_path(username), check_same_thread=False)

def add_items_to_pantry(username, items_list):
    conn = get_db_connection(username)
    c = conn.cursor()
    
    for item in items_list:
        name = item.get('clean_name', 'Unknown Item')
        category = item.get('category', 'Pantry')
        try:
            qty = float(re.search(r'\d+(\.\d+)?', str(item.get('quantity', 1))).group())
        except:
            qty = 1.0
            
        c.execute("SELECT id, quantity FROM pantry WHERE item_name = ?", (name,))
        existing = c.fetchone()
        
        if existing:
            new_total = existing[1] + qty
            c.execute("UPDATE pantry SET quantity = ?, last_updated = ? WHERE id = ?", 
                      (new_total, datetime.now(), existing[0]))
        else:
            c.execute("INSERT INTO pantry (item_name, category, quantity, unit, last_updated) VALUES (?, ?, ?, ?, ?)", 
                      (name, category, qty, item.get('unit',''), datetime.now()))
            
    conn.commit()
    conn.close()

def get_current_inventory(username):
    conn = get_db_connection(username)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Show anything that has more than 0.1 left
    c.execute("SELECT * FROM pantry WHERE quantity > 0.05 ORDER BY category, item_name")
    return [dict(row) for row in c.fetchall()]

def get_grocery_list(username):
    conn = get_db_connection(username)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Show anything close to 0
    c.execute("SELECT * FROM pantry WHERE quantity <= 0.05 ORDER BY category")
    return [dict(row) for row in c.fetchall()]

def update_item_count(username, item_id, delta):
    """Delta can now be a float, e.g., -0.5"""
    conn = get_db_connection(username)
    c = conn.cursor()
    c.execute("SELECT quantity FROM pantry WHERE id = ?", (item_id,))
    row = c.fetchone()
    if row:
        new_qty = max(0.0, row[0] + delta)
        c.execute("UPDATE pantry SET quantity = ? WHERE id = ?", (new_qty, item_id))
    conn.commit()
    conn.close()

def deduct_ingredients(username, ingredient_names, people_count=2):
    """Smart deduction based on category"""
    conn = get_db_connection(username)
    c = conn.cursor()
    logs = []
    
    # Logic: If cooking for 2 people, use 0.25 (1/4) of a bag. If 4 people, use 0.5.
    usage_factor = 0.125 * people_count 
    
    for ing in ingredient_names:
        c.execute("SELECT id, item_name, quantity, category FROM pantry WHERE item_name LIKE ? AND quantity > 0", (f"%{ing}%",))
        match = c.fetchone()
        
        if match:
            cat = match[3]
            current_qty = match[2]
            
            # SMART DEDUCTION RULES
            if cat in ['Pantry', 'Spices', 'Condiments']: 
                # Rice/Oil: Deduct fraction based on people
                deduction = usage_factor 
            elif cat in ['Produce'] and 'spinach' in match[1].lower():
                # Spinach shrinks! Deduct fraction.
                deduction = usage_factor
            elif cat in ['Meat', 'Dairy']:
                # Meat usually gets used up fully per meal if it's a pack
                deduction = 1.0
            else:
                deduction = 1.0 # Default

            new_qty = max(0.0, current_qty - deduction)
            c.execute("UPDATE pantry SET quantity = ? WHERE id = ?", (new_qty, match[0]))
            logs.append(f"Used {deduction} of {match[1]}")
            
    conn.commit()
    conn.close()
    return logs