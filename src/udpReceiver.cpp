#include "udpReceiver.h"

#include <WiFiS3.h>
#include <WiFiUdp.h>

const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

#define UDP_PORT 4210
#define CONNECTION_TIMEOUT_MS 500

static WiFiUDP udp;
static char packetBuffer[64];

static TankCommand lastCommand = {
    512,    // joyX al centro
    false,  // zeroPressed
    false   // connected
};

static unsigned long lastPacketTime = 0;

void UdpReceiver_begin() {
    Serial.println("Creazione Access Point...");

    int status = WiFi.beginAP(WIFI_SSID, WIFI_PASS);

    if (status != WL_AP_LISTENING) {
        Serial.println("ERRORE: impossibile creare Access Point");
        while (true);
    }

    delay(1000);

    Serial.print("Access Point creato. IP Arduino: ");
    Serial.println(WiFi.localIP());

    udp.begin(UDP_PORT);

    Serial.print("UDP in ascolto sulla porta: ");
    Serial.println(UDP_PORT);
}

TankCommand UdpReceiver_update() {
    int packetSize = udp.parsePacket();

    if (packetSize) {
        int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
        packetBuffer[len] = '\0';

        int joyX = 512;
        int zero = 0;

        sscanf(packetBuffer, "X:%d;Z:%d", &joyX, &zero);

        lastCommand.joyX = constrain(joyX, 0, 1023);
        lastCommand.zeroPressed = (zero == 1);
        lastCommand.connected = true;

        lastPacketTime = millis();
    }

    if (millis() - lastPacketTime > CONNECTION_TIMEOUT_MS) {
        lastCommand.joyX = 512;
        lastCommand.zeroPressed = false;
        lastCommand.connected = false;
    }

    return lastCommand;
}