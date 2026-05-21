#ifndef UDP_RECEIVER_H
#define UDP_RECEIVER_H

#include <Arduino.h>

struct TankCommand {
    int joyX;
    int joyY;
    bool zeroPressed;
    bool connected;
};

void UdpReceiver_begin();

TankCommand UdpReceiver_update();

#endif