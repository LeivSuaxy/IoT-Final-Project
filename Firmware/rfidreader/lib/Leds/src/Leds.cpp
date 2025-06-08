#include "Leds.h"

Leds::Leds(int red, int yellow, int green, int blue) : redPin(red), yellowPin(yellow), greenPin(green), bluePin(blue) {
    this->redPin = red;
    this->yellowPin = yellow;
    this->greenPin = green;
    this->bluePin = blue;

    pinMode(redPin, OUTPUT);
    pinMode(yellowPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(bluePin, OUTPUT);
}

void Leds::setRed() {
    digitalWrite(redPin, HIGH);
    digitalWrite(yellowPin, LOW);
    digitalWrite(greenPin, LOW);
}

void Leds::setYellow() {
    digitalWrite(redPin, LOW);
    digitalWrite(yellowPin, HIGH);
    digitalWrite(greenPin, LOW);
}

void Leds::setGreen() {
    digitalWrite(redPin, LOW);
    digitalWrite(yellowPin, LOW);
    digitalWrite(greenPin, HIGH);
}

void Leds::checkLeds() {
    setAll(true);
    delay(1000);
    setAll(false);
}

void Leds::setAll(bool state) {
    digitalWrite(redPin, state ? HIGH : LOW);
    digitalWrite(yellowPin, state ? HIGH : LOW);
    digitalWrite(greenPin, state ? HIGH : LOW);
    digitalWrite(bluePin, state ? HIGH : LOW);
}

void Leds::setBlue(bool state) {
    digitalWrite(bluePin, state ? HIGH : LOW);
    this->blueState = state;
}