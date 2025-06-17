#include <Security.h>
#include <Crypto.h>
#include <SHA256.h>

Security* Security::_instance = nullptr;

Security::Security() {}

Security* Security::getInstance() {
    if (_instance == nullptr) {
        _instance = new Security();
    }
    return _instance;
}

String Security::getSecretKey(String key) {
    int part1 = this->init * this->step;
    int part2 = this->limit + this->step;
    int part3 = this->step + this->limit - this->init;

    String combinedKey = key + String(part1) + String(part2) + String(part3);
    return combinedKey;
}

String Security::generateHMAC(bool handshake=false) {
    String combinedKey = getSecretKey(handshake ? HANDSHAKE_KEY : SECRET_KEY);

    SHA256 sha256;
    sha256.update(combinedKey.c_str(), combinedKey.length());  // Add this line
    uint8_t hash[32];
    sha256.finalize(hash, 32);

    String hmac = "";
    for (int i = 0; i < 16; i++) {  // Use only first 16 bytes to match Rust implementation
        char hex[3];
        sprintf(hex, "%02x", hash[i]);
        hmac += hex;
    }

    return hmac;
}

bool Security::verifyHMAC(const String& data, const String& expectedHMAC) {
    String calculatedHMAC = generateHMAC();
    return calculatedHMAC.equalsIgnoreCase(expectedHMAC);
}

void Security::setHashBuilder(String& hashBuilder) {
    // This function is not implemented in the original code.
    // It can be used to set a custom hash builder if needed.
    // For now, we leave it empty.

    // Parse the format "init:step:limit" and validate
    int colonCount = 0;
    for (int i = 0; i < hashBuilder.length(); i++) {
        if (hashBuilder.charAt(i) == ':') colonCount++;
    }

    // Check if format has exactly 2 colons
    if (colonCount != 2) {
        return; // Invalid format
    }

    // Find colon positions
    int firstColon = hashBuilder.indexOf(':');
    int secondColon = hashBuilder.indexOf(':', firstColon + 1);

    // Extract substrings
    String initStr = hashBuilder.substring(0, firstColon);
    String stepStr = hashBuilder.substring(firstColon + 1, secondColon);
    String limitStr = hashBuilder.substring(secondColon + 1);

    // Validate each part is not empty and contains only digits
    if (initStr.length() == 0 || stepStr.length() == 0 || limitStr.length() == 0) {
        return; // Empty values
    }

    // Check if all characters are digits
    for (int i = 0; i < initStr.length(); i++) {
        if (!isdigit(initStr.charAt(i))) return;
    }
    for (int i = 0; i < stepStr.length(); i++) {
        if (!isdigit(stepStr.charAt(i))) return;
    }
    for (int i = 0; i < limitStr.length(); i++) {
        if (!isdigit(limitStr.charAt(i))) return;
    }

    // Convert to integers
    int init = initStr.toInt();
    int step = stepStr.toInt();
    int limit = limitStr.toInt();

    // Validate positive values
    if (init <= 0 || step <= 0 || limit <= 0) {
        return; // Non-positive values
    }

    // Values are valid, use them as needed
    this->init = init;
    this->step = step;
    this->limit = limit;
}

