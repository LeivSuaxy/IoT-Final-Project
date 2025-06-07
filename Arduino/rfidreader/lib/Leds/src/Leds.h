#ifndef LEDS_H
#define LEDS_H

#include <Arduino.h>

class Leds {
    private:
        int redPin;
        int yellowPin;
        int greenPin;
        int bluePin;
        bool blueState = false;
    public:
        Leds(int red, int yellow, int green, int blue);
        void setRed();
        void setYellow();
        void setGreen();
        void setBlue(bool state = true);
        void checkLeds();
        void setAll(bool state);
        int getRedPin() { return this->redPin; }
        int getYellowPin() { return this->yellowPin; }
        int getGreenPin() { return this->greenPin; }
        int getBluePin() { return this->bluePin; }
        bool getBlueState() { return this->blueState; }
};


#endif