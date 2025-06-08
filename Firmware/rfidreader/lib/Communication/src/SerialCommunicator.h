#ifndef SERIALCOMMUNICATOR_H
#define SERIALCOMMUNICATOR_H

#include <Arduino.h>
#include "Protocol.h"

class SerialCommunicator {
    private:
    //Protocol protocol;
        SerialCommunicator();
        ProtocolMessage protocolMessage;
        static SerialCommunicator* _instance;
        SerialCommunicator(const SerialCommunicator&) = delete;
        SerialCommunicator& operator=(const SerialCommunicator&) = delete;
    public:
        static SerialCommunicator* getInstance();
        void begin(long baudRate);
        void sendMessage(const String& message);
        void sendACK(const String& message);
        void sendERR(const String& message);
        void sendOK(const String& message);
        void sendMISS(const String& message);
        void sendCMD(const String& message);
        void sendINFO(const String& message);
        void sendAUTH(const String& message);
        ProtocolMessage* receiveMessage();
        bool messageAvailable();
};

#endif // SERIALCOMMUNICATOR_H