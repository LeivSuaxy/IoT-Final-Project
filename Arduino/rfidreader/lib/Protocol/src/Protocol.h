#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>

enum class MessageType {
    INFO,
    ERR,
    ACK,
    MISS,
    CMD,
    OK,
};

class ProtocolMessage {
private:
    MessageType messageType;
    String data;

public:
    ProtocolMessage();
    ProtocolMessage(MessageType type, String data);
    String toStringAnonymous(MessageType type, String data);
    String toString();
    String toStringWithChecksum();
    static String messageTypeToString(MessageType type);
    static ProtocolMessage* fromString(String message);
    static String calculateChecksum(String message);
    
    MessageType getType();
    String getData();
};

#endif // PROTOCOL_H