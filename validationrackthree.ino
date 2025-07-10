#include <SPI.h>
#include <MFRC522.h>

// RC522 1 → Rack A
#define SS_1 10
#define RST_1 8

// RC522 2 → Rack B
#define SS_2 9
#define RST_2 7

// RC522 3 → Rack C + D
#define SS_3 6
#define RST_3 5

MFRC522 reader1(SS_1, RST_1);
MFRC522 reader2(SS_2, RST_2);
MFRC522 reader3(SS_3, RST_3);

void setup() {
  Serial.begin(9600);
  SPI.begin();

  reader1.PCD_Init();
  reader2.PCD_Init();
  reader3.PCD_Init();

  Serial.println("📡 3 RC522 Readers Ready");
}

void loop() {
  checkReader(reader1, "RACK1:");
  checkReader(reader2, "RACK2:");
  checkReader(reader3, "RACK3:");
}

void checkReader(MFRC522 &reader, String label) {
  reader.PCD_Init();
  if (reader.PICC_IsNewCardPresent() && reader.PICC_ReadCardSerial()) {
    Serial.print(label);
    for (byte i = 0; i < reader.uid.size; i++) {
      if (reader.uid.uidByte[i] < 0x10) Serial.print("0");
      Serial.print(reader.uid.uidByte[i], HEX);
    }
    Serial.println();
    reader.PICC_HaltA();
    reader.PCD_StopCrypto1();
    delay(1500);
  }
}
