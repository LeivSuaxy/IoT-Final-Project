#ifndef SESSIONSTATE_H
#define SESSIONSTATE_H

#include <Arduino.h>
#include <Security.h>

class SessionState {
    private:
        uint32_t init;
        uint32_t step;
        uint32_t limit;
        bool is_sending;
        bool authenticated;
        Security* _security;
        static SessionState* _instance;
        SessionState();
        SessionState(const SessionState&) = delete;
        SessionState& operator=(const SessionState&) = delete;
    public:
        static SessionState* getInstance();

        // Session management
        void initializeSession(uint32_t init, uint32_t step, uint32_t limit);
        void reset();
        bool isAuthenticated() const { return authenticated; }
        void setAuthenticated(bool value) { authenticated = value; }

        // Hash operations
        SessionState& forSending();
        SessionState& forReceiving();
        String calculateNextHash(bool increment = true);
        bool validateHash(const String& hash);

        // State Checks
        bool needsRehandshake() const;
        String getAuthForMessage();
        bool validateReceivedMessage(const String& message);

        // Getters
        uint32_t getInit() const { return init; }
        uint32_t getStep() const { return step; }
        uint32_t getLimit() const { return limit; }
        bool isSending() const { return is_sending; }
};

#endif