/*
 * TANK MAIN
 *
 * This file does not directly perform all movements: it coordinates modules.
 *
 * Operation method:
 * 1. In setup() initialize the relay, turret, PCA9685 shield and UDP receiver.
 * 2. In loop() read the last command received from the ESP32 controller.
 * 3. Dispatch each part of the command to the appropriate module:
 *    - driveX/driveY     -> differential tracks
 *    - turretX           -> horizontal turret D2-D5
 *    - elevationY        -> servos S5/S6
 *    - firePressed       -> relay D7
 *    - zeroPressed       -> logical zeroing
 * 4. If the controller stops sending packets for too long, stop the motors.
 */

#include <Arduino.h>
#include <Wire.h>

#include "motorController.h"
#include "servoTorreta.h"
#include "trackController.h"
#include "udpReceiver.h"

// Digital pin connected to the relay module.
#define FIRE_RELAY_PIN 7

#define FIRE_RELAY_PIN 7

// true: relay active with HIGH. false: relay active with LOW.
#define FIRE_RELAY_ACTIVE_HIGH true

// Duration of the fire pulse: the relay is not kept continuously on.
#define FIRE_RELAY_PULSE_MS 200

// Minimum time between one shot and the next.
#define FIRE_RELAY_COOLDOWN_MS 12000

// ===== SERIAL MONITOR =====

// Print coordinates once per second to avoid filling the console.
#define COORDINATE_PRINT_INTERVAL_MS 1000

// Shared PCA9685 shield between the tracks and elevation servo.
// Frequency is 50 Hz because it is compatible with servos.
static MotorController shield(50);

// Diventa true solo se la PCA9685 viene trovata su I2C.
static bool shieldReady = false;
static bool shieldFaultReported = false;

// Stato del relay sparo.
static bool fireRelayActive = false;
static unsigned long fireRelayStartTime = 0;
static unsigned long lastFireShotTime = 0;
static bool fireRelayHasShot = false;

// Check whether a device responds at an I2C address.
static bool i2cDevicePresent(uint8_t address) {
    Wire.beginTransmission(address);
    return Wire.endTransmission() == 0;
}

// Automatically select the PCA9685 address on the shield.
// Some shields use different addresses, so the code tries common ones.
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

    Serial.println("ERROR: PCA9685 shield not detected");
    return false;
}

// Set the correct electrical level for the fire relay.
static void setFireRelay(bool active) {
    int level =
        active ? (FIRE_RELAY_ACTIVE_HIGH ? HIGH : LOW) : (FIRE_RELAY_ACTIVE_HIGH ? LOW : HIGH);

    digitalWrite(FIRE_RELAY_PIN, level);
    fireRelayActive = active;
}

// Generate a single fire pulse for each button press.
// Uses the rising edge and then waits 12 seconds before accepting another shot.
static void updateFireRelay(bool firePressed, bool connected) {
    static bool lastFirePressed = false;
    static bool fireInputArmed = false;

    // After timeout or loss of connection the relay must turn off immediately.
    // A subsequent connection cannot reuse a button press that remained active:
    // first observe the release of the Fire button.
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

        // Still record the received level: when Fire is held down
        // during reconnection it will not be interpreted as a rising edge.
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

// Stop all motion in case of UDP timeout.
// Tracks depend on the shield; the turret (D2-D5) can be stopped at any time.
static void stopAllMotion() {
    // TrackController_stop() e' innocua prima dell'inizializzazione e va tentata anche
    // dopo un fault I2C: una PCA9685 che ha conservato l'ultimo PWM puo' essere tornata
    // raggiungibile per un istante. Il controller limita internamente i retry di brake.
    TrackController_stop();
    StepperTorretta_stop();
}

// A NACK or a short I2C read makes the tank disarmed until reset.
// Do not attempt to automatically rearm a PCA9685 that has just reported an error.
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
        Serial.println("ERROR: PCA9685 communication; tank disarmed until reset");
    }
}

void setup() {
    // Preload the GPIO latches in a safe state before making them outputs.
    // This way D7 and D2-D5 do not wait for Serial or boot delay to receive the
    // first level defined by the firmware.
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

    // Initialize and brake the PCA9685 before the serial delay: after a reset
    // the PWM board can briefly retain the last command to the tracks.
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
                    Serial.println("ERROR: PCA9685 initialization failed; tank disarmed");
        }
    }

    // The delay is only for the serial console; it should not delay motor braking.
    delay(1000);

    // Start WiFi access point and UDP reception.
    UdpReceiver_begin();
    Serial.println("Tank ready");
}

void loop() {
    // Riceve l'ultimo comando del controller ESP32.
    // Se non arrivano pacchetti, UdpReceiver_update() restituisce valori sicuri centrati.
    TankCommand command = UdpReceiver_update();

    // The release of Zero must be observed after boot or reconnection before
    // accepting a new press event.
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
        // The horizontal turret is direct: uses D2-D5, so it does not depend on the PCA9685.
        StepperTorretta_updateJoystick(command.turretX);
        // Tracks and elevation depend on the PWM shield.
        if (!shieldReady) {
            shieldFaultReported = true;
            Serial.println("ERROR: PCA9685 communication; tank disarmed until reset");
        }
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

            // Zero resets the turret logical position once per press.
            // After a reconnection, a press that is already held is ignored until release.
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
           Serial.print(command.zeroPressed ? "PRESSED" : "off");
        Serial.print(" fire=");
           Serial.println(command.firePressed ? "PRESSED" : "off");
    }
}
