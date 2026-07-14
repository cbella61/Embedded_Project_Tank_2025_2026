#include "PWMController.h"

#include <Wire.h>

PWMController::PWMController(uint8_t address) : address(address) {}

void PWMController::begin() {
    // Avvia il bus I2C usato per parlare con la PCA9685.
    Wire.begin();

    // MODE1 a 0 resetta il funzionamento base.
    writeRegister(MODE1_REGISTER, 0x00);

    // MODE2 = 0x04 abilita uscite totem-pole/push-pull:
    // il segnale HIGH e' guidato davvero e non resta flottante.
    writeRegister(MODE2_REGISTER, 0x04);
}

void PWMController::setPWMFreq(float frequency) {
    // Per cambiare frequenza la PCA9685 deve entrare in sleep mode.
    float correctedFrequency = frequency * 0.98f;

    // Formula dal datasheet: prescale = clock / (4096 * freq) - 1.
    float prescaleValue = (25000000.0f / (4096.0f * correctedFrequency)) - 1.0f;
    uint8_t prescale = static_cast<uint8_t>(floor(prescaleValue + 0.5f));

    uint8_t oldMode = readRegister(MODE1_REGISTER);
    uint8_t sleepMode = (oldMode & 0x7F) | 0x10;

    // Entra in sleep, scrive prescaler, ripristina modo precedente e riavvia.
    writeRegister(MODE1_REGISTER, sleepMode);
    writeRegister(PRESCALE_REGISTER, prescale);
    writeRegister(MODE1_REGISTER, oldMode);
    delay(5);
    writeRegister(MODE1_REGISTER, oldMode | 0xA1);
}

void PWMController::setPWM(uint8_t channel, uint16_t on, uint16_t off) {
    // Ogni canale PCA9685 ha 4 registri consecutivi:
    // ON_L, ON_H, OFF_L, OFF_H.
    Wire.beginTransmission(address);
    Wire.write(LED0_ON_L_REGISTER + (4 * channel));
    Wire.write(on & 0xFF);
    Wire.write(on >> 8);
    Wire.write(off & 0xFF);
    Wire.write(off >> 8);
    Wire.endTransmission();
}

uint8_t PWMController::readRegister(uint8_t registerAddress) {
    // Prima seleziona il registro da leggere.
    Wire.beginTransmission(address);
    Wire.write(registerAddress);
    Wire.endTransmission();

    // Poi richiede un byte dalla PCA9685.
    Wire.requestFrom(address, static_cast<uint8_t>(1));
    return Wire.available() ? Wire.read() : 0;
}

void PWMController::writeRegister(uint8_t registerAddress, uint8_t value) {
    // Scrittura base di un registro PCA9685.
    Wire.beginTransmission(address);
    Wire.write(registerAddress);
    Wire.write(value);
    Wire.endTransmission();
}
