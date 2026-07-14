#include "joystickReader.h"

/*
 * METODO DI LETTURA DEL CONTROLLER
 *
 * L'ESP32 legge i quattro assi analogici con analogRead().
 * Ogni lettura viene scalata da 0-4095 a 0-1023, cosi il tank riceve
 * valori semplici con centro intorno a 512.
 *
 * Importante: i joystick reali quasi mai stanno esattamente al centro.
 * Per questo il controller calibra il centro all'avvio e applica una
 * deadzone prima di mandare i dati UDP.
 */

// Primo joystick: movimento del tank e sterzata.
#define DRIVE_JOYSTICK_X_PIN 34
#define DRIVE_JOYSTICK_Y_PIN 32

// Secondo joystick: torretta orizzontale ed elevazione.
#define TURRET_JOYSTICK_X_PIN 35
#define TURRET_JOYSTICK_Y_PIN 33

// I pulsanti usano INPUT_PULLUP, quindi premuto significa LOW.
#define ZERO_BUTTON_PIN 25
#define FIRE_BUTTON_PIN 26

// Scala usata dal protocollo UDP del tank.
#define JOYSTICK_CENTER 512
#define AXIS_MIN 0
#define AXIS_MAX 1023

// Zona morta lato controller. Se il joystick balla al centro, aumenta questo.
#define CONTROLLER_DEADZONE 80

// Numero di letture usate all'avvio per trovare il centro reale dei joystick.
#define CALIBRATION_SAMPLES 80

// I joystick sono montati ruotati: scambia fisicamente X con Y su entrambi.
#define DRIVE_SWAP_X_Y true
#define TURRET_SWAP_X_Y true

// Usa queste quattro costanti solo per cambiare il verso di un singolo asse.
// true = 0 diventa 1023 e 1023 diventa 0, mantenendo il centro a 512.
#define DRIVE_X_INVERTED false
#define DRIVE_Y_INVERTED false
#define TURRET_X_INVERTED false
#define ELEVATION_Y_INVERTED false

static int driveXCenter = JOYSTICK_CENTER;
static int driveYCenter = JOYSTICK_CENTER;
static int turretXCenter = JOYSTICK_CENTER;
static int elevationYCenter = JOYSTICK_CENTER;

static int readRawJoystick(int pin) {
    int rawValue = analogRead(pin);

    // L'ADC ESP32 legge 0-4095; il firmware tank lavora in 0-1023.
    return constrain(map(rawValue, 0, 4095, AXIS_MIN, AXIS_MAX), AXIS_MIN, AXIS_MAX);
}

static int calibrateAxisCenter(int pin) {
    long sum = 0;

    for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
        sum += readRawJoystick(pin);
        delay(5);
    }

    return constrain(sum / CALIBRATION_SAMPLES, AXIS_MIN, AXIS_MAX);
}

static int readCalibratedJoystick(int pin, int center) {
    int raw = readRawJoystick(pin);

    // Zona morta attorno al centro reale misurato all'avvio.
    if (abs(raw - center) < CONTROLLER_DEADZONE) {
        return JOYSTICK_CENTER;
    }

    // Sotto il centro: usa tutta la corsa 0 -> centro per arrivare a 0 -> 512.
    // Sopra il centro: usa tutta la corsa centro -> 1023 per arrivare a 512 -> 1023.
    // Cosi' correggiamo il centro senza perdere gli estremi del joystick.
    if (raw < center) {
        int lowerCenter = max(center - CONTROLLER_DEADZONE, 1);
        return constrain(map(raw, AXIS_MIN, lowerCenter, AXIS_MIN, JOYSTICK_CENTER), AXIS_MIN,
                         JOYSTICK_CENTER);
    }

    int upperCenter = min(center + CONTROLLER_DEADZONE, AXIS_MAX - 1);
    return constrain(map(raw, upperCenter, AXIS_MAX, JOYSTICK_CENTER, AXIS_MAX), JOYSTICK_CENTER,
                     AXIS_MAX);
}

static int invertAxisIfNeeded(int value, bool inverted) {
    value = constrain(value, AXIS_MIN, AXIS_MAX);

    if (!inverted || value == JOYSTICK_CENTER) {
        return value;
    }

    return AXIS_MAX - value;
}

static void calibrateJoysticks() {
    Serial.println();
    Serial.println("=== CALIBRAZIONE JOYSTICK ESP32 ===");
    Serial.println("Lascia Joy1 e Joy2 fermi al centro...");
    delay(800);

    driveXCenter = calibrateAxisCenter(DRIVE_JOYSTICK_X_PIN);
    driveYCenter = calibrateAxisCenter(DRIVE_JOYSTICK_Y_PIN);
    turretXCenter = calibrateAxisCenter(TURRET_JOYSTICK_X_PIN);
    elevationYCenter = calibrateAxisCenter(TURRET_JOYSTICK_Y_PIN);

    Serial.print("Joy1 guida centro: X=");
    Serial.print(driveXCenter);
    Serial.print(" Y=");
    Serial.print(driveYCenter);
    Serial.println();

    Serial.print("Joy2 torretta centro: X=");
    Serial.print(turretXCenter);
    Serial.print(" Y=");
    Serial.println(elevationYCenter);
    Serial.println("Da ora un asse fermo viene mandato come circa 512.");
    Serial.println("===================================");
    Serial.println();
}

void JoystickReader_begin() {
    // INPUT_PULLUP evita resistenze esterne: il pin sta HIGH e va LOW quando premi.
    pinMode(ZERO_BUTTON_PIN, INPUT_PULLUP);
    pinMode(FIRE_BUTTON_PIN, INPUT_PULLUP);

    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    calibrateJoysticks();
}

ControllerData JoystickReader_read() {
    ControllerData data;

    int drivePhysicalX = readCalibratedJoystick(DRIVE_JOYSTICK_X_PIN, driveXCenter);
    int drivePhysicalY = readCalibratedJoystick(DRIVE_JOYSTICK_Y_PIN, driveYCenter);
    int turretPhysicalX = readCalibratedJoystick(TURRET_JOYSTICK_X_PIN, turretXCenter);
    int turretPhysicalY = readCalibratedJoystick(TURRET_JOYSTICK_Y_PIN, elevationYCenter);

    // Joy1 viene usato dal tank per il mixing differenziale dei cingoli.
    int driveX = DRIVE_SWAP_X_Y ? drivePhysicalY : drivePhysicalX;
    int driveY = DRIVE_SWAP_X_Y ? drivePhysicalX : drivePhysicalY;
    data.driveX = invertAxisIfNeeded(driveX, DRIVE_X_INVERTED);
    data.driveY = invertAxisIfNeeded(driveY, DRIVE_Y_INVERTED);

    // Joy2 viene usato dal tank per torretta orizzontale ed elevazione.
    int turretX = TURRET_SWAP_X_Y ? turretPhysicalY : turretPhysicalX;
    int elevationY = TURRET_SWAP_X_Y ? turretPhysicalX : turretPhysicalY;
    data.turretX = invertAxisIfNeeded(turretX, TURRET_X_INVERTED);
    data.elevationY = invertAxisIfNeeded(elevationY, ELEVATION_Y_INVERTED);

    // Con INPUT_PULLUP, LOW vuol dire pulsante premuto.
    data.zeroPressed = digitalRead(ZERO_BUTTON_PIN) == LOW;
    data.firePressed = digitalRead(FIRE_BUTTON_PIN) == LOW;

    return data;
}
