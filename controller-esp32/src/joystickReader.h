#ifndef JOYSTICK_READER_H
#define JOYSTICK_READER_H

#include <Arduino.h>

struct ControllerData {
    int joyY;
    int joyX;
    bool zeroPressed;
};

void JoystickReader_begin();

ControllerData JoystickReader_read();

#endif