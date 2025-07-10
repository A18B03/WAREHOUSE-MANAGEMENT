from db_handler import init_db, log_movement, view_all
from serial_reader import read_rfid
from rack_validator import validate_rack_placement
import requests

# Node mapping (rack IDs like "A1", "B2" to RACK 1–8)
rack_to_node = {
    "RACK 1": 1, "RACK 2": 2, "RACK 3": 3, "RACK 4": 4,
    "RACK 5": 5, "RACK 6": 6, "RACK 7": 7, "RACK 8": 8
}

# First letter (A–D) to RACK name
letter_to_rack = {"A": "RACK 1", "B": "RACK 2", "C": "RACK 3", "D": "RACK 4"}

ESP_IP = "http://"  # Update if needed

def send_node_to_esp(rack_id):
    try:
        rack_letter = rack_id[0].upper()
        rack_name = letter_to_rack.get(rack_letter)
        node = rack_to_node.get(rack_name)

        if node:
            response = requests.get(f"{ESP_IP}/receive", params={"node": node})
            if response.status_code == 200:
                print(f"✅ Sent to ESP: Node {node}")
            else:
                print(f"❌ ESP Error: {response.status_code}")
        else:
            print("⚠️ Invalid rack for ESP.")
    except Exception as e:
        print(f"❌ Failed to send to ESP: {e}")


SIMULATE = False

init_db()

while True:
    print("\n📦 RFID Warehouse System")
    print("1. 📥 Inward Product")
    print("2. 🧾 Rack Placement")
    print("3. 📤 Issue Product")
    print("4. 📊 View All Logs")
    print("5. ❌ Exit")

    choice = input("Select option: ")

    if choice == '1':
    tag = read_rfid(simulate=SIMULATE)
    pid = input("Enter Product ID: ")
    rack = input("Assign Rack ID: ").strip().upper()
    log_movement(tag, pid, "Inward", rack)
    print("✅ Product logged as Inward.")

# Send destination node to ESP
    send_node_to_esp(rack)


    elif choice == '2':
        print("📦 Scan tag at rack location...")
        tag = read_rfid(simulate=SIMULATE)
        pid = input("Enter Product ID: ").strip().lower()
        scanned_rack = input("Scanned Rack ID: ").strip().upper()

        validate_rack_placement(tag, pid, scanned_rack, log_movement)

    elif choice == '3':
        tag = read_rfid(simulate=SIMULATE)
        pid = input("Enter Product ID: ")
        rack = input("Last known Rack ID: ")
        log_movement(tag, pid, "Issued", rack)
        print("✅ Product issue logged.")

    elif choice == '4':
        view_all()

    elif choice == '5':
        print("👋 Exiting system.")
        break

    else:
        print("❌ Invalid option.")
