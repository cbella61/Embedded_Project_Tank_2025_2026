/*
 * DC TRACKS OPERATION METHOD
 *
 * Each yellow motor has only two wires. The shield provides:
 * - direction: forward or backward
 * - speed: PWM from the configured minimum to maximum per track
 *
 * The code no longer uses stepper phases. It now simply sends PWM to motors
 * M1 and M3, with differential mixing to steer like a tank.
 */

#include "trackController.h"

// Puntatore al driver PWM ricevuto dal main in TrackController_begin().
static MotorController* motorController = nullptr;

// Before reversing a track, firmware applies a short pause at zero PWM.
// The value must be validated on the real driver: it's a software improvement,
// not a replacement for a hardware cutoff in case of I2C bus failure.
#define TRACK_REVERSE_DEAD_TIME_MS 30

// La deadzone deve lasciare almeno un comando positivo e uno negativo disponibili.
static_assert(TRACK_COMMAND_DEADZONE > 0 && TRACK_COMMAND_DEADZONE < DRIVE_JOYSTICK_CENTER,
              "TRACK_COMMAND_DEADZONE must stay inside the joystick range");

struct TrackMotorState {
    // Last direction passed to DCRun(). It's a software request, not a motor measurement.
    int lastRequestedDirection;
    // Last direction before DCbrake(). It remains stored even if the joystick
    // returns to center, so an immediate reversal still respects the pause time.
    int directionBeforeStop;
    int pendingDirection;
    int pendingSpeed;
    bool waitingForReverse;
    unsigned long stoppedAt;
};

static TrackMotorState leftTrackState = {0, 0, 0, 0, false, 0};
static TrackMotorState rightTrackState = {0, 0, 0, 0, false, 0};

// Avoid constantly rewriting the same four I2C registers while the joystick is
// still. Periodic refresh still preserves the shield health control; a stop
// bypasses this limitation.
static int lastDriveX = DRIVE_JOYSTICK_CENTER;
static int lastDriveY = DRIVE_JOYSTICK_CENTER;
static bool hasLastDriveCommand = false;
static unsigned long lastTrackCommandTime = 0;
static bool stopCommandIssued = false;
static unsigned long lastStopCommandTime = 0;

static TrackMotorState* stateForTrackMotor(int motorNumber) {
    if (motorNumber == LEFT_TRACK_MOTOR) {
        return &leftTrackState;
    }

    if (motorNumber == RIGHT_TRACK_MOTOR) {
        return &rightTrackState;
    }

    return nullptr;
}

// Decode a UDP axis 0--1023 into a signed command centered on zero.
// Example: 512 becomes 0, 1023 becomes about +511, 0 becomes -512.
// Axis inversion is the responsibility of the ESP32 controller, not the tank.
static int decodeDriveAxis(int value) {
    int centered = constrain(value, 0, 1023) - DRIVE_JOYSTICK_CENTER;

    // Primo filtro lato tank: protegge anche da sender UDP diversi dall'ESP32.
    // Il filtro finale di applyTrackMotorCommand() resta necessario dopo forward +/- turn.
    if (abs(centered) < TRACK_COMMAND_DEADZONE) {
        centered = 0;
    }

    return centered;
}

// Bring a track to zero PWM and cancel any pending reversal.
static void stopTrackMotor(int motorNumber) {
    if (motorController == nullptr) {
        return;
    }

    TrackMotorState* state = stateForTrackMotor(motorNumber);
    motorController->DCbrake(motorNumber);

    if (state != nullptr) {
            // Do not clear directionBeforeStop: it is used if after center the opposite
            // direction is requested.
        if (state->lastRequestedDirection != 0) {
            state->directionBeforeStop = state->lastRequestedDirection;
            state->stoppedAt = millis();
        }

        state->lastRequestedDirection = 0;
        state->pendingDirection = 0;
        state->pendingSpeed = 0;
        state->waitingForReverse = false;
    }
}

// Map forward/backward linearly: Joy1 Y must be able to reach maximum.
static int mapLinearTrackSpeed(int magnitude, int minPwm, int maxPwm) {
    int fullMagnitude = DRIVE_JOYSTICK_CENTER - 1;
    int limitedMagnitude = constrain(magnitude, TRACK_COMMAND_DEADZONE, fullMagnitude);

    return map(limitedMagnitude, TRACK_COMMAND_DEADZONE, fullMagnitude, minPwm, maxPwm);
}

// Apply a signed command to a track, including PWM and safe reversal pause.
static void applyTrackMotorCommand(int motorNumber, bool inverted, int command, int minPwm,
                                   int maxPwm, int pwmPercent) {
    if (motorController == nullptr) {
        return;
    }

    TrackMotorState* state = stateForTrackMotor(motorNumber);
    if (state == nullptr) {
        return;
    }

    command = constrain(command, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    minPwm = constrain(minPwm, 0, MAX_SPEED);
    maxPwm = constrain(maxPwm, minPwm, MAX_SPEED);
    pwmPercent = constrain(pwmPercent, 0, 150);

    // Second tank-side filter: mixing can leave a single track small even when
    // forward and turn were both outside their individual deadzones.
    if (abs(command) < TRACK_COMMAND_DEADZONE) {
        stopTrackMotor(motorNumber);
        return;
    }

    int magnitude = abs(command);

    // Forward/backward and the final motor command remain linear.
    int speed = mapLinearTrackSpeed(magnitude, minPwm, maxPwm);
    speed = constrain(static_cast<int>((static_cast<long>(speed) * pwmPercent) / 100), 0, MAX_SPEED);

    int direction = command > 0 ? FORWARD : BACKWARD;
    if (inverted) {
        direction = direction == FORWARD ? BACKWARD : FORWARD;
    }

    unsigned long now = millis();

    // During the reversal pause keep only the last command, without re-enabling
    // the H-bridge before the minimum time has passed.
    if (state->waitingForReverse) {
        state->pendingDirection = direction;
        state->pendingSpeed = speed;

        if (now - state->stoppedAt < TRACK_REVERSE_DEAD_TIME_MS) {
            return;
        }

        motorController->DCrun(motorNumber, state->pendingDirection, state->pendingSpeed);
        state->lastRequestedDirection = state->pendingDirection;
        state->directionBeforeStop = state->pendingDirection;
        state->waitingForReverse = false;
        return;
    }

    // Do not invert a running motor directly: brake, wait and then reapply.
    if (state->lastRequestedDirection != 0 && state->lastRequestedDirection != direction) {
        motorController->DCbrake(motorNumber);
        state->directionBeforeStop = state->lastRequestedDirection;
        state->lastRequestedDirection = 0;
        state->pendingDirection = direction;
        state->pendingSpeed = speed;
        state->waitingForReverse = true;
        state->stoppedAt = now;
        return;
    }

    // If it has already been stopped, the center -> opposite direction path must
    // also wait. Without this check the old code could bypass the 30 ms after center.
    if (state->lastRequestedDirection == 0 && state->directionBeforeStop != 0 &&
        state->directionBeforeStop != direction &&
        now - state->stoppedAt < TRACK_REVERSE_DEAD_TIME_MS) {
        state->pendingDirection = direction;
        state->pendingSpeed = speed;
        state->waitingForReverse = true;
        return;
    }

    // The command is updated at controlled intervals even if unchanged:
    // do not perform permanent caching, otherwise a bus failure could remain
    // invisible to the shield health check.
    motorController->DCrun(motorNumber, direction, speed);
    state->lastRequestedDirection = direction;
    state->directionBeforeStop = direction;
}

void TrackController_begin(MotorController& controller) {
    // Store the reference to the shield initialized by main.
    motorController = &controller;
    hasLastDriveCommand = false;
    stopCommandIssued = false;

    // Always start with both tracks stopped.
    TrackController_stop();
}

void TrackController_update(int driveX, int driveY) {
    unsigned long now = millis();
    driveX = constrain(driveX, 0, 1023);
    driveY = constrain(driveY, 0, 1023);

    bool commandChanged =
        !hasLastDriveCommand || driveX != lastDriveX || driveY != lastDriveY;
    if (!commandChanged && now - lastTrackCommandTime < TRACK_COMMAND_REFRESH_INTERVAL_MS) {
        return;
    }

    lastDriveX = driveX;
    lastDriveY = driveY;
    hasLastDriveCommand = true;
    lastTrackCommandTime = now;
    stopCommandIssued = false;

    // Joy1 Y: forward/backward. Joy1 X: steering.
    int forward = decodeDriveAxis(driveY);
    int turn = decodeDriveAxis(driveX);

    // Differential mixing:
    // - straight forward: both motors run the same
    // - steering: one side speeds up and the other slows down
    // - only X: one motor forward and one backward, so it spins in place
    int leftCommand = constrain(forward + turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    int rightCommand = constrain(forward - turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);

    applyTrackMotorCommand(LEFT_TRACK_MOTOR, LEFT_TRACK_INVERTED, leftCommand, LEFT_TRACK_MIN_PWM,
                           LEFT_TRACK_MAX_PWM, LEFT_TRACK_PWM_PERCENT);
    applyTrackMotorCommand(RIGHT_TRACK_MOTOR, RIGHT_TRACK_INVERTED, rightCommand,
                           RIGHT_TRACK_MIN_PWM, RIGHT_TRACK_MAX_PWM, RIGHT_TRACK_PWM_PERCENT);
}

void TrackController_stop() {
    unsigned long now = millis();
    if (stopCommandIssued && now - lastStopCommandTime < TRACK_COMMAND_REFRESH_INTERVAL_MS) {
        return;
    }

    stopTrackMotor(LEFT_TRACK_MOTOR);
    stopTrackMotor(RIGHT_TRACK_MOTOR);
    hasLastDriveCommand = false;
    stopCommandIssued = true;
    lastStopCommandTime = now;
}
