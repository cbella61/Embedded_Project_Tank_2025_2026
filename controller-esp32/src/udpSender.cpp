#include "udpSender.h"

#include <WiFi.h>
#include <WiFiUdp.h>

/*
 * METODO DI INVIO UDP
 *
 * Il tank crea la rete WiFi. L'ESP32 si collega come client e manda pacchetti
 * UDP all'indirizzo IP del tank. Il messaggio e' una stringa compatta:
 *
 * V1;driveX;driveY;turretX;elevationY;zero;fire
 */

// Credenziali WiFi esposte dal tank Uno R4.
const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

// Deve essere uguale alla porta usata da udpReceiver.cpp sul tank.
#define UDP_PORT 4210

// Stampa coordinate una volta al secondo.
#define COORDINATE_PRINT_INTERVAL_MS 1000

// Se il WiFi cade, prova a ricollegarsi senza bloccare il loop.
#define WIFI_RECONNECT_INTERVAL_MS 3000

static WiFiUDP udp;

// IP tipico dell'access point Arduino. Se il gateway WiFi e' disponibile, viene aggiornato.
static IPAddress tankIP(192, 168, 4, 1);
static unsigned long lastCoordinatePrintTime = 0;
static unsigned long lastReconnectAttemptTime = 0;
static bool wifiWasConnected = false;

// Controlla se un IP e' 0.0.0.0, cioe' non valido.
static bool isEmptyIp(IPAddress ip) {
    return ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] == 0;
}

// Aggiorna l'indirizzo del tank e riapre UDP dopo ogni nuova connessione.
static void configureUdpConnection() {
    // Il gateway dell'access point e' l'indirizzo IP del tank.
    IPAddress gateway = WiFi.gatewayIP();
    if (!isEmptyIp(gateway)) {
        tankIP = gateway;
    }

    udp.stop();
    udp.begin(UDP_PORT);
    lastCoordinatePrintTime = millis();

    Serial.println("WiFi collegato al tank");
    Serial.print("Controller IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Tank IP: ");
    Serial.println(tankIP);
}

// Ritorna true quando il controller puo' inviare dati al tank.
// In caso di perdita WiFi, tenta la riconnessione ogni 3 secondi senza delay().
static bool ensureWifiConnected() {
    if (WiFi.status() == WL_CONNECTED) {
        if (!wifiWasConnected) {
            wifiWasConnected = true;
            configureUdpConnection();
        }

        return true;
    }

    if (wifiWasConnected) {
        wifiWasConnected = false;
        udp.stop();
        Serial.println("WiFi perso: il tank entrera' in timeout di sicurezza");
    }

    unsigned long now = millis();
    if (now - lastReconnectAttemptTime >= WIFI_RECONNECT_INTERVAL_MS) {
        lastReconnectAttemptTime = now;
        Serial.println("Tentativo di riconnessione a Tank_AP...");

        // reconnect() riusa SSID e password impostati da WiFi.begin().
        // Se non parte, begin() ricrea esplicitamente la connessione station.
        if (!WiFi.reconnect()) {
            WiFi.begin(WIFI_SSID, WIFI_PASS);
        }
    }

    return false;
}

void UdpSender_begin() {
    Serial.print("Connessione a ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.persistent(false);
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    lastReconnectAttemptTime = millis();
}

void UdpSender_send(const ControllerData& data) {
    if (!ensureWifiConnected()) {
        // Il tank fermera' i movimenti dopo il proprio timeout di 500 ms.
        return;
    }

    char message[64];

    // Protocollo finale: V1;driveX;driveY;turretX;elevationY;zero;fire
    snprintf(message, sizeof(message), "V1;%d;%d;%d;%d;%d;%d", data.driveX, data.driveY,
             data.turretX, data.elevationY, data.zeroPressed ? 1 : 0, data.firePressed ? 1 : 0);

    if (udp.beginPacket(tankIP, UDP_PORT) == 0) {
        // beginPacket() puo' fallire se la rete non e' pronta.
        return;
    }

    udp.print(message);
    udp.endPacket();

    // Stampa le coordinate una volta al secondo, non ad ogni pacchetto.
    if (millis() - lastCoordinatePrintTime > COORDINATE_PRINT_INTERVAL_MS) {
        lastCoordinatePrintTime = millis();

        Serial.println();
        Serial.println("=== ESP32 TX UDP ===");
        Serial.print("Joy1 guida    X=");
        Serial.print(data.driveX);
        Serial.print(" Y=");
        Serial.println(data.driveY);
        Serial.print("Joy2 torretta X=");
        Serial.print(data.turretX);
        Serial.print(" elevazione Y=");
        Serial.println(data.elevationY);
        Serial.print("Pulsanti      zero=");
        Serial.print(data.zeroPressed ? "PREMUTO" : "off");
        Serial.print(" fire=");
        Serial.println(data.firePressed ? "PREMUTO" : "off");
        Serial.println("===================");
    }
}
