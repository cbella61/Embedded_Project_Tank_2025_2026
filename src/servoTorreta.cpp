#include "servoTorreta.h"   
#define MAX_ANGLE 180
#define MIN_ANGLE -180

// 180° corrispondono a metà giro
#define MAX_STEPS ((STEPS_PER_REV * MAX_ANGLE) / 360)
#define MIN_STEPS ((STEPS_PER_REV * MIN_ANGLE) / 360)

// Joystick analogico: circa 0-1023
#define JOYSTICK_CENTER 512
#define JOYSTICK_DEADZONE 200

// Velocità dello stepper
// Più piccolo = più veloce
#define STEP_INTERVAL_MS 2

static int currentSteps = 0;
static int stepIndex = 0;
static unsigned long lastStepTime = 0;

static void writeStep(int index) {
    switch (index) {
        case 0:
            digitalWrite(IN1, HIGH);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;

        case 1:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, HIGH);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;

        case 2:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, HIGH);
            digitalWrite(IN4, LOW);
            break;

        case 3:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, HIGH);
            break;
    }
}

static void stepRight() {
    if (currentSteps >= MAX_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex++;
    if (stepIndex > 3) {
        stepIndex = 0;
    }

    writeStep(stepIndex);
    currentSteps++;
}

static void stepLeft() {
    if (currentSteps <= MIN_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex--;
    if (stepIndex < 0) {
        stepIndex = 3;
    }

    writeStep(stepIndex);
    currentSteps--;
}

void StepperTorretta_begin() {
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);

    StepperTorretta_stop();

    currentSteps = 0;
    stepIndex = 0;
}

void StepperTorretta_updateJoystick(int joystickValue) {
    unsigned long now = millis();

    if (now - lastStepTime < STEP_INTERVAL_MS) {
        return;
    }

    lastStepTime = now;

    if (joystickValue < JOYSTICK_CENTER - JOYSTICK_DEADZONE) {
        stepLeft();
    }
    else if (joystickValue > JOYSTICK_CENTER + JOYSTICK_DEADZONE) {
        stepRight();
    }
    else {
        StepperTorretta_stop();
    }
}

void StepperTorretta_setZero() {
    currentSteps = 0;
}

void StepperTorretta_stop() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

int StepperTorretta_getAngle() {
    return (currentSteps * 360L) / STEPS_PER_REV;
}

