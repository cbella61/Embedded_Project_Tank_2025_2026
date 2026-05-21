#ifndef UDP_SENDER_H
#define UDP_SENDER_H

#include <Arduino.h>
#include "joystickReader.h"

void UdpSender_begin();

void UdpSender_send(const ControllerData& data);

#endif