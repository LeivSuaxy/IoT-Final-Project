#include <Arduino.h>
#include <MFRC522.h>
#include <Leds.h>
#include <Controller.h>
#include <SerialCommunicator.h>
#include <SPI.h>
#include <SHA256.h>
#include <Api.h>
#include <Protocol.h>

Controller* Controller::_instance = nullptr;

Controller::Controller(int buttonPin, MFRC522 mfrc522, Leds leds) : _mfrc522(mfrc522), _buttonPin(buttonPin), _leds(leds) {
    this->_leds = leds;
    this->_available = false;
    this->_mfrc522 = mfrc522;
    this->_buttonPin = buttonPin;
    this->_com = SerialCommunicator::getInstance();
    this->_security = Security::getInstance();
    this->refreshOutputs();
}

void Controller::alter() {
    _available = !_available;
    this->refreshOutputs();
}

void Controller::readCard() {
    this->_leds.setGreen();

    String uidStr;
    for (byte i = 0; i < this->_mfrc522.uid.size; i++) {
    if (this->_mfrc522.uid.uidByte[i] < 0x10) uidStr += "0";
        uidStr += String(this->_mfrc522.uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();

    this->sha256.reset();
    this->sha256.update((const uint8_t*)uidStr.c_str(), uidStr.length());
    uint8_t hashBin[32];
    this->sha256.finalize(hashBin, sizeof(hashBin));

    String hashStr = "";

    for (int i = 0; i < 32; i++) {
        if (hashBin[i] < 0x10) hashStr += "0";
        hashStr += String(hashBin[i], HEX);
    }
    hashStr.toUpperCase();
    this->_com->sendOK(hashStr);

    delay(1000);
    this->alter();
}

// Public
Controller* Controller::getInstance() {
    return _instance;
}

Controller* Controller::getInstance(int buttonPin, MFRC522 mfrc522, Leds leds) {
    if (_instance == nullptr) {
        _instance = new Controller(buttonPin, mfrc522, leds);
    }
    return _instance;
}

void Controller::mainLoop() {
    if (digitalRead(this->_buttonPin) == LOW) {
        this->alter();
    }

    if (!this->_leds.getBlueState() && this->_security->isLogged()) {
        this->_leds.setBlue();
    }

    if (this->_available && this->_mfrc522.PICC_IsNewCardPresent() && this->_mfrc522.PICC_ReadCardSerial()) {
        this->readCard();
    }
}

void Controller::refreshOutputs() {
    if (this->_available) {
        this->_leds.setYellow();
        return;
    }
    this->_leds.setRed();
}

void Controller::ENABLE() {
    this->_available = true;
    this->refreshOutputs();
    this->_com->sendOK("ENABLE");
}

void Controller::DISABLE() {
    this->_available = false;
    this->refreshOutputs();
    this->_com->sendOK("DISABLE");
}