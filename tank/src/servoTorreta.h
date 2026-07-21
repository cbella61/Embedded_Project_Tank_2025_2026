/*
 * TURRET
 *
 * This module manages two different movements:
 *
 * 1. Horizontal turret:
 *    - it's a stepper with an external driver
 *    - driver signals are connected to digital pins D2-D5
 *    - uses sequence A, B, C, D as in the old working code
 *
 * 2. Elevation:
 *    - uses two servos connected to the shield on S5 and S6
 *    - the two servos move mirrored to raise/lower together
 */

#ifndef SERVO_TORRETA_H
#define SERVO_TORRETA_H

#include <Arduino.h>

#include "motorController.h"

// Number of steps used to convert the turret logical position into degrees.
#define STEPS_PER_REV 2048

// Physical map: turret driver A/B/C/D connected to the shield digital pins.
#define TURRET_DRIVER_A_PIN 2
#define TURRET_DRIVER_B_PIN 3
#define TURRET_DRIVER_C_PIN 4
#define TURRET_DRIVER_D_PIN 5

// Higher means slower turret.
#define TURRET_STEP_INTERVAL_MS 5

// Joystick values near center that do not move turret or elevation.
#define TURRET_JOYSTICK_DEADZONE 200

// Initialize the horizontal turret stepper.
void StepperTorretta_begin();

// Read Joy2 X: below center turns left, above center turns right.
void StepperTorretta_updateJoystick(int joystickValue);

// Reset only the logical count, do not physically move the motor.
void StepperTorretta_setZero();

// Turn off all driver A/B/C/D signals.
void StepperTorretta_stop();

// Return the logical angle calculated from the steps made.
int StepperTorretta_getAngle();

// Initialize the two servos that raise and lower the turret.
void ServoTorretta_begin(MotorController& controller);

// Read Joy2 Y and gradually change the servos' angle.
void ServoTorretta_updateJoystick(int joystickValue);

// Directly set the elevation angle, respecting limits.
void ServoTorretta_setAngle(int angle);

// Set elevation to the logical minimum position.
void ServoTorretta_setZero();

// Return the current logical angle of the servos.
int ServoTorretta_getAngle();

#endif
