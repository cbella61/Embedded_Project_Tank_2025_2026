/*
 * ESP32 JOYSTICK READING
 *
 * This module reads the two analog joysticks and the two buttons.
 * ESP32 ADC values range 0-4095 but are converted to 0-1023 to match the
 * tank firmware scale.
 */

#ifndef JOYSTICK_READER_H
#define JOYSTICK_READER_H

#include <Arduino.h>

struct ControllerData {
    // Joy1: tank drive.
    int driveX;
    int driveY;

    // Joy2: turret and elevation.
    int turretX;
    int elevationY;

    // Digital buttons.
    bool zeroPressed;
    bool firePressed;
};

void JoystickReader_begin();

// After a reconnection or abnormal condition, inhibit commands until
// joysticks and buttons remain neutral/released for the required time.
void JoystickReader_requireNeutralBeforeCommands();

// Read joysticks and buttons. ADCs are mapped from 0-4095 to 0-1023.
ControllerData JoystickReader_read();

#endif
