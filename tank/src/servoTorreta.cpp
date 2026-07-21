/*
 * TURRET OPERATION METHOD
 *
 * Horizontal turret:
 * - the external driver receives four signals: A, B, C, D
 * - on each step we energize a single output at a time
 * - forward sequence: A -> B -> C -> D -> A
 * - backward sequence: D -> C -> B -> A -> D
 *
 * Elevation:
 * - the two servos are connected to the shield PCA9685 on S5 and S6
 * - the first servo receives the normal angle
 * - the second servo receives a mirrored angle: ELEVATION_MIRROR_BASE - angle
 */

#include "servoTorreta.h"

// The horizontal turret stops at half a revolution per side.
#define TURRET_MIN_ANGLE -180
#define TURRET_MAX_ANGLE 180

// The two elevation servos must not exceed this mechanical range.
// Required range for the turret: 0 degrees = low, 47 degrees = high.
#define ELEVATION_MIN_ANGLE 0
#define ELEVATION_MAX_ANGLE 47
#define ELEVATION_MIRROR_BASE 90
#define ELEVATION_SERVO_A S5
#define ELEVATION_SERVO_B S6

// Logical center of joysticks after conversion 0-1023.
#define JOYSTICK_CENTER 512

// Servos are updated slower than the stepper for stability.
#define SERVO_INTERVAL_MS 30

// Convert degree limits to step limits.
#define TURRET_MIN_STEPS ((STEPS_PER_REV * TURRET_MIN_ANGLE) / 360)
#define TURRET_MAX_STEPS ((STEPS_PER_REV * TURRET_MAX_ANGLE) / 360)

// Pointer to the shield provided by main. Used only for servos S5/S6.
static MotorController* shield = nullptr;

// Logical state of the horizontal stepper.
static int currentSteps = 0;
static int stepIndex = 0;
static unsigned long lastStepTime = 0;
static bool stepperEnabled = false;

// Logical state of the elevation servos.
static int currentServoAngle = 0;
static unsigned long lastServoUpdateTime = 0;

// Physically write a phase to the turret driver.
// This is the same single-coil sequence used in the old Arduino direct code.
static void writeTurretStep(int phase) {
    switch (phase) {
    case 0:
        digitalWrite(TURRET_DRIVER_A_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 1:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 2:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 3:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, HIGH);
        break;
    }

    stepperEnabled = true;
}

// Step one position to the right, if not at the software limit.
static void stepRight() {
    if (currentSteps >= TURRET_MAX_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex = (stepIndex + 1) % 4;
    writeTurretStep(stepIndex);
    currentSteps++;
}

// Step one position to the left, if not at the software limit.
static void stepLeft() {
    if (currentSteps <= TURRET_MIN_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex = (stepIndex + 3) % 4;
    writeTurretStep(stepIndex);
    currentSteps--;
}

void StepperTorretta_begin() {
    // Pins D2-D5 are exposed by the shield as Arduino digital pins.
    pinMode(TURRET_DRIVER_A_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_B_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_C_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_D_PIN, OUTPUT);

    // Immediately force all outputs LOW and start from phase 0.
    stepperEnabled = true;
    StepperTorretta_stop();
    currentSteps = 0;
    stepIndex = 0;
}

void StepperTorretta_updateJoystick(int joystickValue) {
    unsigned long now = millis();

    // Limit the speed: if not enough time has passed, do not step.
    if (now - lastStepTime < TURRET_STEP_INTERVAL_MS) {
        return;
    }

    lastStepTime = now;

    // Joy2 X below center turns left, above center turns right.
    // Inside the deadzone the driver is turned off to avoid vibration.
    if (joystickValue < JOYSTICK_CENTER - TURRET_JOYSTICK_DEADZONE) {
        stepLeft();
    } else if (joystickValue > JOYSTICK_CENTER + TURRET_JOYSTICK_DEADZONE) {
        stepRight();
    } else {
        StepperTorretta_stop();
    }
}

void StepperTorretta_setZero() {
    // Reset the logical position without moving the motor.
    currentSteps = 0;
}

void StepperTorretta_stop() {
    if (!stepperEnabled) {
        return;
    }

    // All outputs low: the driver does not energize any coil.
    digitalWrite(TURRET_DRIVER_A_PIN, LOW);
    digitalWrite(TURRET_DRIVER_B_PIN, LOW);
    digitalWrite(TURRET_DRIVER_C_PIN, LOW);
    digitalWrite(TURRET_DRIVER_D_PIN, LOW);
    stepperEnabled = false;
}

int StepperTorretta_getAngle() {
    return (currentSteps * 360L) / STEPS_PER_REV;
}

void ServoTorretta_begin(MotorController& controller) {
    // Store the shield pointer and move servos to the initial position.
    shield = &controller;
    ServoTorretta_setZero();
}

void ServoTorretta_updateJoystick(int joystickValue) {
    unsigned long now = millis();

    // Servos are not updated on every loop: 30 ms is more stable.
    if (now - lastServoUpdateTime < SERVO_INTERVAL_MS) {
        return;
    }

    lastServoUpdateTime = now;

    int nextAngle = currentServoAngle;

    // Joy2 Y lowers/raises one degree at a time.
    if (joystickValue < JOYSTICK_CENTER - TURRET_JOYSTICK_DEADZONE) {
        nextAngle--;
    } else if (joystickValue > JOYSTICK_CENTER + TURRET_JOYSTICK_DEADZONE) {
        nextAngle++;
    }

    if (nextAngle != currentServoAngle) {
        ServoTorretta_setAngle(nextAngle);
    }
}

void ServoTorretta_setAngle(int angle) {
    if (shield == nullptr) {
        return;
    }

    // Clamp the angle within mechanical limits and command the two mirrored servos.
    currentServoAngle = constrain(angle, ELEVATION_MIN_ANGLE, ELEVATION_MAX_ANGLE);
    shield->servoPairTurn(ELEVATION_SERVO_A, ELEVATION_SERVO_B, currentServoAngle,
                          ELEVATION_MIRROR_BASE);
}

void ServoTorretta_setZero() {
    ServoTorretta_setAngle(ELEVATION_MIN_ANGLE);
}

int ServoTorretta_getAngle() {
    return currentServoAngle;
}
