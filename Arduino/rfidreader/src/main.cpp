#include <MFRC522.h>
#include <SPI.h>
#include <SHA256.h>
#include <SerialCommunicator.h>
#include <Leds.h>
#include <Api.h>
#include <Protocol.h>
#include <Controller.h>

// Encrypt
SHA256 sha256;

#ifndef HANDSHAKE_KEY
#define HANDSHAKE_KEY "default_handshake_key"
#endif

#ifndef SECRET_KEY
#define SECRET_KEY "default_secret_key"
#endif
// Communication
SerialCommunicator* com = SerialCommunicator::getInstance();

// LEDS
#define RED 29
#define YELLOW 31
#define GREEN 33
#define BLUE 8
Leds leds = Leds(RED, YELLOW, GREEN, BLUE);

// Buzzer
#define BUZZER 9

// RFID
#define RST_PIN 5
#define SS_PIN 53
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Button
#define BUTTON 23

Controller* controller = Controller::getInstance(BUTTON, BUZZER, mfrc522, leds);
Api api = Api(); // Alway after controller instance
// Variables
bool available = false;


void setup() {
  leds.checkLeds();
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(BUZZER, OUTPUT);
  leds.setRed();
  controller->refreshOutputs();
  com->begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  if (com->messageAvailable()) {
    ProtocolMessage* message = com->receiveMessage();
    api.findRoute(*message);
  }
  
  controller->mainLoop();

  delay(250);
} 