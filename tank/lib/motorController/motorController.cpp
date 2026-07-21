#include "motorController.h"

namespace {
// Safe servo pulse limits for PCA9685 at 50 Hz.
// Avoid overly extreme pulses to prevent driving servos beyond end stops.
const int SERVO_MIN_PULSE = 110;
const int SERVO_MAX_PULSE = 500;
} // namespace

MotorController::MotorController(int frequency, uint8_t address)
    : frequency(frequency), pwm(address) {}

void MotorController::setAddress(uint8_t address) {
    // Recreate the PWM driver with the I2C address found by main.
    pwm = PWMController(address);
}

bool MotorController::begin() {
    // Initialize the PCA9685 chip and set the frequency shared by all channels.
    return pwm.begin() && pwm.setPWMFreq(frequency);
}

bool MotorController::isCommunicationHealthy() const {
    return pwm.isCommunicationHealthy();
}

void MotorController::DCrun(int motorNumber, int direction, int speed) {
    int directionChannel = -1;
    int speedChannel = -1;

    // Each M port on the shield corresponds to two PCA9685 channels:
    // one selects direction, the other controls PWM speed.
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

    // Before changing direction remove PWM: avoid switching direction while the
    // H-bridge is still commanded at non-zero speed.
    if (lastDirection[motorNumber] != 0 && lastDirection[motorNumber] != requestedDirection) {
        setPwmChannel(speedChannel, 0);
    }

    // Direction is written before speed so a start from standstill does not
    // receive a pulse with the previous direction.
    setDigitalChannel(directionChannel, requestedDirection == FORWARD);
    setPwmChannel(speedChannel, requestedSpeed);
    lastDirection[motorNumber] = requestedDirection;
}

void MotorController::DCbrake(int motorNumber) {
    // Turn off PWM speed and drive the motor direction low for the chosen motor.
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
    // Used at startup and for safety cases.
    DCbrake(M1);
    DCbrake(M2);
    DCbrake(M3);
    DCbrake(M4);
}

void MotorController::bipolarStepperStop(int motorA, int motorB) {
    // A bipolar stepper uses two motor outputs: turn both off.
    DCbrake(motorA);
    DCbrake(motorB);
}

void MotorController::servoTurn(int servoNumber, int degree) {
    // Convert servo degrees into a PCA9685 PWM value.
    int constrainedDegree = constrain(degree, 0, 180);
    int pulse = map(constrainedDegree, 0, 180, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
    setPwmChannel(servoNumber, pulse);
}

void MotorController::servoPairTurn(int servoA, int servoB, int degree, int invertedDegreeBase) {
    // The first servo follows the normal angle.
    int firstAngle = constrain(degree, 0, 180);

    // The second servo moves mirrored relative to the first.
    int secondAngle = constrain(invertedDegreeBase - firstAngle, 0, 180);

    servoTurn(servoA, firstAngle);
    servoTurn(servoB, secondAngle);
}

void MotorController::setDigitalChannel(int channel, bool value) {
    // To force LOW on the PCA9685 use the full-off bit.
    // To force HIGH use the full-on bit.
    pwm.setPWM(channel, value ? 4096 : 0, value ? 0 : 4096);
}

void MotorController::setPwmChannel(int channel, int value) {
    // value <= 0 completely turns the channel off.
    if (value <= 0) {
        pwm.setPWM(channel, 0, 4096);
    }
    // value >= 4096 fully turns the channel on.
    else if (value >= MAX_SPEED) {
        pwm.setPWM(channel, 4096, 0);
    }
    // Otherwise generate normal PWM from 0 up to the requested value.
    else {
        pwm.setPWM(channel, 0, value);
    }
}
