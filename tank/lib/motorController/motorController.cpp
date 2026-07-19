#include "motorController.h"

namespace {
// Limiti sicuri del pulse servo sulla PCA9685 a 50 Hz.
// Evitiamo impulsi troppo estremi per non mandare i servo oltre il fine corsa.
const int SERVO_MIN_PULSE = 110;
const int SERVO_MAX_PULSE = 500;
} // namespace

MotorController::MotorController(int frequency, uint8_t address)
    : frequency(frequency), pwm(address) {}

void MotorController::setAddress(uint8_t address) {
    // Ricrea il driver PWM con l'indirizzo I2C trovato dal main.
    pwm = PWMController(address);
}

bool MotorController::begin() {
    // Avvia il chip PCA9685 e imposta la frequenza condivisa da tutti i canali.
    return pwm.begin() && pwm.setPWMFreq(frequency);
}

bool MotorController::isCommunicationHealthy() const {
    return pwm.isCommunicationHealthy();
}

void MotorController::DCrun(int motorNumber, int direction, int speed) {
    int directionChannel = -1;
    int speedChannel = -1;

    // Ogni M della shield corrisponde a due canali PCA9685:
    // uno decide la direzione, l'altro decide la velocita PWM.
    switch (motorNumber) {
    case M1:
        directionChannel = M1_DIRECTION_CHANNEL;
        speedChannel = M1_SPEED_CHANNEL;
        break;
    case M2:
        directionChannel = M2_DIRECTION_CHANNEL;
        speedChannel = M2_SPEED_CHANNEL;
        break;
    case M3:
        directionChannel = M3_DIRECTION_CHANNEL;
        speedChannel = M3_SPEED_CHANNEL;
        break;
    case M4:
        directionChannel = M4_DIRECTION_CHANNEL;
        speedChannel = M4_SPEED_CHANNEL;
        break;
    default:
        return;
    }

    int requestedDirection = direction == FORWARD ? FORWARD : BACKWARD;
    int requestedSpeed = constrain(speed, 0, MAX_SPEED);

    // Prima di cambiare verso togli PWM: evita di commutare la direzione
    // mentre il ponte H e' ancora comandato a velocita diversa da zero.
    if (lastDirection[motorNumber] != 0 && lastDirection[motorNumber] != requestedDirection) {
        setPwmChannel(speedChannel, 0);
    }

    // Il verso viene scritto prima della velocita, cosi' una partenza da fermo
    // non riceve un impulso con la direzione precedente.
    setDigitalChannel(directionChannel, requestedDirection == FORWARD);
    setPwmChannel(speedChannel, requestedSpeed);
    lastDirection[motorNumber] = requestedDirection;
}

void MotorController::DCbrake(int motorNumber) {
    // Spegne velocita PWM e porta bassa la direzione del motore scelto.
    switch (motorNumber) {
    case M1:
        setPwmChannel(M1_SPEED_CHANNEL, 0);
        setDigitalChannel(M1_DIRECTION_CHANNEL, false);
        lastDirection[M1] = 0;
        break;
    case M2:
        setPwmChannel(M2_SPEED_CHANNEL, 0);
        setDigitalChannel(M2_DIRECTION_CHANNEL, false);
        lastDirection[M2] = 0;
        break;
    case M3:
        setPwmChannel(M3_SPEED_CHANNEL, 0);
        setDigitalChannel(M3_DIRECTION_CHANNEL, false);
        lastDirection[M3] = 0;
        break;
    case M4:
        setPwmChannel(M4_SPEED_CHANNEL, 0);
        setDigitalChannel(M4_DIRECTION_CHANNEL, false);
        lastDirection[M4] = 0;
        break;
    }
}

void MotorController::DCbrakeAll() {
    // Usato all'avvio e nei casi di sicurezza.
    DCbrake(M1);
    DCbrake(M2);
    DCbrake(M3);
    DCbrake(M4);
}

void MotorController::bipolarStepperStop(int motorA, int motorB) {
    // Uno stepper bipolare usa due uscite motore: spegniamo entrambe.
    DCbrake(motorA);
    DCbrake(motorB);
}

void MotorController::servoTurn(int servoNumber, int degree) {
    // Converte i gradi del servo nel valore PWM PCA9685.
    int constrainedDegree = constrain(degree, 0, 180);
    int pulse = map(constrainedDegree, 0, 180, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
    setPwmChannel(servoNumber, pulse);
}

void MotorController::servoPairTurn(int servoA, int servoB, int degree, int invertedDegreeBase) {
    // Il primo servo segue l'angolo normale.
    int firstAngle = constrain(degree, 0, 180);

    // Il secondo servo si muove al contrario rispetto al primo.
    int secondAngle = constrain(invertedDegreeBase - firstAngle, 0, 180);

    servoTurn(servoA, firstAngle);
    servoTurn(servoB, secondAngle);
}

void MotorController::setDigitalChannel(int channel, bool value) {
    // Per forzare LOW sulla PCA9685 serve il bit full-off.
    // Per forzare HIGH serve il bit full-on.
    pwm.setPWM(channel, value ? 4096 : 0, value ? 0 : 4096);
}

void MotorController::setPwmChannel(int channel, int value) {
    // value <= 0 spegne completamente il canale.
    if (value <= 0) {
        pwm.setPWM(channel, 0, 4096);
    }
    // value >= 4096 accende completamente il canale.
    else if (value >= MAX_SPEED) {
        pwm.setPWM(channel, 4096, 0);
    }
    // Altrimenti genera PWM normale da 0 fino al valore richiesto.
    else {
        pwm.setPWM(channel, 0, value);
    }
}
