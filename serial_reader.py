import serial

def read_rfid(port='COM6', simulate=False):
    if simulate:
        return input("🔁 Simulated RFID Tag: ").strip()

    try:
        with serial.Serial(port, 9600, timeout=5) as ser:
            print("📡 Waiting for tag on", port)
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("DATA:"):
                    data = line[5:].strip()
                    if len(data) >= 7:
                        print(f"✅ Read tag: {data}")
                        return data
    except Exception as e:
        print(f"⚠️ Serial error on {port}: {e}")
        return input("🔁 Enter Tag ID manually: ").strip()
