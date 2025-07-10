#include <SoftwareSerial.h>
SoftwareSerial espSerial(2, 3);          // RX = D2, TX = D3  @9600

/* ---------- pins ---------- */
#define SENSOR_L A0
#define SENSOR_M A1
#define SENSOR_R A2

#define LEFT_EN   6
#define RIGHT_EN 11
#define LEFT_IN1 10
#define LEFT_IN2  9
#define RIGHT_IN1 8
#define RIGHT_IN2 7

#define BUZZER    12

/* Ultrasonic */
#define TRIG_PIN 4
#define ECHO_PIN 5
const float  CM_PER_US  = 0.0343;
const unsigned long US_TIMEOUT = 30000UL;
const int OBSTACLE_CM = 30;

/* ---------- state ---------- */
int currentNode = 0;      // assume robot starts at Node 1
int targetNode  = 1;      // updated by ESP commands
int heading     = 1;      // +1 toward higher node numbers
int direction   = 0;      // +1 fwd, ‑1 rev, 0 idle
bool moving     = false;
bool onNode     = false;
int  lastDirLine = 0;

/* ONE preset left turn at Node 4 (index 4) */
bool leftTurnNode[9] = {
  false, false, false, false,  // 0‑3 (0 unused)
  true,  false, false, false, false  // Node 4 only
};

/* ---------- setup ---------- */
void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);

  pinMode(LEFT_IN1,OUTPUT); pinMode(LEFT_IN2,OUTPUT);
  pinMode(RIGHT_IN1,OUTPUT); pinMode(RIGHT_IN2,OUTPUT);
  pinMode(LEFT_EN,OUTPUT);  pinMode(RIGHT_EN,OUTPUT);
  analogWrite(LEFT_EN,255); analogWrite(RIGHT_EN,255);

  pinMode(SENSOR_L,INPUT); pinMode(SENSOR_M,INPUT); pinMode(SENSOR_R,INPUT);
  pinMode(BUZZER,OUTPUT);

  pinMode(TRIG_PIN,OUTPUT); pinMode(ECHO_PIN,INPUT);

  Serial.println(F("🔧 8‑Node LineBot (left turn only at Node 4) ready"));
}

/* ---------- main loop ---------- */
void loop() {

  /* 1. new command: ASCII ‘1’–‘8’ */
  if (espSerial.available()) {
    char c = espSerial.read();
    if (c >= '1' && c <= '8') {
      int newTarget = c - '0';
      if (newTarget != currentNode) {
        int newDir = (newTarget > currentNode) ? 1 : -1;

        if (newDir != heading) {          // need 180° flip
          stopMotors();
          spinLeft180();
          heading = -heading;
        }

        targetNode = newTarget;
        direction  = newDir;
        moving     = true;

        Serial.print(F("🎯 Target Node ")); Serial.println(targetNode);
        beep(2);
      } else {
        beep(1);  // already at node
      }
    }
  }

  if (!moving) return;

  /* 2. ultrasonic pause */
  float d = distanceCM();
  if (d>0 && d<=OBSTACLE_CM) { stopMotors(); return; }

  /* 3. line following & node counting */
  byte pat = readPattern();

  if (pat == 0b111) {              // node
    if (!onNode) {
      onNode = true;
      currentNode += direction;

      /* --- NEW: notify ESP ---- */
      espSerial.println(String("REACHED:") + currentNode);

      Serial.print(F("📍 Node ")); Serial.println(currentNode);

      /* single preset left turn at Node 4 when heading forward */
      if (heading == 1 && currentNode == 4 && leftTurnNode[4]) {
        Serial.println(F("↩ Preset left turn @ Node 4"));
        spinLeft(); delay(500); stopMotors(); delay(200);
      }

      if (currentNode == targetNode) {
        Serial.println(F("✅ Arrived"));
        stopMotors(); beep(3);
        moving = false; direction = 0;
      }
    }
  } else {                         // line follow
    onNode = false;
    switch (pat) {
      case 0b010: forward(); lastDirLine = 0; break;
      case 0b110: case 0b100: forward(); lastDirLine = (heading==1?-1:1); break;
      case 0b011: case 0b001: forward(); lastDirLine = (heading==1?1:-1);  break;
      case 0b101: forward(); lastDirLine = 0; break;
      case 0b000: (lastDirLine==-1)? spinLeft(): spinRight(); break;
      default:    forward(); break;
    }
  }

  delay(30);
}

/* ---------- helpers ---------- */
void forward(){
  if(heading==1){
    digitalWrite(LEFT_IN1,HIGH); digitalWrite(LEFT_IN2,LOW);
    digitalWrite(RIGHT_IN1,HIGH);digitalWrite(RIGHT_IN2,LOW);
  }else{
    digitalWrite(LEFT_IN1,LOW);  digitalWrite(LEFT_IN2,HIGH);
    digitalWrite(RIGHT_IN1,LOW); digitalWrite(RIGHT_IN2,HIGH);
  }
}
void stopMotors(){ digitalWrite(LEFT_IN1,LOW); digitalWrite(LEFT_IN2,LOW);
                   digitalWrite(RIGHT_IN1,LOW);digitalWrite(RIGHT_IN2,LOW); }
void spinLeft(){  digitalWrite(LEFT_IN1,LOW);  digitalWrite(LEFT_IN2,HIGH);
                  digitalWrite(RIGHT_IN1,HIGH);digitalWrite(RIGHT_IN2,LOW); }
void spinRight(){ digitalWrite(LEFT_IN1,HIGH); digitalWrite(LEFT_IN2,LOW);
                  digitalWrite(RIGHT_IN1,LOW); digitalWrite(RIGHT_IN2,HIGH); }
void spinLeft180(){ spinLeft(); delay(650); stopMotors(); delay(200); }

void beep(int n){ while(n--){ digitalWrite(BUZZER,HIGH); delay(100);
                              digitalWrite(BUZZER,LOW);  delay(100);} }

byte readPattern(){
  return (digitalRead(SENSOR_L)<<2) |
         (digitalRead(SENSOR_M)<<1) |
          digitalRead(SENSOR_R);
}
float distanceCM(){
  digitalWrite(TRIG_PIN,LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN,HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN,LOW);
  unsigned long us=pulseIn(ECHO_PIN,HIGH,US_TIMEOUT);
  return us? (us*CM_PER_US)/2.0 : -1;
}