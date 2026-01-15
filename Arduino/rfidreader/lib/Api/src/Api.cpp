#include <Arduino.h>
#include "SerialCommunicator.h"
#include <Protocol.h>
#include "Service.h"
#include "Api.h"

Api::Api(){
    this->_com = SerialCommunicator::getInstance();
    this->_controller = Controller::getInstance();
    this->_security = new Security(SECRET_KEY);
}

bool Api::authenticateMessage(ProtocolMessage& message) {
    this->_com->sendINFO("AUTHENTICATING MESSAGE");
    String data = message.getData();
    this->_com->sendINFO("DATA: " + data);
    String expectedHMAC = message.getHMAC();
    this->_com->sendINFO("EXPECTED HMAC: " + expectedHMAC);

    return this->_security->verifyHMAC(data, expectedHMAC);
}

void Api::findRoute(ProtocolMessage& message) {
    if(message.getType() == MessageType::AUTH) {
        this->_com->sendACK("RECEIVED AUTH");
        this->findAuth(message);
        return;
    }

    if(!authenticateMessage(message)) {
        this->_com->sendERR("AUTHENTICATION FAILED");
        return;
    }

    this->_com->sendINFO(authenticateMessage(message) ? "AUTHENTICATED" : "NOT AUTH");
    switch (message.getType())
    {
    case MessageType::CMD:
        this->_com->sendACK("RECEIVED COMMAND");
        this->findCommand(message);
        break;
    
    default:
        this->_com->sendINFO(message.toString());
        this->_com->sendERR("NOT FOUND ROUTE");
    }
}

void Api::findAuth(ProtocolMessage& message) {
    String command = message.getData();

    if (command.startsWith("HDSHK_INIT")) {
        this->_com->sendACK("RECEIVED HANDSHAKE INIT");
        
        // Parse the command: HANDSHAKE_INIT|hash&values
        int pipeIndex = command.indexOf('|');
        int ampersandIndex = command.indexOf('&');

        String hash;
        String authValues;
        
        if (pipeIndex != -1 && ampersandIndex != -1 && pipeIndex < ampersandIndex) {
            hash = command.substring(pipeIndex + 1, ampersandIndex);
            authValues = command.substring(ampersandIndex + 1);
            
            this->_com->sendINFO("Hash: " + hash);
            this->_com->sendINFO("Auth values: " + authValues);
            
            // Process hash and authValues as needed
        } else {
            this->_com->sendERR("INVALID HANDSHAKE FORMAT");
            return;
        }

        this->_security->setHashBuilder(authValues);
        String newHash = this->_security->generateHMAC();

        if (newHash.equalsIgnoreCase(hash)){
            this->_com->sendOK("HANDSHAKE SUCCESSFUL");
        } else {
            this->_com->sendERR(this->_security->getSecretKey());
            this->_com->sendERR(SECRET_KEY);
            this->_com->sendERR("HANDSHAKE FAILED");
            this->_com->sendERR("EXPECTED: " + hash);
            this->_com->sendERR("GOT: " + newHash);
            return;
        }
        //HANDSHAKE_INIT|a9e5b361265f201086933f1f33923a0e&996:14:6698

    }
}

void Api::findCommand(ProtocolMessage& message){
    String command = message.getData();

    if (command == "ENABLE")
    {
        this->_com->sendACK("RECEIVED ENABLE");
        this->_controller->ENABLE();
        return;
    }
    else if (command == "DISABLE")
    {
        this->_com->sendACK("RECEIVED DISABLE");
        this->_controller->DISABLE();
        return;
    }
}