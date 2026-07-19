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
    bool begin();

    // Imposta la frequenza PWM condivisa da tutti i canali.
    bool setPWMFreq(float frequency);

    // Imposta il tempo ON/OFF di un canale PWM (0-15).
    bool setPWM(uint8_t channel, uint16_t on, uint16_t off);

    // Resta false dopo un NACK, una lettura corta o un canale non valido.
    // Il chiamante puo' trasformare questa condizione in un fault sicuro.
    bool isCommunicationHealthy() const;

  private:
    // Registri principali della PCA9685.
    static const uint8_t MODE1_REGISTER = 0x00;
    static const uint8_t MODE2_REGISTER = 0x01;
    static const uint8_t PRESCALE_REGISTER = 0xFE;
    static const uint8_t LED0_ON_L_REGISTER = 0x06;

    // Indirizzo I2C reale della PCA9685.
    uint8_t address;
    bool communicationHealthy = true;

    // Lettura/scrittura registro via Wire.
    bool readRegister(uint8_t registerAddress, uint8_t& value);
    bool writeRegister(uint8_t registerAddress, uint8_t value);
};

#endif
