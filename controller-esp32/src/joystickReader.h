#ifndef JOYSTICK_READER_H
#define JOYSTICK_READER_H

#include <Arduino.h>

/*
 * LETTURA JOYSTICK ESP32
 *
 * Questo modulo legge i due joystick analogici e i due pulsanti.
 * I valori analogici dell'ESP32 vanno da 0 a 4095, ma vengono convertiti
 * in 0-1023 per usare la stessa scala del firmware tank.
 */

// Ingressi letti dall'ESP32 e spediti al tank via UDP.
struct ControllerData {
    // Joy1: guida del tank.
    int driveX;
    int driveY;

    // Joy2: torretta ed elevazione.
    int turretX;
    int elevationY;

    // Pulsanti digitali.
    bool zeroPressed;
    bool firePressed;
};

// Configura i due pulsanti.
void JoystickReader_begin();

// Dopo una reconnessione o una condizione anomala, inibisce i comandi finche'
// joystick e pulsanti non restano neutrali/rilasciati per il tempo previsto.
void JoystickReader_requireNeutralBeforeCommands();

// Legge joystick e pulsanti. Gli ADC vengono mappati da 0-4095 a 0-1023.
ControllerData JoystickReader_read();

#endif
