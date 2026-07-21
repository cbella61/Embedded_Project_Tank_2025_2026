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

// WiFi.begin() e' asincrona: in un ambiente radio affollato associazione e DHCP
// possono richiedere vari secondi. Non interrompere un tentativo gia' in corso
// prima di questo limite.
#define WIFI_CONNECTION_ATTEMPT_TIMEOUT_MS 10000

// Solo un socket che non riesce ad aprirsi viene riprovato. L'attesa evita
// allocazioni e bind ripetuti mentre la memoria di rete e' sotto pressione.
#define UDP_SOCKET_RECOVERY_INTERVAL_MS 1000

// Un singolo ENOMEM di sendto() puo' essere transitorio. Dopo piu' invii
// consecutivi falliti si sospende brevemente il TX, ma non si ricrea il socket.
#define UDP_SEND_FAILURE_LIMIT 3
#define UDP_TX_FAULT_BACKOFF_MS 100

static WiFiUDP udp;

// IP tipico dell'access point Arduino. Se il gateway WiFi e' disponibile, viene aggiornato.
static IPAddress tankIP(192, 168, 4, 1);
static unsigned long lastCoordinatePrintTime = 0;
static unsigned long lastWifiConnectionStartTime = 0;
static unsigned long lastSocketRecoveryAttemptTime = 0;
static bool wifiWasConnected = false;
static bool udpReady = false;
static bool suppressCommandAfterConnection = false;
static uint8_t consecutiveUdpSendFailures = 0;
static unsigned long lastUdpSendFailureTime = 0;
static bool udpFaultReported = false;

// Controlla se un IP e' 0.0.0.0, cioe' non valido.
static bool isEmptyIp(IPAddress ip) {
    return ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] == 0;
}

static void resetUdpSendFailures() {
    consecutiveUdpSendFailures = 0;
    udpFaultReported = false;
}

// Il confronto con sottrazione unsigned resta corretto anche al wrap di millis().
static bool udpTxBackoffActive(unsigned long now) {
    return consecutiveUdpSendFailures >= UDP_SEND_FAILURE_LIMIT &&
           now - lastUdpSendFailureTime < UDP_TX_FAULT_BACKOFF_MS;
}

static const char* wifiStatusName(wl_status_t status) {
    switch (status) {
        case WL_IDLE_STATUS:
            return "IDLE";
        case WL_NO_SSID_AVAIL:
            return "SSID_NON_TROVATO";
        case WL_SCAN_COMPLETED:
            return "SCAN_COMPLETATO";
        case WL_CONNECTED:
            return "COLLEGATO";
        case WL_CONNECT_FAILED:
            return "CONNESSIONE_FALLITA";
        case WL_CONNECTION_LOST:
            return "CONNESSIONE_PERSA";
        case WL_DISCONNECTED:
            return "DISCONNESSO";
        default:
            return "STATO_SCONOSCIUTO";
    }
}

// Avvia un solo tentativo WiFi controllato. Il reset esplicito e' usato solo
// dopo che il tentativo precedente ha avuto 10 s per completare, oppure dopo
// una perdita di collegamento gia' confermata da WiFi.status().
static void startWifiConnectionAttempt(unsigned long now, bool resetConnection) {
    lastWifiConnectionStartTime = now;

    if (resetConnection) {
        // Non cancella le credenziali memorizzate in RAM; prepara una nuova
        // associazione senza attendere in modo bloccante.
        WiFi.disconnect(false, false);
    }

    WiFi.begin(WIFI_SSID, WIFI_PASS);
}

// ENOMEM da endPacket() indica che sendto() non puo' accodare il datagramma nella
// pila WiFi/lwIP. Chiudere e riaprire il socket qui richiederebbe una nuova
// allocazione del buffer UDP da 1460 byte, peggiorando proprio questa condizione.
static void registerUdpSendFailure() {
    if (consecutiveUdpSendFailures < UDP_SEND_FAILURE_LIMIT) {
        consecutiveUdpSendFailures++;
    }

    lastUdpSendFailureTime = millis();

    if (consecutiveUdpSendFailures == UDP_SEND_FAILURE_LIMIT && !udpFaultReported) {
        udpFaultReported = true;
        Serial.println("UDP TX temporaneamente saturo: pausa di recupero programmata");
    }
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
// In caso di perdita WiFi usa un solo retry controllato, senza delay().
static bool ensureWifiConnected() {
    unsigned long now = millis();

    if (WiFi.status() == WL_CONNECTED) {
        if (!wifiWasConnected) {
            wifiWasConnected = true;
            return configureUdpConnection();
        }

        // Anche con WiFi associato, l'apertura iniziale del socket puo' fallire.
        // Gli errori ENOMEM di invio, invece, vengono gestiti senza ricrearlo.
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

        // Dopo una connessione realmente attiva si puo' iniziare subito un
        // nuovo tentativo; il successivo reset e' comunque ritardato di 10 s.
        startWifiConnectionAttempt(now, true);
        return false;
    }

    if (now - lastWifiConnectionStartTime >= WIFI_CONNECTION_ATTEMPT_TIMEOUT_MS) {
        Serial.print("Nuovo tentativo WiFi controllato a Tank_AP (stato: ");
        Serial.print(wifiStatusName(WiFi.status()));
        Serial.println(")...");

        // WiFi.reconnect() forza una disconnessione ad ogni chiamata. Non lo
        // usiamo qui: ogni tentativo riceve prima il tempo necessario per
        // completare associazione e DHCP anche in presenza di molta congestione.
        startWifiConnectionAttempt(now, true);
    }

    return false;
}

void UdpSender_begin() {
    Serial.print("Connessione a ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.persistent(false);
    // Il firmware gestisce i retry per non sovrapporsi al reconnect automatico
    // del core ESP32, che potrebbe interrompere una connessione in corso.
    WiFi.setAutoReconnect(false);
    // Evita i ritardi del modem-sleep durante il controllo manuale.
    // Aumenta il consumo del controller, ma non sostituisce una buona alimentazione.
    WiFi.setSleep(false);
    startWifiConnectionAttempt(millis(), false);
    udpReady = false;
    resetUdpSendFailures();
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

    // Dopo tre ENOMEM consecutivi lascia tempo alla coda WiFi per svuotarsi.
    // Se la radio non recupera, il timeout indipendente del tank ferma il mezzo.
    if (udpTxBackoffActive(millis())) {
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
