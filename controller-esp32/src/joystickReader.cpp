#include "joystickReader.h"

#define JOYSTICK_Y_PIN 35
#define JOYSTICK_X_PIN 34
#define ZERO_BUTTON_PIN 25

void JoystickReader_begin() {
    pinMode(ZERO_BUTTON_PIN, INPUT_PULLUP);
}

ControllerData JoystickReader_read() {
    ControllerData data;

    int rawX = analogRead(JOYSTICK_X_PIN);
    int rawY = analogRead(JOYSTICK_Y_PIN);
    // ESP32 legge 0-4095.
    // Arduino R4 riceve 0-1023.
    data.joyX = map(rawX, 0, 4095, 0, 1023);
    data.joyY = map(rawY, 0, 4095, 0, 1023);

    data.zeroPressed = (digitalRead(ZERO_BUTTON_PIN) == LOW);

    return data;
}
