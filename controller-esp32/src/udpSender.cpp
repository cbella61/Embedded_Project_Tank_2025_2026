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

// Un socket UDP locale fallito viene riprovato prima della reconnessione WiFi completa.
#define UDP_SOCKET_RECOVERY_INTERVAL_MS 200

// Un singolo ENOMEM di sendto() puo' essere transitorio. Il socket viene chiuso
// solo dopo piu' invii consecutivi falliti.
#define UDP_SEND_FAILURE_LIMIT 3

static WiFiUDP udp;

// IP tipico dell'access point Arduino. Se il gateway WiFi e' disponibile, viene aggiornato.
static IPAddress tankIP(192, 168, 4, 1);
static unsigned long lastCoordinatePrintTime = 0;
static unsigned long lastReconnectAttemptTime = 0;
static unsigned long lastSocketRecoveryAttemptTime = 0;
static bool wifiWasConnected = false;
static bool udpReady = false;
static bool suppressCommandAfterConnection = false;
static uint8_t consecutiveUdpSendFailures = 0;

// Controlla se un IP e' 0.0.0.0, cioe' non valido.
static bool isEmptyIp(IPAddress ip) {
    return ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] == 0;
}

static void resetUdpSendFailures() {
    consecutiveUdpSendFailures = 0;
}

// ENOMEM da endPacket() puo' essere dovuto a un buffer WiFi momentaneamente pieno.
// Non interrompiamo subito il controllo per un solo datagramma perso; dopo tre errori
// chiudiamo il socket e lo riapriamo con un retry breve, imponendo poi la neutralita'.
static void registerUdpSendFailure() {
    if (consecutiveUdpSendFailures < UDP_SEND_FAILURE_LIMIT) {
        consecutiveUdpSendFailures++;
    }

    if (consecutiveUdpSendFailures < UDP_SEND_FAILURE_LIMIT) {
        return;
    }

    udp.stop();
    udpReady = false;
    lastSocketRecoveryAttemptTime = millis();
    Serial.println("UDP TX fallito ripetutamente: recupero socket programmato");
}

// Aggiorna l'indirizzo del tank e riapre UDP dopo ogni nuova connessione.
// Un socket non aperto non viene trattato come canale di controllo operativo.
static bool configureUdpConnection() {
    // Il gateway dell'access point e' l'indirizzo IP del tank.
    IPAddress gateway = WiFi.gatewayIP();
    if (!isEmptyIp(gateway)) {
        tankIP = gateway;
    }

    udp.stop();
    udpReady = udp.begin(UDP_PORT) == 1;
    lastSocketRecoveryAttemptTime = millis();
    lastCoordinatePrintTime = millis();
    // Il pacchetto costruito prima della reconnessione potrebbe contenere un
    // pulsante premuto. Impone di nuovo neutralita' prima di trasmettere dati.
    JoystickReader_requireNeutralBeforeCommands();
    suppressCommandAfterConnection = true;

    if (!udpReady) {
        Serial.println("ERRORE: socket UDP controller non disponibile");
        return false;
    }

    resetUdpSendFailures();
    Serial.println("WiFi collegato al tank");
    Serial.print("Controller IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Tank IP: ");
    Serial.println(tankIP);
    return true;
}

// Ritorna true quando il controller puo' inviare dati al tank.
// In caso di perdita WiFi, tenta la riconnessione ogni 3 secondi senza delay().
static bool ensureWifiConnected() {
    unsigned long now = millis();

    if (WiFi.status() == WL_CONNECTED) {
        if (!wifiWasConnected) {
            wifiWasConnected = true;
            lastReconnectAttemptTime = now;
            return configureUdpConnection();
        }

        // Anche con WiFi associato, il socket puo' aver fallito localmente.
        // Il recupero UDP e' rapido; i 3 secondi restano riservati alla perdita WiFi reale.
        if (!udpReady && now - lastSocketRecoveryAttemptTime >= UDP_SOCKET_RECOVERY_INTERVAL_MS) {
            lastSocketRecoveryAttemptTime = now;
            return configureUdpConnection();
        }

        return udpReady;
    }

    if (wifiWasConnected) {
        wifiWasConnected = false;
        udpReady = false;
        resetUdpSendFailures();
        udp.stop();
        Serial.println("WiFi perso: il tank entrera' in timeout di sicurezza");
    }

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
    // Evita i ritardi del modem-sleep durante il controllo manuale.
    // Aumenta il consumo del controller, ma non sostituisce una buona alimentazione.
    WiFi.setSleep(false);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    udpReady = false;
    resetUdpSendFailures();
    lastReconnectAttemptTime = millis();
    lastSocketRecoveryAttemptTime = millis();
}

void UdpSender_send(const ControllerData& data) {
    if (!ensureWifiConnected()) {
        // Il tank fermera' i movimenti dopo il proprio timeout di 200 ms.
        return;
    }

    // Scarta il campione letto prima del cambio stato WiFi. Dal ciclo
    // successivo JoystickReader_read() restituisce solo il comando sicuro
    // finche' joystick e pulsanti non sono neutrali e rilasciati.
    if (suppressCommandAfterConnection) {
        suppressCommandAfterConnection = false;
        return;
    }

    char message[64];

    // Protocollo finale: V1;driveX;driveY;turretX;elevationY;zero;fire
    int messageLength =
        snprintf(message, sizeof(message), "V1;%d;%d;%d;%d;%d;%d", data.driveX, data.driveY,
                 data.turretX, data.elevationY, data.zeroPressed ? 1 : 0, data.firePressed ? 1 : 0);

    if (messageLength <= 0 || messageLength >= static_cast<int>(sizeof(message))) {
        Serial.println("ERRORE: pacchetto UDP controller non valido");
        return;
    }

    if (udp.beginPacket(tankIP, UDP_PORT) == 0) {
        // beginPacket() puo' fallire se la rete non e' pronta o il socket e' saturo.
        registerUdpSendFailure();
        return;
    }

    // endPacket() va comunque eseguito dopo beginPacket(), anche se una futura
    // implementazione di print() dovesse riportare una scrittura corta.
    size_t writtenBytes = udp.print(message);
    int packetSent = udp.endPacket();
    if (writtenBytes != static_cast<size_t>(messageLength) || packetSent != 1) {
        registerUdpSendFailure();
        return;
    }

    resetUdpSendFailures();
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
