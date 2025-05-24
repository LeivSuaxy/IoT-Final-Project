#ifndef API_H
#define API_H

#include <Arduino.h>
#include "SerialCommunicator.h"
#include "Protocol.h"
#include "Service.h"
#include "Controller.h"

class Api {
    public:
        Api();
        void findRoute(ProtocolMessage& message);
    private:
        SerialCommunicator* _com;
        Controller* _controller;
        void findCommand(ProtocolMessage& message);
};

#endif