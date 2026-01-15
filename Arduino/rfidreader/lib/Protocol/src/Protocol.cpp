#include <Arduino.h>
#include <Protocol.h>

ProtocolMessage::ProtocolMessage() {
    
}

ProtocolMessage::ProtocolMessage(MessageType type, String data, String hmac = "") {
    this->messageType = type;
    this->data = data;
    this->_hmac = hmac;
}

String ProtocolMessage::toStringAnonymous(MessageType type, String data) {
    String typeStr = "";
    switch(type) {
        case MessageType::AUTH: typeStr = "AUTH"; break;
        case MessageType::INFO: typeStr = "INFO"; break;
        case MessageType::ERR: typeStr = "ERR"; break;
        case MessageType::ACK: typeStr = "ACK"; break;
        case MessageType::MISS: typeStr = "MISS"; break;
        case MessageType::CMD: typeStr = "CMD"; break;
        case MessageType::OK: typeStr = "OK"; break;
    }
    return typeStr + "_" + data;
}

String ProtocolMessage::toString() {
    String typeStr = "";
    switch(messageType) {
        case MessageType::AUTH: typeStr = "AUTH"; break;
        case MessageType::INFO: typeStr = "INFO"; break;
        case MessageType::ERR: typeStr = "ERR"; break;
        case MessageType::ACK: typeStr = "ACK"; break;
        case MessageType::MISS: typeStr = "MISS"; break;
        case MessageType::CMD: typeStr = "CMD"; break;
        case MessageType::OK: typeStr = "OK"; break;
    }
    return typeStr + "_" + data;
}
    
String ProtocolMessage::toStringWithChecksum() {
    String baseMessage = toString();
    String checksum = calculateChecksum(baseMessage);
    return baseMessage + ";" + checksum;
}
    
static ProtocolMessage* ProtocolMessage::fromString(String message) {
    int hmacPos = message.lastIndexOf('|');
    String actualMessage = message;
    String hmac = "";

    if (hmacPos != -1) {
        actualMessage = message.substring(0, hmacPos);
        hmac = message.substring(hmacPos + 1);
    }

    int underscorePos = message.indexOf('_');
    if (underscorePos <= 0) {
        return nullptr;
    }
    
    String typeStr = message.substring(0, underscorePos);
    String dataStr = message.substring(underscorePos + 1);
    
    MessageType type;
    if (typeStr == "AUTH") type = MessageType::AUTH;
    else if (typeStr == "INFO") type = MessageType::INFO;
    else if (typeStr == "ERR") type = MessageType::ERR;
    else if (typeStr == "ACK") type = MessageType::ACK;
    else if (typeStr == "MISS") type = MessageType::MISS;
    else if (typeStr == "CMD") type = MessageType::CMD;
    else if (typeStr == "OK") type = MessageType::OK;
    else return nullptr;

    ProtocolMessage* msg = new ProtocolMessage(type, dataStr);
    msg->setHMAC(hmac);
    return msg;
}

static String ProtocolMessage::messageTypeToString(MessageType type) {
    String message;
    switch(type) {
        case MessageType::AUTH: message = "AUTH"; break;
        case MessageType::INFO: message = "INFO"; break;
        case MessageType::ERR: message = "ERR"; break;
        case MessageType::ACK: message = "ACK"; break;
        case MessageType::MISS: message = "MISS"; break;
        case MessageType::CMD: message = "CMD"; break;
        case MessageType::OK: message = "OK"; break;
    }

    return message;
}
    
static String ProtocolMessage::calculateChecksum(String message) {
    uint16_t sum = 0;
    for (unsigned int i = 0; i < message.length(); i++) {
        sum += (uint8_t)message.charAt(i);
    }
    
    char checksum[5];
    sprintf(checksum, "%04X", sum);
    return String(checksum);
}
    
MessageType ProtocolMessage::getType() {
    return messageType;
}
    
String ProtocolMessage::getData() {
    return data;
}
