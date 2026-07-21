#include "joystickReader.h"

#define DRIVE_JOYSTICK_X_PIN 34
#define DRIVE_JOYSTICK_Y_PIN 32
#define TURRET_JOYSTICK_X_PIN 35
#define TURRET_JOYSTICK_Y_PIN 33
#define ZERO_BUTTON_PIN 25
#define FIRE_BUTTON_PIN 26
// Scale used by the tank UDP protocol.
#define JOYSTICK_CENTER 512
#define AXIS_MIN 0
#define AXIS_MAX 1023
// These deadzones filter ADC noise around the measured physical center.
// For Joy1 (drive) we use a small value so it does not add too much to the
// tank's TRACK_COMMAND_DEADZONE and make initial movement insensitive.
#define DRIVE_INPUT_DEADZONE 20
#define TURRET_INPUT_DEADZONE 80
// Number of samples used at startup to find the real joystick center.
#define CALIBRATION_SAMPLES 80
// Calibration tolerance settings.
#define CALIBRATION_MAX_CENTER_OFFSET 70
#define CALIBRATION_MAX_SPREAD 40
#define NEUTRAL_ARMING_MS 400
#define BUTTON_DEBOUNCE_MS 40
#define DRIVE_SWAP_X_Y true
#define TURRET_SWAP_X_Y true
#define DRIVE_X_INVERTED false
#define DRIVE_Y_INVERTED false
#define TURRET_X_INVERTED false
#define ELEVATION_Y_INVERTED false

static int driveXCenter = JOYSTICK_CENTER;
static int driveYCenter = JOYSTICK_CENTER;
static int turretXCenter = JOYSTICK_CENTER;
static int elevationYCenter = JOYSTICK_CENTER;
static bool calibrationValid = false;
static bool commandsArmed = false;
static unsigned long neutralSince = 0;

struct DebouncedButton {
    uint8_t pin;
    bool candidatePressed;
    bool stablePressed;
    unsigned long candidateChangedAt;
};

static DebouncedButton zeroButton = {ZERO_BUTTON_PIN, false, false, 0};
static DebouncedButton fireButton = {FIRE_BUTTON_PIN, false, false, 0};

/*
 * CONTROLLER READING METHOD
 *
 * The ESP32 reads the four analog axes with analogRead(). Each reading is
 * scaled from 0-4095 to 0-1023 so the tank receives simple values centered
 * around 512. Real joysticks rarely rest exactly at center, so the controller
 * calibrates the center on startup and applies a deadzone before sending UDP.
 */
static int readRawJoystick(int pin) {
    int rawValue = analogRead(pin);
    // ESP32 ADC reads 0-4095; the tank firmware uses 0-1023.
    return constrain(map(rawValue, 0, 4095, AXIS_MIN, AXIS_MAX), AXIS_MIN, AXIS_MAX);
}

static bool calibrateAxisCenter(int pin, int& center) {
    long sum = 0;
    int minValue = AXIS_MAX;
    int maxValue = AXIS_MIN;

    for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
        int value = readRawJoystick(pin);
        sum += value;
        minValue = min(minValue, value);
        maxValue = max(maxValue, value);
        delay(2);
    }

    center = constrain(sum / CALIBRATION_SAMPLES, AXIS_MIN, AXIS_MAX);

    bool closeToExpectedCenter = abs(center - JOYSTICK_CENTER) <= CALIBRATION_MAX_CENTER_OFFSET;
    bool stableDuringSampling = maxValue - minValue <= CALIBRATION_MAX_SPREAD;
    return closeToExpectedCenter && stableDuringSampling;
}

// Read, re-center and normalize an axis.
static int readCalibratedJoystick(int pin, int center, int inputDeadzone) {
    int raw = readRawJoystick(pin);
    int availableBelowCenter = max(center - AXIS_MIN - 1, 0);
    int availableAboveCenter = max(AXIS_MAX - center - 1, 0);
    int deadzone = constrain(inputDeadzone, 0, min(availableBelowCenter, availableAboveCenter));

    // Dead zone around the real center measured at startup.
    if (abs(raw - center) < deadzone) {
        return JOYSTICK_CENTER;
    }

    // Below center: map full travel 0 -> center to 0 -> 512.
    // Above center: map full travel center -> 1023 to 512 -> 1023.
    if (raw < center) {
        int lowerCenter = max(center - deadzone, 1);
        return constrain(map(raw, AXIS_MIN, lowerCenter, AXIS_MIN, JOYSTICK_CENTER), AXIS_MIN,
                         JOYSTICK_CENTER);
    }

    int upperCenter = min(center + deadzone, AXIS_MAX - 1);
    return constrain(map(raw, upperCenter, AXIS_MAX, JOYSTICK_CENTER, AXIS_MAX), JOYSTICK_CENTER,
                     AXIS_MAX);
}

static int invertAxisIfNeeded(int value, bool inverted) {
    value = constrain(value, AXIS_MIN, AXIS_MAX);
    if (!inverted || value == JOYSTICK_CENTER) {
        return value;
    }
    return AXIS_MAX - value;
}

static bool calibrateJoysticks() {
    Serial.println();
    Serial.println("=== ESP32 JOYSTICK CALIBRATION ===");
    Serial.println("Leave Joy1 and Joy2 centered...");
    delay(600);

    bool driveXValid = calibrateAxisCenter(DRIVE_JOYSTICK_X_PIN, driveXCenter);
    bool driveYValid = calibrateAxisCenter(DRIVE_JOYSTICK_Y_PIN, driveYCenter);
    bool turretXValid = calibrateAxisCenter(TURRET_JOYSTICK_X_PIN, turretXCenter);
    bool elevationYValid = calibrateAxisCenter(TURRET_JOYSTICK_Y_PIN, elevationYCenter);

    Serial.print("Joy1 drive center: X=");
    Serial.print(driveXCenter);
    Serial.print(" Y=");
    Serial.print(driveYCenter);
    Serial.println();

    Serial.print("Joy2 turret center: X=");
    Serial.print(turretXCenter);
    Serial.print(" Y=");
    Serial.println(elevationYCenter);
    Serial.println("From now on a steady axis will be sent as approx. 512.");
    Serial.println("===================================");
    Serial.println();

    bool valid = driveXValid && driveYValid && turretXValid && elevationYValid;
    if (!valid) {
        Serial.println("ERROR: joysticks not centered or unstable.");
        Serial.println("Commands disabled: restart with joysticks held at center.");
    }

    return valid;
}

static void beginDebouncedButton(DebouncedButton& button) {
    bool pressed = digitalRead(button.pin) == LOW;
    button.candidatePressed = pressed;
    button.stablePressed = pressed;
    button.candidateChangedAt = millis();
}

static bool readDebouncedButton(DebouncedButton& button) {
    bool rawPressed = digitalRead(button.pin) == LOW;
    unsigned long now = millis();

    if (rawPressed != button.candidatePressed) {
        button.candidatePressed = rawPressed;
        button.candidateChangedAt = now;
    }

    if (button.stablePressed != button.candidatePressed &&
        now - button.candidateChangedAt >= BUTTON_DEBOUNCE_MS) {
        button.stablePressed = button.candidatePressed;
    }

    return button.stablePressed;
}

static ControllerData safeControllerData() {
    return {JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, false, false};
}

static bool axesAreNeutral(int drivePhysicalX, int drivePhysicalY, int turretPhysicalX,
                           int turretPhysicalY) {
    return drivePhysicalX == JOYSTICK_CENTER && drivePhysicalY == JOYSTICK_CENTER &&
           turretPhysicalX == JOYSTICK_CENTER && turretPhysicalY == JOYSTICK_CENTER;
}

void JoystickReader_begin() {
    // INPUT_PULLUP avoid external resistors and allows the use of a simple switch to ground.
    pinMode(ZERO_BUTTON_PIN, INPUT_PULLUP);
    pinMode(FIRE_BUTTON_PIN, INPUT_PULLUP);

    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    beginDebouncedButton(zeroButton);
    beginDebouncedButton(fireButton);
    calibrationValid = calibrateJoysticks();
    JoystickReader_requireNeutralBeforeCommands();
}

void JoystickReader_requireNeutralBeforeCommands() {
    commandsArmed = false;
    neutralSince = 0;
}

ControllerData JoystickReader_read() {
    int drivePhysicalX =
        readCalibratedJoystick(DRIVE_JOYSTICK_X_PIN, driveXCenter, DRIVE_INPUT_DEADZONE);
    int drivePhysicalY =
        readCalibratedJoystick(DRIVE_JOYSTICK_Y_PIN, driveYCenter, DRIVE_INPUT_DEADZONE);
    int turretPhysicalX =
        readCalibratedJoystick(TURRET_JOYSTICK_X_PIN, turretXCenter, TURRET_INPUT_DEADZONE);
    int turretPhysicalY =
        readCalibratedJoystick(TURRET_JOYSTICK_Y_PIN, elevationYCenter, TURRET_INPUT_DEADZONE);
    bool zeroPressed = readDebouncedButton(zeroButton);
    bool firePressed = readDebouncedButton(fireButton);

    if (!calibrationValid) {
        return safeControllerData();
    }

    if (!commandsArmed) {
        bool neutralAndReleased =
            axesAreNeutral(drivePhysicalX, drivePhysicalY, turretPhysicalX, turretPhysicalY) &&
            !zeroPressed && !firePressed;

        if (!neutralAndReleased) {
            neutralSince = 0;
            return safeControllerData();
        }

        unsigned long now = millis();
        if (neutralSince == 0) {
            neutralSince = now;
            return safeControllerData();
        }

        if (now - neutralSince < NEUTRAL_ARMING_MS) {
            return safeControllerData();
        }

        commandsArmed = true;
        Serial.println("Joystick commands armed.");
    }

    ControllerData data;

    // Joy1 is used by the tank for differential mixing of the tracks.
    int driveX = DRIVE_SWAP_X_Y ? drivePhysicalY : drivePhysicalX;
    int driveY = DRIVE_SWAP_X_Y ? drivePhysicalX : drivePhysicalY;
    data.driveX = invertAxisIfNeeded(driveX, DRIVE_X_INVERTED);
    data.driveY = invertAxisIfNeeded(driveY, DRIVE_Y_INVERTED);

    // Joy2 is used by the tank for horizontal turret and elevation.
    int turretX = TURRET_SWAP_X_Y ? turretPhysicalY : turretPhysicalX;
    int elevationY = TURRET_SWAP_X_Y ? turretPhysicalX : turretPhysicalY;
    data.turretX = invertAxisIfNeeded(turretX, TURRET_X_INVERTED);
    data.elevationY = invertAxisIfNeeded(elevationY, ELEVATION_Y_INVERTED);

    data.zeroPressed = zeroPressed;
    data.firePressed = firePressed;

    return data;
}
