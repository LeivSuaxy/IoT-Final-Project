#ifndef SECURITY_H
#define SECURITY_H

#include <Crypto.h>
#include <SHA256.h>
#include <Arduino.h>

class Security {
    private:
        Security();
        SHA256 sha256;
        uint8_t key[32];
        uint32_t init = 0;
        uint32_t step = 0;
        uint32_t limit = 0;
        bool logged = false;
        static Security* _instance;
        Security(const Security&) = delete;
        Security& operator=(const Security&) = delete;        
    public:
        static Security* getInstance();
        String generateHMAC(bool handshake = false);
        bool verifyHMAC(const String& data, const String& expectedHMAC);
        void setHashBuilder(String& hashBuilder);
        String getSecretKey(String key);
        bool isLogged() const { return logged; }
        void setLogged(bool value) { logged = value; }
};


#endif
