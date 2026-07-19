#include "PWMController.h"

#include <Wire.h>

PWMController::PWMController(uint8_t address) : address(address) {}

bool PWMController::begin() {
    // Avvia il bus I2C usato per parlare con la PCA9685.
    Wire.begin();
    communicationHealthy = true;

    // MODE1 a 0 resetta il funzionamento base.
    if (!writeRegister(MODE1_REGISTER, 0x00)) {
        return false;
    }

    // MODE2 = 0x04 abilita uscite totem-pole/push-pull:
    // il segnale HIGH e' guidato davvero e non resta flottante.
    return writeRegister(MODE2_REGISTER, 0x04);
}

bool PWMController::setPWMFreq(float frequency) {
    if (frequency <= 0.0f) {
        communicationHealthy = false;
        return false;
    }

    // Per cambiare frequenza la PCA9685 deve entrare in sleep mode.
    float correctedFrequency = frequency * 0.98f;

    // Formula dal datasheet: prescale = clock / (4096 * freq) - 1.
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

    // Ogni canale PCA9685 ha 4 registri consecutivi:
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
    // Prima seleziona il registro da leggere.
    Wire.beginTransmission(address);
    Wire.write(registerAddress);
    if (Wire.endTransmission() != 0) {
        communicationHealthy = false;
        return false;
    }

    // Poi richiede un byte dalla PCA9685.
    if (Wire.requestFrom(address, static_cast<uint8_t>(1)) != 1 || !Wire.available()) {
        communicationHealthy = false;
        return false;
    }

    value = Wire.read();
    return true;
}

bool PWMController::writeRegister(uint8_t registerAddress, uint8_t value) {
    // Scrittura base di un registro PCA9685.
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
