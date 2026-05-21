#include "udpSender.h"

#include <WiFi.h>
#include <WiFiUdp.h>

const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

IPAddress tankIP(192, 168, 4, 1);

#define UDP_PORT 4210

static WiFiUDP udp;

void UdpSender_begin() {
    Serial.print("Connessione a ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("ESP32 connesso al tank");

    Serial.print("IP ESP32: ");
    Serial.println(WiFi.localIP());
}

void UdpSender_send(const ControllerData& data) {
    char message[64];

    sprintf(message, "X:%d;Y:%d;Z:%d",
            data.joyX,
            data.joyY,
            data.zeroPressed ? 1 : 0);

    udp.beginPacket(tankIP, UDP_PORT);
    udp.print(message);
    udp.endPacket();

    Serial.println(message);
}