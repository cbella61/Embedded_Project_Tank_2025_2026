#include <Arduino.h>
#include <Wire.h>

#include "motorController.h"
#include "servoTorreta.h"
#include "trackController.h"
#include "udpReceiver.h"

/*
 * MAIN DEL TANK
 *
 * Questo file non fa direttamente tutti i movimenti: coordina i moduli.
 *
 * Metodo di funzionamento:
 * 1. In setup() inizializza relay, torretta, shield PCA9685 e ricevitore UDP.
 * 2. In loop() legge l'ultimo comando arrivato dal controller ESP32.
 * 3. Passa ogni parte del comando al modulo giusto:
 *    - driveX/driveY     -> cingoli differenziali
 *    - turretX           -> torretta orizzontale D2-D5
 *    - elevationY        -> servo S5/S6
 *    - firePressed       -> relay D7
 *    - zeroPressed       -> azzeramento logico
 * 4. Se il controller non manda pacchetti per troppo tempo, ferma i motori.
 */

// ===== CONFIGURAZIONE RELAY SPARO =====

// Pin digitale collegato al modulo relay.
#define FIRE_RELAY_PIN 7

// true: relay acceso con HIGH. false: relay acceso con LOW.
#define FIRE_RELAY_ACTIVE_HIGH true

// Durata dell'impulso di sparo: il relay non resta acceso fisso.
#define FIRE_RELAY_PULSE_MS 200

// Tempo minimo tra un colpo e quello successivo.
#define FIRE_RELAY_COOLDOWN_MS 12000

// ===== MONITOR SERIALE =====

// Stampa le coordinate una volta al secondo per non riempire la console.
#define COORDINATE_PRINT_INTERVAL_MS 1000

// Shield PCA9685 condivisa da cingoli e servo di elevazione.
// La frequenza e' 50 Hz perche' e' compatibile con i servo.
static MotorController shield(50);

// Diventa true solo se la PCA9685 viene trovata su I2C.
static bool shieldReady = false;
static bool shieldFaultReported = false;

// Stato del relay sparo.
static bool fireRelayActive = false;
static unsigned long fireRelayStartTime = 0;
static unsigned long lastFireShotTime = 0;
static bool fireRelayHasShot = false;

// Verifica se un dispositivo risponde a un indirizzo I2C.
static bool i2cDevicePresent(uint8_t address) {
    Wire.beginTransmission(address);
    return Wire.endTransmission() == 0;
}

// Seleziona automaticamente l'indirizzo della PCA9685 della shield.
// Alcune shield usano indirizzi diversi, quindi il codice prova i piu' comuni.
static bool configureShieldAddress() {
    static const uint8_t candidateAddresses[] = {0x60, 0x40, 0x7F};

    for (uint8_t address : candidateAddresses) {
        if (i2cDevicePresent(address)) {
            shield.setAddress(address);
            Serial.print("Shield PCA9685: I2C 0x");
            Serial.println(address, HEX);
            return true;
        }
    }

    Serial.println("ERRORE: PCA9685 shield non rilevata");
    return false;
}

// Imposta il livello elettrico corretto per il relay sparo.
static void setFireRelay(bool active) {
    int level =
        active ? (FIRE_RELAY_ACTIVE_HIGH ? HIGH : LOW) : (FIRE_RELAY_ACTIVE_HIGH ? LOW : HIGH);

    digitalWrite(FIRE_RELAY_PIN, level);
    fireRelayActive = active;
}

// Genera un solo impulso di sparo per ogni pressione del pulsante.
// Usa il fronte di salita e poi aspetta 12 secondi prima di accettare un altro colpo.
static void updateFireRelay(bool firePressed, bool connected) {
    static bool lastFirePressed = false;
    static bool fireInputArmed = false;

    // Dopo timeout o perdita del collegamento il relay deve spegnersi subito.
    // Il successivo collegamento non puo' riutilizzare una pressione rimasta attiva:
    // prima va osservato il rilascio del pulsante Fire.
    if (!connected) {
        setFireRelay(false);
        fireInputArmed = false;
        lastFirePressed = false;
        return;
    }

    if (!fireInputArmed) {
        if (!firePressed) {
            fireInputArmed = true;
        }

        // Memorizza comunque il livello ricevuto: quando Fire e' tenuto premuto
        // alla reconnessione non verra' interpretato come fronte di salita.
        lastFirePressed = firePressed;
        return;
    }

    bool newFirePress = firePressed && !lastFirePressed;
    bool cooldownFinished =
        !fireRelayHasShot || millis() - lastFireShotTime >= FIRE_RELAY_COOLDOWN_MS;

    if (newFirePress && cooldownFinished) {
        setFireRelay(true);
        fireRelayStartTime = millis();
        lastFireShotTime = fireRelayStartTime;
        fireRelayHasShot = true;
    }

    if (fireRelayActive && millis() - fireRelayStartTime >= FIRE_RELAY_PULSE_MS) {
        setFireRelay(false);
    }

    lastFirePressed = firePressed;
}

// Ferma ogni movimento in caso di timeout UDP.
// I cingoli dipendono dalla shield; la torretta D2-D5 invece puo' essere fermata sempre.
static void stopAllMotion() {
    // TrackController_stop() e' innocua prima dell'inizializzazione e va tentata anche
    // dopo un fault I2C: una PCA9685 che ha conservato l'ultimo PWM puo' essere tornata
    // raggiungibile per un istante. Il controller limita internamente i retry di brake.
    TrackController_stop();
    StepperTorretta_stop();
}

// Un NACK o una lettura I2C corta rende il tank disarmato fino a reset.
// Non tentiamo di riarmare automaticamente una PCA9685 che ha appena segnalato errore.
static void enterShieldFault() {
    if (!shieldReady) {
        return;
    }

    // Spegni prima le uscite che non dipendono da I2C e tenta l'ultimo brake della
    // PCA9685 prima di segnare la shield come non utilizzabile.
    setFireRelay(false);
    StepperTorretta_stop();
    TrackController_stop();
    shieldReady = false;

    if (!shieldFaultReported) {
        shieldFaultReported = true;
        Serial.println("ERRORE: comunicazione PCA9685; tank disarmato fino al reset");
    }
}

void setup() {
    // Precarica i latch GPIO nello stato sicuro prima di trasformarli in output.
    // In questo modo D7 e D2-D5 non attendono Serial o il ritardo di avvio per
    // ricevere il primo livello definito dal firmware.
    int inactiveRelayLevel = FIRE_RELAY_ACTIVE_HIGH ? LOW : HIGH;
    digitalWrite(FIRE_RELAY_PIN, inactiveRelayLevel);
    pinMode(FIRE_RELAY_PIN, OUTPUT);
    setFireRelay(false);

    digitalWrite(TURRET_DRIVER_A_PIN, LOW);
    digitalWrite(TURRET_DRIVER_B_PIN, LOW);
    digitalWrite(TURRET_DRIVER_C_PIN, LOW);
    digitalWrite(TURRET_DRIVER_D_PIN, LOW);
    StepperTorretta_begin();

    Serial.begin(9600);

    // Inizializza e frena la PCA9685 prima del ritardo seriale: dopo un reset la
    // scheda PWM puo' conservare per poco l'ultimo comando ai cingoli.
    Wire.begin();
    shieldReady = configureShieldAddress();
    if (shieldReady) {
        // Avvia PWM, spegne le uscite motore e passa la shield ai moduli.
        shieldReady = shield.begin();
        if (shieldReady) {
            shield.DCbrakeAll();
            shieldReady = shield.isCommunicationHealthy();
        }

        if (shieldReady) {
            TrackController_begin(shield);
            ServoTorretta_begin(shield);
            shieldReady = shield.isCommunicationHealthy();
        }

        if (!shieldReady) {
            shieldFaultReported = true;
            Serial.println("ERRORE: inizializzazione PCA9685 fallita; tank disarmato");
        }
    }

    // Il ritardo serve solo alla console seriale, non deve ritardare il brake motori.
    delay(1000);

    // Avvia WiFi access point e ricezione UDP.
    UdpReceiver_begin();
    Serial.println("Tank pronto");
}

void loop() {
    // Riceve l'ultimo comando del controller ESP32.
    // Se non arrivano pacchetti, UdpReceiver_update() restituisce valori sicuri centrati.
    TankCommand command = UdpReceiver_update();

    // Il rilascio di Zero deve essere osservato dopo boot o reconnessione prima
    // di accettare un nuovo fronte di pressione.
    static bool lastZeroPressed = false;
    static bool zeroInputArmed = false;

    // Non inviare alcun nuovo comando agli attuatori se il link e' scaduto.
    // Spegnimento relay e arresto vengono eseguiti prima di ogni altro aggiornamento.
    if (!command.connected || !shieldReady) {
        setFireRelay(false);
        stopAllMotion();
        updateFireRelay(false, false);
        lastZeroPressed = false;
        zeroInputArmed = false;

        if (shieldReady && !shield.isCommunicationHealthy()) {
            enterShieldFault();
        }
    } else {
        // La torretta orizzontale e' diretta: usa D2-D5, quindi non dipende dalla PCA9685.
        StepperTorretta_updateJoystick(command.turretX);

        // Cingoli ed elevazione dipendono dalla shield PWM.
        if (shieldReady) {
            TrackController_update(command.driveX, command.driveY);
            if (!shield.isCommunicationHealthy()) {
                enterShieldFault();
            } else {
                ServoTorretta_updateJoystick(command.elevationY);
                if (!shield.isCommunicationHealthy()) {
                    enterShieldFault();
                }
            }
        }

        // Fire e Zero restano inibiti se una scrittura PWM ha appena fallito.
        if (shieldReady) {
            updateFireRelay(command.firePressed, true);

            // Zero azzera la posizione logica della torretta una sola volta per pressione.
            // Dopo una reconnessione, una pressione gia' mantenuta viene ignorata fino al rilascio.
            if (!zeroInputArmed) {
                if (!command.zeroPressed) {
                    zeroInputArmed = true;
                }
                lastZeroPressed = command.zeroPressed;
            } else {
                if (command.zeroPressed && !lastZeroPressed) {
                    StepperTorretta_setZero();
                    ServoTorretta_setZero();
                }
                lastZeroPressed = command.zeroPressed;
            }
        } else {
            updateFireRelay(false, false);
            lastZeroPressed = false;
            zeroInputArmed = false;
        }
    }

    // Mostra coordinate e stato connessione una volta al secondo.
    static unsigned long lastPrintTime = 0;
    if (millis() - lastPrintTime > COORDINATE_PRINT_INTERVAL_MS) {
        lastPrintTime = millis();

        Serial.print("RX ");
        Serial.print(command.connected && shieldReady ? "OK" : "DISARMED");
        Serial.print(" | drive X=");
        Serial.print(command.driveX);
        Serial.print(" Y=");
        Serial.print(command.driveY);
        Serial.print(" | turret X=");
        Serial.print(command.turretX);
        Serial.print(" angolo=");
        Serial.print(StepperTorretta_getAngle());
        Serial.print("deg | elev Y=");
        Serial.print(command.elevationY);
        Serial.print(" servo=");
        Serial.print(ServoTorretta_getAngle());
        Serial.print("deg | zero=");
        Serial.print(command.zeroPressed ? "PREMUTO" : "off");
        Serial.print(" fire=");
        Serial.println(command.firePressed ? "PREMUTO" : "off");
    }
}
