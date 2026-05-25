//Library for controlling DC motors and Servomotors

/*
--DC MOTOR CONTROL
The DC motors are controlled with the TB6612FNG chip.
The TB6612FNG is an H-Bridge chip used to control motors.
It can control 2 separate DC motors.
It has 3 control input per motor.
They are IN1 and IN2, which are used to control the direction of the motor,
and PWM which is used to regulate the speed trough a PWM signal.
The pin IN1 is directly connected to the PWM generator, while IN2 is IN1 inverted.


--SERVO MOTOR--
Servo motors are controlled with a 50 Hz PWM pulse.
The pulses width ranges from 1ms to 2ms with 1.5ms in the center of rotation.
it may not be so precise if you do the math, because we used a for loop to get the minimum and maximum signal value.


--CONNECTIONS--

              TB6612FNG
           ---------------
      PWM10|             |M1A
     ------|IN1A         |-----
     ~PWM10|             |M1B
     ------|IN2A         |-----
       PWM8|             |
     ------|PWMA         |
           |             |
      PWM11|             |M2A
     ------|             |-----
     ~PWM11|             |M2B
     ------|             |-----
      PWM13|PWMB         |
     ------|             |
           ---------------

              TB6612FNG
           ---------------
       PWM4|             |M3A
     ------|IN1A         |-----
      ~PWM4|             |M3B
     ------|IN2A         |-----
       PWM2|             |
     ------|PWMA         |
           |             |
       PWM5|             |M4A
     ------|             |-----
      ~PWM5|             |M4B
     ------|             |-----
       PWM7|PWMB         |
     ------|             |
           ---------------

    PWM0 -> SERVO1
    PWM1 -> SERVO2
    PWM3 -> SERVO3
    PWM6 -> SERVO4
    PWM9 -> SERVO5
    PWM12 -> SERVO6
    PWM14 -> SERVO7
    PWM15 -> SERVO8


*/

//If we add an angle parameter for every servo motor we can have the actual angle of a servo in case we need if
//Example to have a slow rotation or an increment/decremet.

#ifndef __MOTOR_CONTROLLER_H__
#define __MOTOR_CONTROLLER_H__

#include "PWMController.h"

//DC Motors
#define M1 1
#define M2 2
#define M3 3
#define M4 4

//Stepper Motors
#define SM1 1
#define SM2 2

//Motor pins
#define IN1 10
#define PWM1 8
#define IN2 11
#define PWM2 13
#define IN3 4
#define PWM3 2
#define IN4 5
#define PWM4 7

//Directions
#define FORWARD 0
#define BACKWARD 1
#define BREAK 2

//Stepper modes
#define SINGLE 0
#define DOUBLE 1

//Motor speed
#define MAX_SPEED 4096

//Servo motors levels
#define LMAX 540
#define LMIN 80

//Servo motors pins
#define S1 0
#define S2 1
#define S3 3
#define S4 6
#define S5 9
#define S6 12
#define S7 14
#define S8 15

//BOOLEAN
#define HIGH 1
#define LOW 0

class MotorController{
    public:
        MotorController(int freq); //constructor with frequency parameter in order to set PWM freq.
        void begin();
        void DCrun(int motorNumber, int direction, int speed); //to make a DC motor run at a certain speed
        void DCbrake(int motorNumber); //to stop a DC motor
        void DCbrakeAll(); //to stop all DC motors
        void servoTurn(int servoNumber, int degree);
        void setStepperMotors(int stepper, int motor1, int motor2);
        void stepperTurn(int stepper, int steps, int direction, int speed);
        void stepperRelease(int stepper);
    private:
        int freq;
        PWMController PWM;
        int steppers[2][2];
        int stepIndex[2];
        void setPin(int pin, bool value); //To set the control pin INx to on, without PWM
        void setPWM(int pin, int value);
        void singleStep(int stepper, int mode);
};

#endif
