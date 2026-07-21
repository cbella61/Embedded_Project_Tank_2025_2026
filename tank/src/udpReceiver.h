/*
 * TANK UDP RECEIVER
 *
 * This module creates the tank WiFi network and reads commands from the controller.
 * The main should not need to know how WiFi/UDP works: it only receives a ready-to-use TankCommand.
 */

#ifndef UDP_RECEIVER_H
#define UDP_RECEIVER_H

#include <Arduino.h>

// Full command received from the ESP32 controller.
// All axes are in the 0-1023 scale, with center around 512.
struct TankCommand {
    // Joy1: differential drive.
    int driveX;
    int driveY;

    // Joy2: horizontal turret and elevation.
    int turretX;
    int elevationY;

    // Buttons.
    bool zeroPressed;
    bool firePressed;

    // true only when valid packets are recent and neutral rearm has been completed.
    // false means no actuator should be commanded.
    bool connected;
};

// Initialize AP/UDP in disarmed state; retry waits are non-blocking and
// attempts are performed by UdpReceiver_update().
void UdpReceiver_begin();

// Legge il pacchetto piu' recente o restituisce valori sicuri se scatta il timeout.
TankCommand UdpReceiver_update();

#endif
