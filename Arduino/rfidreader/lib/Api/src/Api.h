#ifndef API_H
#define API_H

#include <Arduino.h>
#include "SerialCommunicator.h"
#include "Protocol.h"
#include "Service.h"
#include "Controller.h"
#include <Security.h>

class Api {
    public:
        Api();
        void findRoute(ProtocolMessage& message);
        bool authenticateMessage(ProtocolMessage& message);
    private:
        SerialCommunicator* _com;
        Controller* _controller;
        Security* _security;
        void findAuth(ProtocolMessage& message);
        void findCommand(ProtocolMessage& message);
};

#endif