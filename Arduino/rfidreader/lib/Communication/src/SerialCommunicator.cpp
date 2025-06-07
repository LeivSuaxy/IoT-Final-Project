#include "SerialCommunicator.h"
#include "Protocol.h"

SerialCommunicator* SerialCommunicator::_instance = nullptr;

SerialCommunicator* SerialCommunicator::getInstance() {
    if (_instance == nullptr) {
        _instance = new SerialCommunicator();
    }
    return _instance;
}

SerialCommunicator::SerialCommunicator() {
    protocolMessage = ProtocolMessage();
}

void SerialCommunicator::begin(long baudRate) {
    Serial.begin(baudRate);
}

void SerialCommunicator::sendMessage(const String& message) {
    Serial.println(message);
}

ProtocolMessage* SerialCommunicator::receiveMessage() {
    String message = Serial.readStringUntil('\n');

    ProtocolMessage* pMessage = this->protocolMessage.fromString(message);

    if (pMessage != nullptr) {
        MessageType typeMessage = pMessage->getType();

        this->sendACK("Received Message with MessageType " + ProtocolMessage::messageTypeToString(typeMessage));
        return pMessage;
    }

    this->sendERR("Invalid protocol message");
    return nullptr;
}

bool SerialCommunicator::messageAvailable() {
    return Serial.available();
}

// Protocols Messages

void SerialCommunicator::sendACK(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::ACK, message));
    delay(10);
}

void SerialCommunicator::sendERR(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::ERR, message));
    delay(10);
}

void SerialCommunicator::sendOK(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::OK, message));
    delay(10);
}

void SerialCommunicator::sendMISS(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::OK, message));
    delay(10);
}

void SerialCommunicator::sendCMD(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::CMD, message));
    delay(10);
}

void SerialCommunicator::sendINFO(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::INFO, message));
    delay(10);
}

void SerialCommunicator::sendAUTH(const String& message) {
    Serial.println(this->protocolMessage.toStringAnonymous(MessageType::AUTH, message));
    delay(10);
}

