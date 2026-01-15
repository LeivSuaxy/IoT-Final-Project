#ifndef SECURITY_H
#define SECURITY_H

#include <Crypto.h>
#include <SHA256.h>
#include <Arduino.h>

class Security {
    private:
        SHA256 sha256;
        uint8_t key[32];
        uint32_t init = 0;
        uint32_t step = 0;
        uint32_t limit = 0;
        
    public:
        Security(const char* secretKey);
        String generateHMAC();
        bool verifyHMAC(const String& data, const String& expectedHMAC);
        void setHashBuilder(String& hashBuilder);
        String getSecretKey();
};


#endif
