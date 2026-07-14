#include "udpReceiver.h"

#include <WiFiS3.h>
#include <WiFiUdp.h>

/*
 * METODO DI FUNZIONAMENTO UDP SUL TANK
 *
 * Il tank fa da access point WiFi. Il controller ESP32 si collega a questa rete
 * e manda pacchetti UDP nel formato:
 *
 * V1;driveX;driveY;turretX;elevationY;zero;fire
 *
 * La funzione UdpReceiver_update() non blocca il programma: controlla se c'e'
 * un pacchetto, aggiorna lastCommand se il pacchetto e' valido, poi ritorna
 * sempre un comando. Se non arrivano pacchetti per 500 ms, ritorna un comando
 * sicuro con joystick al centro e connected=false.
 */

// Rete WiFi creata dal tank.
const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

// Porta UDP condivisa da tank e controller.
#define UDP_PORT 4210

// Dopo questo tempo senza pacchetti il tank ferma i movimenti.
#define CONNECTION_TIMEOUT_MS 500

// Valore centrale degli assi joystick in scala 0-1023.
#define JOYSTICK_CENTER 512

static WiFiUDP udp;

// Buffer temporaneo dove viene letta la stringa UDP.
static char packetBuffer[64];

// Comando sicuro usato prima del primo pacchetto e dopo un timeout.
static TankCommand lastCommand = {
    JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, false, false, false};

// Ultimo momento in cui e' arrivato un pacchetto valido.
static unsigned long lastPacketTime = 0;

void UdpReceiver_begin() {
    Serial.println("Creazione Access Point...");

    // Se l'access point non parte, il tank non puo' essere controllato.
    if (WiFi.beginAP(WIFI_SSID, WIFI_PASS) != WL_AP_LISTENING) {
        Serial.println("ERRORE: impossibile creare Access Point");
        while (true) {
        }
    }

    delay(1000);
    udp.begin(UDP_PORT);

    // Normalmente l'IP sara' 192.168.4.1.
    Serial.print("Tank IP: ");
    Serial.println(WiFi.localIP());
}

TankCommand UdpReceiver_update() {
    // parsePacket() ritorna 0 se non c'e' nessun pacchetto nuovo.
    int packetSize = udp.parsePacket();

    if (packetSize > 0) {
        // Lascia sempre un byte libero per terminare la stringa con '\0'.
        int length = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
        if (length > 0) {
            packetBuffer[length] = '\0';

            // Valori di fallback: se qualcosa non viene letto bene, resta al centro.
            int driveX = JOYSTICK_CENTER;
            int driveY = JOYSTICK_CENTER;
            int turretX = JOYSTICK_CENTER;
            int elevationY = JOYSTICK_CENTER;
            int zero = 0;
            int fire = 0;

            // Protocollo finale: V1;driveX;driveY;turretX;elevationY;zero;fire
            int parsed = sscanf(packetBuffer, "V1;%d;%d;%d;%d;%d;%d", &driveX, &driveY, &turretX,
                                &elevationY, &zero, &fire);

            if (parsed == 6) {
                // Salva solo valori validi e limitati tra 0 e 1023.
                lastCommand.driveX = constrain(driveX, 0, 1023);
                lastCommand.driveY = constrain(driveY, 0, 1023);
                lastCommand.turretX = constrain(turretX, 0, 1023);
                lastCommand.elevationY = constrain(elevationY, 0, 1023);
                lastCommand.zeroPressed = zero == 1;
                lastCommand.firePressed = fire == 1;
                lastCommand.connected = true;

                // Questo resetta il timer del timeout connessione.
                lastPacketTime = millis();
            }
        }
    }

    // Se il controller smette di trasmettere, il comando diventa sicuro.
    if (millis() - lastPacketTime > CONNECTION_TIMEOUT_MS) {
        lastCommand.driveX = JOYSTICK_CENTER;
        lastCommand.driveY = JOYSTICK_CENTER;
        lastCommand.turretX = JOYSTICK_CENTER;
        lastCommand.elevationY = JOYSTICK_CENTER;
        lastCommand.zeroPressed = false;
        lastCommand.firePressed = false;
        lastCommand.connected = false;
    }

    return lastCommand;
}
