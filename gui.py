import tkinter as tk
from tkinter import ttk, simpledialog
from db_handler import log_movement, get_assigned_rack, init_db
from serial_reader import read_rfid
import sqlite3
import requests
import threading


# Mapping racks to node numbers for ESP
rack_to_node = {
    "RACK 1": 1, "RACK 2": 2, "RACK 3": 3, "RACK 4": 4,
    "RACK 5": 5, "RACK 6": 6, "RACK 7": 7, "RACK 8": 8
}

import requests

ESP_IP = "http://10.204.117.20"  # Replace with actual ESP IP

def poll_robot_status():
    try:
        response = requests.get("http://10.204.117.20/status", timeout=2)
        if response.status_code == 200:
            robot_status.set("🤖 Robot: " + response.text)
    except:
        robot_status.set("❌ Robot status: unreachable")
    finally:
        root.after(2000, poll_robot_status)  # Poll every 2 seconds
        


def send_node_to_esp(rack_id):
    try:
        # Convert rack A1–D3 to node number (1–8)
        letter_to_rack = {"A": "RACK 1", "B": "RACK 2", "C": "RACK 3", "D": "RACK 4"}
        rack_to_node = {
            "RACK 1": 1, "RACK 2": 2, "RACK 3": 3, "RACK 4": 4,
            "RACK 5": 5, "RACK 6": 6, "RACK 7": 7, "RACK 8": 8
        }

        rack_letter = rack_id[0].upper()  # A, B, C, D
        mapped_rack = letter_to_rack.get(rack_letter)
        node = rack_to_node.get(mapped_rack)

        if node:
            response = requests.get(f"{ESP_IP}/receive", params={"node": node}, timeout=3)
            if response.status_code == 200:
                print(f"✅ Sent node {node} to ESP")
            else:
                print(f"❌ ESP responded with: {response.status_code}")
        else:
            print("❌ Invalid rack mapping.")
    except Exception as e:
        print(f"❌ Error sending to ESP: {e}")

# Initialize the database table
init_db()

SIMULATE = False
flash_active = False

# Rack number to letter mapping (Rack 1 = A, Rack 2 = B, etc.)
rack_number_to_letter = {
    "1": "A", "2": "B", "3": "C", "4": "D"
}

# GUI Setup
root = tk.Tk()
root.title("📦 RFID Warehouse System")
root.geometry("1400x900")
root.state('zoomed')

default_font = ("Arial", 18)
root.option_add("*Font", default_font)

output_text = tk.StringVar()

rack_labels = {}
levels = {
    "Upper": ["A3", "B3", "C3", "D3"],
    "Middle": ["A2", "B2", "C2", "D2"],
    "Lower": ["A1", "B1", "C1", "D1"]
}

rack_frame = tk.Frame(root, pady=20)
rack_frame.pack()

for i, (level, racks) in enumerate(levels.items()):
    tk.Label(rack_frame, text=level, font=("Arial", 22, "bold"), width=8, anchor="e").grid(row=i, column=0, padx=10, pady=10)
    for j, rack in enumerate(racks):
        lbl = tk.Label(rack_frame, text=rack, width=12, height=2, relief="solid", bg="white")
        lbl.grid(row=i, column=j+1, padx=10, pady=10)
        rack_labels[rack] = lbl

# Flash red background on error
def flash_red(count=6):
    global flash_active
    if count <= 0:
        root.configure(bg="SystemButtonFace")
        flash_active = False
        return
    root.configure(bg="red" if count % 2 == 0 else "SystemButtonFace")
    root.after(300, flash_red, count - 1)

# Inward/Issue product
def inward_product():
    tag = read_rfid(port='COM6', simulate=SIMULATE)
    pid = entry_pid.get().strip()
    rack = entry_rack.get().strip().upper()

    if not tag or not pid or not rack:
        output_text.set("⚠️ All fields must be filled.")
        return

    log_movement(tag, pid, "Inward", rack)
    output_text.set(f"✅ {pid} assigned to {rack}")

    if rack in rack_labels:
        rack_labels[rack].configure(bg="lightblue")

    send_node_to_esp(rack)

def issue_product():
    tag = read_rfid(port='COM6', simulate=SIMULATE)
    pid = entry_pid.get().strip()
    rack = entry_rack.get().strip().upper()
    if not tag or not pid or not rack:
        output_text.set("⚠️ All fields must be filled.")
        return
    log_movement(tag, pid, "Issued", rack)
    output_text.set(f"📤 {pid} issued from {rack}")

def show_logs():
    win = tk.Toplevel()
    win.title("📊 Logs")
    win.geometry("800x500")

    cols = ("RFID", "Product", "Movement", "Rack", "Timestamp")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT RFID, Product_ID, Movement_type, Rack_ID, timestamp FROM warehouse_log ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

def find_product():
    pid = entry_pid.get().strip()
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Rack_ID, Movement_type FROM warehouse_log
        WHERE Product_ID = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (pid,))
    result = cursor.fetchone()
    conn.close()

    for lbl in rack_labels.values():
        lbl.configure(bg="white")

    if result:
        rack, movement = result
        if rack in rack_labels:
            rack_labels[rack].configure(bg="yellow")
        output_text.set(f"📦 {pid} is currently in rack {rack} ({movement})")
    else:
        output_text.set(f"⚠️ No record found for product '{pid}'")

def scan_and_find():
    tag = read_rfid(port='COM6', simulate=SIMULATE)
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Product_ID, Rack_ID, Movement_type FROM warehouse_log
        WHERE RFID = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (tag,))
    result = cursor.fetchone()
    conn.close()

    for lbl in rack_labels.values():
        lbl.configure(bg="white")

    if result:
        pid, rack, movement = result
        entry_pid.delete(0, tk.END)
        entry_pid.insert(0, pid)
        if rack in rack_labels:
            rack_labels[rack].configure(bg="yellow")
        output_text.set(f"🔍 {pid} (RFID {tag}) is in rack {rack} ({movement})")
    else:
        output_text.set(f"⚠️ No record found for RFID {tag}")

def start_validate_rack():
    thread = threading.Thread(target=do_validate_rack)
    thread.daemon = True
    thread.start()

def do_validate_rack():
    import serial

    output_text.set("📡 Waiting for rack tag scan...")

    try:
        ser1 = serial.Serial('COM3', 9600, timeout=1)
        ser2 = serial.Serial('COM8', 9600, timeout=1)
    except Exception as e:
        output_text.set(f"⚠️ Serial error: {e}")
        return

    tag = None
    base = ""
    source_line = ""

    while True:
        if ser1.in_waiting:
            source_line = ser1.readline().decode(errors='ignore').strip()
        elif ser2.in_waiting:
            source_line = ser2.readline().decode(errors='ignore').strip()
        else:
            continue

        if source_line.startswith("RACK1:"):
            tag = source_line.replace("RACK1:", "")
            base = "A"
            break
        elif source_line.startswith("RACK2:"):
            tag = source_line.replace("RACK2:", "")
            base = "B"
            break
        elif source_line.startswith("RACK3:"):
            tag = source_line.replace("RACK3:", "")
            break

    ser1.close()
    ser2.close()

    if base:
        root.after(0, lambda: continue_validation(tag, base))
    else:
        def ask_rack_number():
            rack_num = simpledialog.askstring("Rack Detected", "Enter rack number (1=A, 2=B, 3=C, 4=D):")
            if rack_num not in rack_number_to_letter:
                output_text.set("⚠️ Invalid rack number.")
                return
            base_letter = rack_number_to_letter[rack_num]
            root.after(0, lambda: continue_validation(tag, base_letter))
        root.after(0, ask_rack_number)

def continue_validation(tag, base):
    level_map = {"1": "1", "2": "2", "3": "3"}
    level = simpledialog.askstring("Shelf Level", "Enter shelf level (1=Lower, 2=Middle, 3=Upper):")

    if level not in level_map:
        output_text.set("⚠️ Invalid level. Must be 1, 2, or 3.")
        return

    scanned_rack = f"{base}{level_map[level]}"
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Product_ID FROM warehouse_log
        WHERE RFID = ? AND Movement_type = 'Inward'
        ORDER BY timestamp DESC LIMIT 1
    """, (tag,))
    result = cursor.fetchone()
    conn.close()

    for lbl in rack_labels.values():
        lbl.configure(bg="white")

    if not result:
        output_text.set("⚠️ No inward record found for this tag.")
        return

    pid = result[0]
    expected_rack = get_assigned_rack(tag, pid)

    if scanned_rack == expected_rack:
        output_text.set(f"✅ {pid} placed correctly in {scanned_rack}")
        rack_labels[expected_rack].configure(bg="lightgreen")
    else:
        output_text.set(f"❌ Misplaced! {pid} expected in {expected_rack}, found in {scanned_rack}")
        if expected_rack in rack_labels:
            rack_labels[expected_rack].configure(bg="green")
        if scanned_rack in rack_labels:
            rack_labels[scanned_rack].configure(bg="red")
        flash_red()

form = tk.Frame(root)
form.pack(pady=20)
tk.Label(form, text="📌 Product ID:", anchor="e", width=15).grid(row=0, column=0, padx=10, pady=10)
entry_pid = tk.Entry(form, width=25, font=("Arial", 18))
entry_pid.grid(row=0, column=1, padx=10, pady=10)

tk.Label(form, text="📦 Rack ID:", anchor="e", width=15).grid(row=1, column=0, padx=10, pady=10)
entry_rack = tk.Entry(form, width=25, font=("Arial", 18))
entry_rack.grid(row=1, column=1, padx=10, pady=10)

robot_status = tk.StringVar()
robot_status.set("🤖 Robot: Waiting...")

robot_label = tk.Label(root, textvariable=robot_status, fg="green", font=("Arial", 20))
robot_label.pack(pady=10)


# Button section
btns = tk.Frame(root)
btns.pack(pady=30)

tk.Button(btns, text="⬆️ Inward Product", command=lambda: threading.Thread(target=inward_product, daemon=True).start(), width=16, height=2).grid(row=0, column=0, padx=15, pady=10)
tk.Button(btns, text="✅ Validate Rack", command=start_validate_rack, width=14, height=2).grid(row=0, column=1, padx=15, pady=10)
tk.Button(btns, text="📤 Issue Product", command=issue_product, width=14, height=2).grid(row=0, column=2, padx=15, pady=10)
tk.Button(btns, text="🔍 Find Product", command=find_product, width=14, height=2).grid(row=0, column=3, padx=15, pady=10)
tk.Button(btns, text="📊 View Logs", command=show_logs, width=14, height=2).grid(row=0, column=4, padx=15, pady=10)
tk.Button(btns, text="📡 Scan to Find", command=scan_and_find, width=14, height=2).grid(row=0, column=5, padx=15, pady=10)

# Output
# Output label
output_label = tk.Label(
    root, textvariable=output_text,
    fg="blue", font=("Arial", 24, "bold"),
    anchor="center", justify="center"
)
output_label.pack(pady=30)

# Start polling robot status every 2 seconds
poll_robot_status()

# Launch the GUI
root.mainloop()
