# WAREHOUSE-MANAGEMENT
Using RFID and AGV robot
# 📦 RFID-Based Rack Delivery System with Line-Following AGV 🤖

This project is a smart warehouse automation system that uses **RFID** and a **line-following AGV robot** to transport items to specified rack locations. The user via RFID scanner, selects a destination rack using a GUI, and the robot autonomously navigates along a path to the selected node.

---

## 🚀 Features

- 🔐 **RFID User Authentication**  
  Each user must scan their RFID tag to begin the delivery process.

- 🖥️ **Python GUI** (Tkinter)  
  Lets the user choose a destination rack (RACK 1 to RACK 8).

- 📡 **Wireless Communication**  
  The GUI sends the destination wirelessly to the Arduino via ESP8266.

- 🧭 **Autonomous Line-Following Robot**  
  Uses IR sensors to follow black lines on the warehouse floor and count nodes.

- 🛑 **Node-Based Rack Detection**  
  Robot stops at the node number corresponding to the rack selected by the user.


## 🛠️ Technologies Used

- **Arduino Uno** – Robot microcontroller  
- **ESP8266 WiFi Module** – Wireless data reception from GUI  
- **RFID Reader (RC522)** – User authentication  
- **IR Sensors and ultrasonic sensors** – Line following,node detection and obstacle detection. 
- **Motor Driver (L298N)** – Controls robot wheels  
- **Python (Tkinter)** – GUI for rack management(view logs,scan,find,validation).
- **Serial Communication / HTTP** – Between ESP8266 and Arduino



