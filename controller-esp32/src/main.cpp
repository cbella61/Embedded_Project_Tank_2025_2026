#include <Arduino.h>

#include "joystickReader.h"
#include "udpSender.h"

void setup() {
    Serial.begin(115200);

    JoystickReader_begin();
    UdpSender_begin();

    Serial.println("Controller pronto");
}

void loop() {
    ControllerData data = JoystickReader_read();

    UdpSender_send(data);

    delay(30);
}