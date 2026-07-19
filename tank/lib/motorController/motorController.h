#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include "PWMController.h"

/*
 * MOTOR CONTROLLER DELLA SHIELD
 *
 * Questo wrapper rende piu' semplice usare la shield:
 * - comandi motore DC: M1, M2, M3, M4
 * - comandi servo: S1-S8
 *
 * Internamente la shield usa una PCA9685. Ogni uscita motore ha un canale per
 * direzione e un canale per velocita PWM.
 */

// Uscite motore della shield. Uno stepper bipolare dei cingoli usa due uscite.
#define M1 1
#define M2 2
#define M3 3
#define M4 4

// Canali PCA9685 collegati internamente ai driver motore TB6612.
#define M1_DIRECTION_CHANNEL 10
#define M1_SPEED_CHANNEL 8
#define M2_DIRECTION_CHANNEL 11
#define M2_SPEED_CHANNEL 13
#define M3_DIRECTION_CHANNEL 4
#define M3_SPEED_CHANNEL 2
#define M4_DIRECTION_CHANNEL 5
#define M4_SPEED_CHANNEL 7

// Direzioni accettate da DCrun().
#define FORWARD 1
#define BACKWARD 2

// La PCA9685 ha risoluzione PWM a 12 bit: 0-4096.
#define MAX_SPEED 4096

// Canali dei connettori servo verificati sulla shield usata in questo progetto.
#define S1 0
#define S2 1
#define S3 3
#define S4 6
#define S5 9
#define S6 12
#define S7 14
#define S8 15

class MotorController {
  public:
    // La frequenza deve restare a 50 Hz perche' la stessa PCA9685 pilota i servo.
    explicit MotorController(int frequency, uint8_t address = 0x60);

    // Seleziona l'indirizzo I2C della PCA9685 prima di begin().
    void setAddress(uint8_t address);

    // Avvia la PCA9685 e applica la frequenza configurata.
    // false segnala un errore I2C: il chiamante deve entrare in fault sicuro.
    bool begin();

    // Ritorna false dopo un errore I2C rilevato dal driver PCA9685.
    bool isCommunicationHealthy() const;

    // Pilota una uscita motore della shield con direzione e velocita PWM.
    void DCrun(int motorNumber, int direction, int speed);

    // Ferma una o tutte le uscite motore della shield.
    void DCbrake(int motorNumber);
    void DCbrakeAll();
    void bipolarStepperStop(int motorA, int motorB);

    // Manda un comando servo standard 0-180 gradi a un canale servo.
    void servoTurn(int servoNumber, int degree);

    // Comanda due servo collegati, con il secondo specchiato attorno a un angolo base.
    void servoPairTurn(int servoA, int servoB, int degree, int invertedDegreeBase);

  private:
    int frequency;
    PWMController pwm;
    int lastDirection[5] = {0, 0, 0, 0, 0};

    // Helper interni: uno per segnali digitali, uno per valori PWM veri.
    void setDigitalChannel(int channel, bool value);
    void setPwmChannel(int channel, int value);
};

#endif
