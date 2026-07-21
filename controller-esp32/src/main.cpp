#include <Arduino.h>

#include "joystickReader.h"
#include "udpSender.h"

/*
 * MAIN DEL CONTROLLER ESP32
 *
 * Metodo di funzionamento:
 * 1. Configura joystick/pulsanti.
 * 2. Si collega alla rete WiFi creata dal tank.
 * 3. Ogni 50 ms legge gli ingressi e invia un pacchetto UDP al tank.
 * 4. Se perde il WiFi, continua il loop e tenta automaticamente la riconnessione.
 */

// 50 ms = 20 pacchetti al secondo. Riduce la pressione sui buffer WiFi e
// lascia quattro opportunita' di ricezione entro il timeout del tank di 200 ms.
#define UDP_SEND_INTERVAL_MS 50

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

    // Legge joystick/pulsanti e invia un comando UDP ogni 50 ms.
    ControllerData data = JoystickReader_read();
    UdpSender_send(data);
}
