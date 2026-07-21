/*
 * TANK UDP RECEIVER
 *
 * The tank creates a WiFi access point and receives commands in the format:
 *
 * V1;driveX;driveY;turretX;elevationY;zero;fire
 *
 * For compatibility with the initial version, parsing uses sscanf and then
 * clamps axes to the 0--1023 range.
 */

#include "udpReceiver.h"

#include <WiFiS3.h>
#include <WiFiUdp.h>

// WiFi network created by the tank.
const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

// Channel chosen after a 2.4 GHz scan: on channel 6 adjacent networks
// are noticeably weaker than Tank_AP. If the environment changes, perform
// a new scan and prefer channel 1, 6, or 11.
#define WIFI_AP_CHANNEL 6

// Shared UDP port for tank and controller.
#define UDP_PORT 4210

// After this time without valid packets the tank stops movement.
// With nominal sending every 20 ms this leaves margin for ten lost datagrams,
// but it reduces the maximum time with the last command still active.
#define CONNECTION_TIMEOUT_MS 200

// If AP or UDP socket are not ready, retry with limited frequency.
#define NETWORK_RETRY_INTERVAL_MS 3000

// Before rearming after boot, timeout, or network fault require three neutral commands.
#define REARM_NEUTRAL_PACKET_COUNT 3
#define REARM_NEUTRAL_TOLERANCE 20

// Center value for joystick axes on the 0-1023 scale.
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

// Always bring the receiver to a state that cannot command actuators.
static void disarmControls() {
    lastCommand = makeSafeCommand();
    lastPacketTime = 0;
    hasValidPacket = false;
    controlsArmed = false;
    consecutiveNeutralPackets = 0;
}

// Putting the socket into fault does not interrupt the loop: retry will be handled by millis().
static void enterNetworkFault() {
    networkState = NETWORK_FAULT;
    disarmControls();
}

// Start or restore AP and UDP. On error return false and leave a safe command.
static bool ensureNetworkReady(unsigned long now) {
    if (networkState == NETWORK_READY) {
        return true;
    }

    if (now - lastNetworkAttemptTime < NETWORK_RETRY_INTERVAL_MS) {
        return false;
    }

    Serial.println("Starting/restoring Access Point...");

    if (WiFi.beginAP(WIFI_SSID, WIFI_PASS, WIFI_AP_CHANNEL) != WL_AP_LISTENING) {
        Serial.println("ERROR: unable to create Access Point; scheduled retry");
        enterNetworkFault();
        // Timestamp dopo la chiamata: se il coprocessore ha atteso a lungo,
        // il giro successivo non deve ritentare immediatamente.
        lastNetworkAttemptTime = millis();
        return false;
    }

    if (udp.begin(UDP_PORT) == 0) {
        Serial.println("ERROR: unable to open UDP; scheduled retry");
        enterNetworkFault();
        lastNetworkAttemptTime = millis();
        return false;
    }

    networkState = NETWORK_READY;
    Serial.print("Access Point and UDP ready on channel ");
    Serial.print(WIFI_AP_CHANNEL);
    Serial.println("; awaiting neutral commands.");
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
        Serial.println("Controls rearmed after neutral position");
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
    Serial.println("Creating Access Point...");

    disarmControls();
    networkState = NETWORK_FAULT;

    // Primo tentativo immediato dal loop; gli eventuali retry restano limitati nel tempo.
    lastNetworkAttemptTime = millis() - NETWORK_RETRY_INTERVAL_MS;
}

TankCommand UdpReceiver_update() {
    unsigned long now = millis();

    // If an already active connection has timed out, immediately return the safe command.
    // Do not call parsePacket() in this loop: WiFiS3 may block internally and
    // delay braking the tracks. A hardware cutoff is still necessary against a lock
    // that happens before the firmware can detect the timeout.
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

                // Re-arming is kept separate from the parser and continues to protect boot/reconnect.
                acceptValidCommand(received, millis());
            }
        }
    }

    return currentCommandOrSafe(millis());
}
