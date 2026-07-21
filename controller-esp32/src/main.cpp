#include <Arduino.h>

#include "joystickReader.h"
#include "udpSender.h"

/*
 * ESP32 CONTROLLER MAIN
 *
 * Operation method:
 * 1. Configure joysticks/buttons.
 * 2. Connect to the WiFi network created by the tank.
 * 3. Every 50 ms read inputs and send a UDP packet to the tank.
 * 4. If WiFi is lost, continue the loop and automatically attempt reconnection.
 */

#define UDP_SEND_INTERVAL_MS 50

static unsigned long lastUdpSendTime = 0;

void setup() {
    Serial.begin(115200);

    // Configure inputs before connecting to the tank network.
    JoystickReader_begin();
    UdpSender_begin();

    Serial.println("Controller ready");
}

void loop() {
    unsigned long now = millis();
    if (now - lastUdpSendTime < UDP_SEND_INTERVAL_MS) {
        return;
    }
    lastUdpSendTime = now;

    // Read joysticks/buttons and send a UDP command every 50 ms.
    ControllerData data = JoystickReader_read();
    UdpSender_send(data);
}
