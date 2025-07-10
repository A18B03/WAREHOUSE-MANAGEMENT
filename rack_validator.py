import sqlite3

def get_assigned_rack(rfid, product_id):
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Rack_ID FROM warehouse_log 
        WHERE LOWER(RFID) = LOWER(?) AND LOWER(Product_ID) = LOWER(?) AND Movement_type = 'Inward'
        ORDER BY timestamp DESC LIMIT 1
    """, (rfid, product_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def validate_rack_placement(rfid, product_id, scanned_rack_id, _):
    expected_rack = get_assigned_rack(rfid, product_id)
    if expected_rack is None:
        print("⚠️ No inward record found for this product and tag.")
        return

    # Normalize both sides before comparison
    if scanned_rack_id.strip().upper() == expected_rack.strip().upper():
        print(f"✅ Rack placement correct! → {scanned_rack_id}")
    else:
        print(f"❌ Misplaced! Expected: {expected_rack}, Found: {scanned_rack_id}")

