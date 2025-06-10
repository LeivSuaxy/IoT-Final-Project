#include <Arduino.h>
#include "SerialCommunicator.h"
#include <Protocol.h>
#include "Service.h"
#include "Api.h"
#include "SessionState.h"

Api::Api(){
    this->_com = SerialCommunicator::getInstance();
    this->_controller = Controller::getInstance();
    this->_security = Security::getInstance();
}

bool Api::authenticateMessage(ProtocolMessage& message) {
    SessionState* session = SessionState::getInstance();

    if(!session->isAuthenticated()) {
        this->_com->sendERR("NOT AUTHENTICATED");
        return false;
    }

    String receivedHMAC = message.getHMAC();
    this->_com->sendINFO("Received HMAC: " + receivedHMAC );
    String generatedHMAC = session->calculateNextHash(false);
    this->_com->sendINFO("Generated HMAC: " + generatedHMAC);
    
    this->_com->sendINFO((String)session->getInit() + ":" + (String)session->getStep() + ":" + (String)session->getLimit());

    bool isValid = session->validateReceivedMessage(receivedHMAC);

    if (receivedHMAC == "REHANDSHAKE") {
        this->_com->sendINFO("REHANDSHAKE REQUESTED");
        session->reset();
        return false;
    }

    return isValid;
}

void Api::findRoute(ProtocolMessage& message) {
    if(message.getType() == MessageType::AUTH) {
        this->findAuth(message);
        return;
    }

    if(!authenticateMessage(message)) {
        this->_com->sendERR("AUTHENTICATION FAILED");
        return;
    }

    switch (message.getType())
    {
    case MessageType::CMD:
        this->_com->sendINFO("COMMAND RECEIVED: " + message.getData());
        this->findCommand(message);
        break;
    
    default:
        this->_com->sendINFO(message.toString());
        this->_com->sendERR("NOT FOUND ROUTE");
    }
}

void Api::findAuth(ProtocolMessage& message) {
    String command = message.getData();
    this->_com->sendINFO(command);
    this->_com->sendINFO(command);

    if (command.startsWith("HDSHK_INIT")) {
        this->_com->sendACK("RECEIVED HANDSHAKE INIT");
        
        // Parse the command: HANDSHAKE_INIT|hash&values
        int ampersandIndex = message.getHMAC().indexOf('&');
        this->_com->sendINFO("Ampersand index: " + String(ampersandIndex));
        String hash;
        String authValues;
        
        if (ampersandIndex != -1) {
            hash = message.getHMAC().substring(0, ampersandIndex);
            authValues = message.getHMAC().substring(ampersandIndex + 1);
            
            this->_com->sendINFO("Hash: " + hash);
            this->_com->sendINFO("Auth values: " + authValues);
            
            this->_security->setHashBuilder((String&) authValues);
            String expectedHash = this->_security->generateHMAC(true);

            if (expectedHash.equalsIgnoreCase(hash)) {
                int firstColon = authValues.indexOf(':');
                int secondColon = authValues.indexOf(':', firstColon + 1);

                if (firstColon != -1 && secondColon != -1) {
                    uint32_t init = authValues.substring(0, firstColon).toInt();
                    uint32_t step = authValues.substring(firstColon + 1, secondColon).toInt();
                    uint32_t limit = authValues.substring(secondColon + 1).toInt();
                    
                    // Initialize session
                    SessionState* session = SessionState::getInstance();
                    session->initializeSession(init, step, limit);
                    session->setAuthenticated(true);
                    
                    this->_com->sendOK("HANDSHAKE SUCCESSFUL");
                    this->_security->setLogged(true);
                } else {
                    this->_com->sendERR("INVALID AUTH VALUES FORMAT");
                    return;
                }



            } else {
                this->_com->sendERR(this->_security->getSecretKey(HANDSHAKE_KEY));
                this->_com->sendERR(SECRET_KEY);
                this->_com->sendERR("HANDSHAKE FAILED");
                this->_com->sendERR("EXPECTED: " + hash);
                this->_com->sendERR("GOT: " + expectedHash);
                return;
            }
        //HANDSHAKE_INIT|a9e5b361265f201086933f1f33923a0e&996:14:6698

        }
    }
}

void Api::findCommand(ProtocolMessage& message){
    String command = message.getData();
    this->_com->sendINFO("Command: " + command);
    if (command.equalsIgnoreCase("ENABLE"))
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
    else if (command == "SOUND_DENY")
    {
        this->_com->sendACK("RECEIVED SOUND_DENY");
        this->_controller->soundDeny();
        return;
    } 
}