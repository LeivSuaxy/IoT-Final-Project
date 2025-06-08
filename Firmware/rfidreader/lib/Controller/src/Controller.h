#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <Arduino.h>
#include <Leds.h>
#include <MFRC522.h>
#include <SPI.h>
#include <SHA256.h>
#include <SerialCommunicator.h>
#include <Security.h>

class Controller {
    private:
        Controller(int buttonPin, int buzzerPin, MFRC522 mfrc522, Leds leds); // Todo DEFINE REAL THINGS
        static Controller* _instance;
        Leds _leds;
        SHA256 sha256;
        MFRC522 _mfrc522;
        SerialCommunicator* _com;
        Security* _security;
        int _buttonPin;
        int _buzzerPin;
        bool _available = false;
        Controller(const Controller&) = delete;
        Controller& operator=(const Controller&) = delete;
        
    public:
        static Controller* getInstance(int buttonPin, int buzzerPin, MFRC522 mfrc522, Leds leds);
        static Controller* getInstance();
        void mainLoop();
        void refreshOutputs();
        void readCard();
        void alter();
        void ENABLE();
        void DISABLE();
        bool isAvailable() { return this->_available; }
        void setAvailable(bool available) { this->_available = available; }
};

#endif