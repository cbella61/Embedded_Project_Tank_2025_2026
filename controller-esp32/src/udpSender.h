/*
 * ESP32 UDP SENDER
 *
 * This module takes data read by joystickReader and sends it to the tank.
 * The controller does not directly control motors: it only sends coordinates
 * and buttons using protocol V1.
 */

#ifndef UDP_SENDER_H
#define UDP_SENDER_H

#include <Arduino.h>

#include "joystickReader.h"

// Start the connection to the tank. If WiFi drops, the module retries without blocking the loop.
void UdpSender_begin();

// Send a ControllerData command using UDP protocol V1.
void UdpSender_send(const ControllerData& data);

#endif
