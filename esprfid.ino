#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <SoftwareSerial.h>

// RX = D5 (receives from Arduino TX), TX = D6 (sends to Arduino RX)
SoftwareSerial robotSerial(D5, D6);  

const char* ssid = "TestESP";       // 🔁 Change if needed
const char* password = "12345678";  // 🔁 Change if needed

ESP8266WebServer server(80);
String latestStatus = "🔄 Waiting for robot...";

// 📥 Handle GUI sending node number
void handleReceive() {
  if (server.hasArg("node")) {
    String node = server.arg("node");
    robotSerial.println(node);  // Forward to Robot Arduino
    server.send(200, "text/plain", "✅ Node received: " + node);
    Serial.println("→ Sent to Arduino: " + node);
  } else {
    server.send(400, "text/plain", "❌ Missing 'node' parameter");
  }
}

// 📤 Read status from Robot Arduino
void readRobotStatus() {
  if (robotSerial.available()) {
    latestStatus = robotSerial.readStringUntil('\n');
    latestStatus.trim();
    Serial.println("🤖 Robot says: " + latestStatus);
  }
}

// 🖥️ Serve latest status to GUI
void handleStatus() {
  server.send(200, "text/plain", latestStatus);
}

void setup() {
  Serial.begin(115200);
  robotSerial.begin(9600);

  Serial.println("\n📡 Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ Connected to WiFi");
  Serial.print("📶 IP Address: ");
  Serial.println(WiFi.localIP());

  // Web endpoints
  server.on("/receive", handleReceive);
  server.on("/status", handleStatus);
  server.begin();
  Serial.println("✅ Server ready.");
}

void loop() {
  server.handleClient();    // Handle HTTP requests
  readRobotStatus();        // Read serial from Robot Arduino
}
