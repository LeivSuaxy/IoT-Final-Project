#ifndef LEDS_H
#define LEDS_H

#include <Arduino.h>

class Leds {
    private:
        int redPin;
        int yellowPin;
        int greenPin;
    public:
        Leds(int red, int yellow, int green);
        void setRed();
        void setYellow();
        void setGreen();
        void checkLeds();
        void setAll(bool state);
        int getRedPin() { return this->redPin; }
        int getYellowPin() { return this->yellowPin; }
        int getGreenPin() { return this->greenPin; }
};


#endif