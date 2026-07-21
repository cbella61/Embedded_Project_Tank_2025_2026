#include "udpReceiver.h"

#include <WiFiS3.h>
#include <WiFiUdp.h>

/*
 * RICEVITORE UDP DEL TANK
 *
 * Il tank crea un access point WiFi e riceve comandi nel formato:
 *
 * V1;driveX;driveY;turretX;elevationY;zero;fire
 *
 * Per compatibilita' con la versione iniziale, il parsing usa sscanf e poi
 * limita gli assi nella scala 0--1023.
 */

// Rete WiFi creata dal tank.
const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

// Canale scelto dopo la scansione 2,4 GHz in universita': sul canale 6 le
// reti adiacenti sono sensibilmente piu' deboli di Tank_AP. Se l'ambiente
// cambia, usare una nuova scansione e scegliere preferibilmente 1, 6 oppure 11.
#define WIFI_AP_CHANNEL 6

// Porta UDP condivisa da tank e controller.
#define UDP_PORT 4210

// Dopo questo tempo senza pacchetti validi il tank ferma i movimenti.
// Con invio nominale ogni 20 ms lascia margine per dieci datagrammi persi,
// ma riduce sensibilmente il tempo massimo con l'ultimo comando attivo.
#define CONNECTION_TIMEOUT_MS 200

// Se AP o socket UDP non sono pronti, prova di nuovo con frequenza limitata.
#define NETWORK_RETRY_INTERVAL_MS 3000

// Prima di riarmare dopo boot, timeout o guasto rete richiede tre comandi neutrali.
#define REARM_NEUTRAL_PACKET_COUNT 3
#define REARM_NEUTRAL_TOLERANCE 20

// Valore centrale degli assi joystick in scala 0-1023.
#define JOYSTICK_CENTER 512

static WiFiUDP udp;

// Buffer temporaneo: viene lasciato un byte libero per il terminatore '\0'.
static char packetBuffer[64];

enum ReceiverNetworkState {
    NETWORK_FAULT,
    NETWORK_READY,
};

static ReceiverNetworkState networkState = NETWORK_FAULT;
static unsigned long lastNetworkAttemptTime = 0;

// Comando sicuro usato prima del primo pacchetto e dopo un timeout/guasto rete.
static TankCommand makeSafeCommand() {
    return {JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, false, false,
            false};
}

static TankCommand lastCommand = makeSafeCommand();
static unsigned long lastPacketTime = 0;
static bool hasValidPacket = false;
static bool controlsArmed = false;
static uint8_t consecutiveNeutralPackets = 0;

// Riporta sempre il ricevitore a uno stato che non puo' comandare attuatori.
static void disarmControls() {
    lastCommand = makeSafeCommand();
    lastPacketTime = 0;
    hasValidPacket = false;
    controlsArmed = false;
    consecutiveNeutralPackets = 0;
}

// Mettere il socket in fault non interrompe il loop: il retry verra' fatto da millis().
static void enterNetworkFault() {
    networkState = NETWORK_FAULT;
    disarmControls();
}

// Avvia o ripristina AP e UDP. In caso di errore ritorna false e lascia comando sicuro.
static bool ensureNetworkReady(unsigned long now) {
    if (networkState == NETWORK_READY) {
        return true;
    }

    if (now - lastNetworkAttemptTime < NETWORK_RETRY_INTERVAL_MS) {
        return false;
    }

    Serial.println("Avvio/ripristino Access Point...");

    if (WiFi.beginAP(WIFI_SSID, WIFI_PASS, WIFI_AP_CHANNEL) != WL_AP_LISTENING) {
        Serial.println("ERRORE: impossibile creare Access Point; retry programmato");
        enterNetworkFault();
        // Timestamp dopo la chiamata: se il coprocessore ha atteso a lungo,
        // il giro successivo non deve ritentare immediatamente.
        lastNetworkAttemptTime = millis();
        return false;
    }

    if (udp.begin(UDP_PORT) == 0) {
        Serial.println("ERRORE: impossibile aprire UDP; retry programmato");
        enterNetworkFault();
        lastNetworkAttemptTime = millis();
        return false;
    }

    networkState = NETWORK_READY;
    Serial.print("Access Point e UDP pronti sul canale ");
    Serial.print(WIFI_AP_CHANNEL);
    Serial.println("; attesa di comandi neutrali.");
    return true;
}

static bool isNeutralReleasedCommand(const TankCommand& command) {
    return abs(command.driveX - JOYSTICK_CENTER) <= REARM_NEUTRAL_TOLERANCE &&
           abs(command.driveY - JOYSTICK_CENTER) <= REARM_NEUTRAL_TOLERANCE &&
           abs(command.turretX - JOYSTICK_CENTER) <= REARM_NEUTRAL_TOLERANCE &&
           abs(command.elevationY - JOYSTICK_CENTER) <= REARM_NEUTRAL_TOLERANCE &&
           !command.zeroPressed && !command.firePressed;
}

// Un pacchetto valido rinnova il watchdog, ma puo' comandare gli attuatori solo da armato.
static void acceptValidCommand(const TankCommand& received, unsigned long now) {
    lastPacketTime = now;
    hasValidPacket = true;

    if (!controlsArmed) {
        if (!isNeutralReleasedCommand(received)) {
            consecutiveNeutralPackets = 0;
            return;
        }

        if (consecutiveNeutralPackets < REARM_NEUTRAL_PACKET_COUNT) {
            consecutiveNeutralPackets++;
        }

        if (consecutiveNeutralPackets < REARM_NEUTRAL_PACKET_COUNT) {
            return;
        }

        controlsArmed = true;
        Serial.println("Comandi riarmati dopo posizione neutra");
    }

    lastCommand = received;
    lastCommand.connected = true;
}

static bool commandTimedOut(unsigned long now) {
    return !hasValidPacket || now - lastPacketTime >= CONNECTION_TIMEOUT_MS;
}

// Un datagramma malformato non deve riattivare ne' alterare il comando precedente.
static TankCommand currentCommandOrSafe(unsigned long now) {
    if (commandTimedOut(now)) {
        disarmControls();
        return makeSafeCommand();
    }

    return controlsArmed ? lastCommand : makeSafeCommand();
}

void UdpReceiver_begin() {
    Serial.println("Creazione Access Point...");

    disarmControls();
    networkState = NETWORK_FAULT;

    // Primo tentativo immediato dal loop; gli eventuali retry restano limitati nel tempo.
    lastNetworkAttemptTime = millis() - NETWORK_RETRY_INTERVAL_MS;
}

TankCommand UdpReceiver_update() {
    unsigned long now = millis();

    // Se un collegamento gia' attivo e' scaduto, restituisci subito il comando sicuro.
    // Non chiamare parsePacket() in questo giro: WiFiS3 puo' attendere internamente e
    // ritardare il brake dei cingoli. Un cutoff hardware resta necessario contro un blocco
    // che avvenga prima che il firmware possa rilevare la scadenza.
    if (hasValidPacket && now - lastPacketTime >= CONNECTION_TIMEOUT_MS) {
        disarmControls();
        return makeSafeCommand();
    }

    if (!ensureNetworkReady(now)) {
        return makeSafeCommand();
    }

    // parsePacket() ritorna la dimensione del prossimo datagramma, oppure 0 se non ce n'e'.
    int packetSize = udp.parsePacket();

    if (packetSize > 0) {
        // Mantiene il comportamento del parser iniziale: legge al massimo 63 byte
        // e lascia sempre spazio per terminare la stringa con '\0'.
        int length = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
        if (length > 0) {
            packetBuffer[length] = '\0';

            int driveX = JOYSTICK_CENTER;
            int driveY = JOYSTICK_CENTER;
            int turretX = JOYSTICK_CENTER;
            int elevationY = JOYSTICK_CENTER;
            int zero = 0;
            int fire = 0;

            // Compatibilita' V1 originale: sei interi letti da sscanf, poi clamp degli assi.
            int parsed = sscanf(packetBuffer, "V1;%d;%d;%d;%d;%d;%d", &driveX, &driveY, &turretX,
                                &elevationY, &zero, &fire);

            if (parsed == 6) {
                TankCommand received = {
                    constrain(driveX, 0, 1023),
                    constrain(driveY, 0, 1023),
                    constrain(turretX, 0, 1023),
                    constrain(elevationY, 0, 1023),
                    zero == 1,
                    fire == 1,
                    false,
                };

                // Il riarmo resta separato dal parser e continua a proteggere boot/reconnect.
                acceptValidCommand(received, millis());
            }
        }
    }

    return currentCommandOrSafe(millis());
}
