/*
 * SHIELD MOTOR CONTROLLER
 *
 * This wrapper makes it easier to use the shield:
 * - DC motor commands: M1, M2, M3, M4
 * - servo commands: S1-S8
 *
 * Internally the shield uses a PCA9685. Each motor output has a channel for
 * direction and a channel for PWM speed.
 */

 #ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include "PWMController.h"


#define M1 1
#define M2 2
#define M3 3
#define M4 4

// Motor outputs on the shield. A bipolar stepper for the tracks uses two outputs.
// (Note: the #defines above remain for pin/channel mapping.)
#define M1_DIRECTION_CHANNEL 10
#define M1_SPEED_CHANNEL 8
#define M2_DIRECTION_CHANNEL 11
#define M2_SPEED_CHANNEL 13
#define M3_DIRECTION_CHANNEL 4
#define M3_SPEED_CHANNEL 2
#define M4_DIRECTION_CHANNEL 5
#define M4_SPEED_CHANNEL 7

// PCA9685 channels internally connected to the TB6612 motor drivers.
#define FORWARD 1
#define BACKWARD 2

// Directions accepted by DCrun().
#define MAX_SPEED 4096

// Verified servo connector channels on the shield used in this project.
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
    // Frequency must remain 50 Hz because the same PCA9685 drives the servos.
    explicit MotorController(int frequency, uint8_t address = 0x60);

    // Select the PCA9685 I2C address before begin().
    void setAddress(uint8_t address);

    // Start the PCA9685 and apply the configured frequency.
    // false signals an I2C error: the caller must enter a safe fault state.
    bool begin();

    // Returns false after an I2C error detected by the PCA9685 driver.
    bool isCommunicationHealthy() const;

    // Drive a shield motor output with direction and PWM speed.
    void DCrun(int motorNumber, int direction, int speed);

    // Stop one or all motor outputs of the shield.
    void DCbrake(int motorNumber);
    void DCbrakeAll();
    void bipolarStepperStop(int motorA, int motorB);

    // Send a standard 0-180 degree servo command to a servo channel.
    void servoTurn(int servoNumber, int degree);

    // Command two linked servos, with the second mirrored around a base angle.
    void servoPairTurn(int servoA, int servoB, int degree, int invertedDegreeBase);

  private:
    int frequency;
    PWMController pwm;
    int lastDirection[5] = {0, 0, 0, 0, 0};

    // Internal helpers: one for digital signals, one for real PWM values.
    void setDigitalChannel(int channel, bool value);
    void setPwmChannel(int channel, int value);
};

#endif
