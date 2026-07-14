#include <Arduino.h>

#include "joystickReader.h"
#include "udpSender.h"

/*
 * MAIN DEL CONTROLLER ESP32
 *
 * Metodo di funzionamento:
 * 1. Configura joystick/pulsanti.
 * 2. Si collega alla rete WiFi creata dal tank.
 * 3. Ogni 10 ms legge gli ingressi e invia un pacchetto UDP al tank.
 * 4. Se perde il WiFi, continua il loop e tenta automaticamente la riconnessione.
 */

// 10 ms = circa 100 pacchetti al secondo.
// Abbassare troppo questo valore puo' intasare il WiFi senza migliorare molto.
#define UDP_SEND_INTERVAL_MS 10

static unsigned long lastUdpSendTime = 0;

void setup() {
    Serial.begin(115200);

    // Configura gli ingressi prima di collegarsi alla rete del tank.
    JoystickReader_begin();
    UdpSender_begin();

    Serial.println("Controller pronto");
}

void loop() {
    unsigned long now = millis();
    if (now - lastUdpSendTime < UDP_SEND_INTERVAL_MS) {
        return;
    }
    lastUdpSendTime = now;

    // Legge joystick/pulsanti e invia un comando UDP ogni 10 ms.
    ControllerData data = JoystickReader_read();
    UdpSender_send(data);
}
