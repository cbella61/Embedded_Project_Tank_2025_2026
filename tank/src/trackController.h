/*
 * TRACK CONTROL WITH DC MOTORS
 *
 * The yellow motors in the photos are 2-wire DC motors, not steppers.
 * Therefore each track uses a single motor port on the shield:
 * - left: M3
 * - right: M1
 *
 * M2 is left unused because on the project shield that port tends to spin
 * even with the joystick at rest.
 *
 * Joy1 joystick is converted into differential drive:
 * - driveY decides forward/backward
 * - driveX decides steering
 * - left command = forward + steer
 * - right command = forward - steer
 */

#ifndef TRACK_CONTROLLER_H
#define TRACK_CONTROLLER_H

#include <Arduino.h>

#include "motorController.h"

// Joysticks arrive from the controller already scaled 0 to 1023.
// Ideal center is 512.
#define DRIVE_JOYSTICK_CENTER 512

// Final protection for track command in the UDP 0--1023 scale.
// Applied both before and after differential mixing: it must not match
// the ESP32 DRIVE_INPUT_DEADZONE, which only filters joystick noise.
// If one side still tries to move from rest, increase by 10/20 and test on the physical tank.
#define TRACK_COMMAND_DEADZONE 40

// Each track uses a DC motor port on the shield.
// M2 remains free: use M3 for left and M1 for right.
#define LEFT_TRACK_MOTOR M1
#define RIGHT_TRACK_MOTOR M3

// Separate min and max PWM per track.
// The two DC motors are never identical: one may start earlier or run faster
// than the other even with the same command.
//
// How to adjust:
// - a track does not start on small movements: increase its MIN_PWM by 50;
// - a track starts too early/jerks: lower its MIN_PWM by 50;
// - one track is faster than the other: lower its MAX_PWM or PWM_PERCENT.
#define LEFT_TRACK_MIN_PWM 900
#define RIGHT_TRACK_MIN_PWM 900
#define LEFT_TRACK_MAX_PWM MAX_SPEED
#define RIGHT_TRACK_MAX_PWM MAX_SPEED

// Final percentage trim.
// 100 = normal, 90 = that track runs at 90%, 110 = that track pushes more.
// If M1/right runs faster than M3/left, lower RIGHT_TRACK_PWM_PERCENT.
#define LEFT_TRACK_PWM_PERCENT 100
#define RIGHT_TRACK_PWM_PERCENT 100

// Maximum I2C refresh rate when the command remains unchanged.
// A new command and a safety stop do not wait for the next period.
#define TRACK_COMMAND_REFRESH_INTERVAL_MS 20

// Joy1 X steering is linear: no hidden curve or intermediate threshold.
// Its magnitude enters directly into the differential mixing below.

// Joystick axis orientation is corrected once on the ESP32.
// Here remain only inversions due to the motor wiring.
#define LEFT_TRACK_INVERTED false
#define RIGHT_TRACK_INVERTED false

// Initialize the two DC motors for the tracks on the shield.
void TrackController_begin(MotorController& controller);

// Apply linear differential mixing of Joy1 to the two tracks.
void TrackController_update(int driveX, int driveY);

// Bring both tracks to PWM zero via DCbrake().
void TrackController_stop();

#endif
