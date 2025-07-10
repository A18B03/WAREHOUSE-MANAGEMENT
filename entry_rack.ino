#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("📡 RFID Ready. Waiting for tag...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String tagContent = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    tagContent += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    tagContent += String(rfid.uid.uidByte[i], HEX);
  }
  tagContent.toUpperCase();

  Serial.println("DATA:" + tagContent);  // Sent to Python serial_reader

  delay(1000);
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
