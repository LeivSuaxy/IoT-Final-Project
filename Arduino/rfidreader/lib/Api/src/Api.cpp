#include <Arduino.h>
#include "SerialCommunicator.h"
#include <Protocol.h>
#include "Service.h"
#include "Api.h"

Api::Api(){
    this->_com = SerialCommunicator::getInstance();
    this->_controller = Controller::getInstance();
}

void Api::findRoute(ProtocolMessage& message) {
    switch (message.getType())
    {
    case MessageType::CMD:
        //
        this->_com->sendACK("Received Command");
        this->findCommand(message);
        break;
    
    default:
        this->_com->sendERR("Not found route");
    }
}

void Api::findCommand(ProtocolMessage& message){
    String command = message.getData();

    if (command == "ENABLE")
    {
        this->_com->sendACK("RECEIVED_ENABLE");
        this->_controller->ENABLE();
        return;
    }
    else if (command == "DISABLE")
    {
        this->_com->sendACK("RECEIVED_DISABLE");
        this->_controller->DISABLE();
        return;
    }
}