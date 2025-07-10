import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warehouse_log (
        RFID TEXT,
        Product_ID TEXT,
        Movement_type TEXT,
        Rack_ID TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def log_movement(rfid, product_id, movement_type, rack_id):
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT * FROM warehouse_log WHERE RFID = ? AND Product_ID = ?
    """, (rfid, product_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE warehouse_log
            SET Movement_type = ?, Rack_ID = ?, timestamp = ?
            WHERE RFID = ? AND Product_ID = ?
        """, (movement_type, rack_id, timestamp, rfid, product_id))
    else:
        cursor.execute("""
            INSERT INTO warehouse_log (RFID, Product_ID, Movement_type, Rack_ID, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (rfid, product_id, movement_type, rack_id, timestamp))

    conn.commit()
    conn.close()

def view_all():
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warehouse_log")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

def get_assigned_rack(rfid, product_id):
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Rack_ID FROM warehouse_log 
        WHERE RFID = ? AND Product_ID = ? AND Movement_type = 'Inward'
        ORDER BY timestamp DESC LIMIT 1
    """, (rfid, product_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
