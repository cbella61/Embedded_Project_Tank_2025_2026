#ifndef PWM_CONTROLLER_H
#define PWM_CONTROLLER_H

#include <Arduino.h>

/*
 * DRIVER MINIMALE PCA9685
 *
 * La PCA9685 e' il chip PWM della shield. Questo file contiene solo le
 * operazioni basse livello:
 * - inizializzazione I2C
 * - impostazione frequenza PWM
 * - scrittura dei registri ON/OFF di un canale
 */
class PWMController {
  public:
    explicit PWMController(uint8_t address = 0x40);

    // Avvia I2C e resetta i registri base della PCA9685.
    void begin();

    // Imposta la frequenza PWM condivisa da tutti i canali.
    void setPWMFreq(float frequency);

    // Imposta il tempo ON/OFF di un canale PWM (0-15).
    void setPWM(uint8_t channel, uint16_t on, uint16_t off);

  private:
    // Registri principali della PCA9685.
    static const uint8_t MODE1_REGISTER = 0x00;
    static const uint8_t MODE2_REGISTER = 0x01;
    static const uint8_t PRESCALE_REGISTER = 0xFE;
    static const uint8_t LED0_ON_L_REGISTER = 0x06;

    // Indirizzo I2C reale della PCA9685.
    uint8_t address;

    // Lettura/scrittura registro via Wire.
    uint8_t readRegister(uint8_t registerAddress);
    void writeRegister(uint8_t registerAddress, uint8_t value);
};

#endif
