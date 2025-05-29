#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>

enum class MessageType {
    AUTH,
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
    String _hmac;
public:
    ProtocolMessage();
    ProtocolMessage(MessageType type, String data, String hmac = "");
    String toStringAnonymous(MessageType type, String data);
    String toString();
    String toStringWithChecksum();
    String getHMAC() const { return _hmac; }
    void setHMAC(const String& hmac) { _hmac = hmac; }
    static String messageTypeToString(MessageType type);
    static ProtocolMessage* fromString(String message);
    static String calculateChecksum(String message);
    
    MessageType getType();
    String getData();
};

#endif // PROTOCOL_H