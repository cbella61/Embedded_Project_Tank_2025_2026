#include "PWMController.h"

#include <Wire.h>

PWMController::PWMController(uint8_t address) : address(address) {}

bool PWMController::begin() {
    // Start the I2C bus used to talk to the PCA9685.
    Wire.begin();
    communicationHealthy = true;

    // MODE1 = 0 resets basic operation.
    if (!writeRegister(MODE1_REGISTER, 0x00)) {
        return false;
    }

    // MODE2 = 0x04 enables totem-pole / push-pull outputs:
    // a HIGH signal is actively driven and not left floating.
    return writeRegister(MODE2_REGISTER, 0x04);
}

bool PWMController::setPWMFreq(float frequency) {
    if (frequency <= 0.0f) {
        communicationHealthy = false;
        return false;
    }

    // To change frequency the PCA9685 must enter sleep mode.
    float correctedFrequency = frequency * 0.98f;

    // Datasheet formula: prescale = clock / (4096 * freq) - 1.
    float prescaleValue = (25000000.0f / (4096.0f * correctedFrequency)) - 1.0f;
    uint8_t prescale = static_cast<uint8_t>(floor(prescaleValue + 0.5f));

    uint8_t oldMode = 0;
    if (!readRegister(MODE1_REGISTER, oldMode)) {
        return false;
    }
    uint8_t sleepMode = (oldMode & 0x7F) | 0x10;

    // Entra in sleep, scrive prescaler, ripristina modo precedente e riavvia.
    if (!writeRegister(MODE1_REGISTER, sleepMode) || !writeRegister(PRESCALE_REGISTER, prescale) ||
        !writeRegister(MODE1_REGISTER, oldMode)) {
        return false;
    }
    delay(5);
    return writeRegister(MODE1_REGISTER, oldMode | 0xA1);
}

bool PWMController::setPWM(uint8_t channel, uint16_t on, uint16_t off) {
    if (channel > 15) {
        communicationHealthy = false;
        return false;
    }

    // Each PCA9685 channel has 4 consecutive registers:
    // ON_L, ON_H, OFF_L, OFF_H.
    Wire.beginTransmission(address);
    Wire.write(LED0_ON_L_REGISTER + (4 * channel));
    Wire.write(on & 0xFF);
    Wire.write(on >> 8);
    Wire.write(off & 0xFF);
    Wire.write(off >> 8);
    if (Wire.endTransmission() != 0) {
        communicationHealthy = false;
        return false;
    }

    return true;
}

bool PWMController::readRegister(uint8_t registerAddress, uint8_t& value) {
    // First select the register to read.
    Wire.beginTransmission(address);
    Wire.write(registerAddress);
    if (Wire.endTransmission() != 0) {
        communicationHealthy = false;
        return false;
    }

    // Then request one byte from the PCA9685.
    if (Wire.requestFrom(address, static_cast<uint8_t>(1)) != 1 || !Wire.available()) {
        communicationHealthy = false;
        return false;
    }

    value = Wire.read();
    return true;
}

bool PWMController::writeRegister(uint8_t registerAddress, uint8_t value) {
    // Basic write of a PCA9685 register.
    Wire.beginTransmission(address);
    Wire.write(registerAddress);
    Wire.write(value);
    if (Wire.endTransmission() != 0) {
        communicationHealthy = false;
        return false;
    }

    return true;
}

bool PWMController::isCommunicationHealthy() const {
    return communicationHealthy;
}
