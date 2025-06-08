#include <SessionState.h>

SessionState* SessionState::_instance = nullptr;

SessionState::SessionState() {
    this->init = 0;
    this->step = 0;
    this->limit = 0;
    this->is_sending = false;
    this->authenticated = false;
    this->_security = Security::getInstance();
}

SessionState* SessionState::getInstance() {
    if (_instance == nullptr) {
        _instance = new SessionState();
    }
    return _instance;
}

void SessionState::initializeSession(uint32_t init, uint32_t step, uint32_t limit) {
    this->init = init;
    this->step = step;
    this->limit = limit;
    this->authenticated = false;
}

void SessionState::reset() {
    this->init = 0;
    this->step = 0;
    this->limit = 0;
    this->is_sending = false;
    this->authenticated = false;
}

SessionState& SessionState::forSending() {
    this->is_sending = true;
    return *this;
}

SessionState& SessionState::forReceiving() {
    this->is_sending = false;
    return *this;
}

String SessionState::calculateNextHash(bool increment = true) {
    if (!authenticated) {
        return "";
    }

    String hashBuilder = String(init) + ":" + String(step) + ":" + String(limit);
    this->_security->setHashBuilder((String&)hashBuilder);
    String hash = this->_security->generateHMAC();

    if (increment) {
        this->init += this->step;
    }

    return hash;
}

bool SessionState::validateHash(const String& hash) {
    if (!authenticated) {
        return false;
    }

    String calculatedHash = calculateNextHash();
    return calculatedHash.equalsIgnoreCase(hash);
}

bool SessionState::needsRehandshake() const {
    return authenticated && (this->init >= this->limit);
}

String SessionState::getAuthForMessage() {
    if (!this->authenticated) {
        return "";
    }

    if (needsRehandshake()) {
        return "REHANDSHAKE";
    }

    return forSending().calculateNextHash();
}

bool SessionState::validateReceivedMessage(const String& auth) {
    if (!this->authenticated) {
        return false;
    }

    if (auth == "REHANDSHAKE") {
        return true;
    }

    return forReceiving().validateHash(auth);
}