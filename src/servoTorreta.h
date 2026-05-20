#ifndef SERVO_TORRETA_H
#define SERVO_TORRETA_H
#define STEPS_PER_REV 2048 // Number of steps per revolution for the stepper motor

#define IN1   11
#define IN2   10
#define IN3   9
#define IN4   8

#include <Arduino.h>
#include <Servo.h>
#include <Stepper.h>


void StepperTorretta_begin();

void StepperTorretta_updateJoystick(int joystickValue);

void StepperTorretta_setZero();

void StepperTorretta_stop();

int StepperTorretta_getAngle();

void StepperTorretta_backtoZero();


#endif // SERVO_TORRETA_H