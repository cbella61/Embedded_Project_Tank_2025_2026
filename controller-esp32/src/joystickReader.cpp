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

// Queste deadzone filtrano il rumore ADC attorno al centro fisico calibrato.
// Non sono la protezione dei motori: quella resta sul tank, dopo il mixing dei cingoli.
// Per Joy1 guida usiamo un valore piccolo, altrimenti si sommerebbe troppo alla
// TRACK_COMMAND_DEADZONE del tank e renderebbe poco sensibile la partenza.
// 20 e' coerente con la tolleranza di riarmo del ricevitore UDP.
#define DRIVE_INPUT_DEADZONE 20

// Joy2 mantiene la sensibilita' precedente, indipendente dalla guida dei cingoli.
#define TURRET_INPUT_DEADZONE 80

// Numero di letture usate all'avvio per trovare il centro reale dei joystick.
#define CALIBRATION_SAMPLES 80

// La calibrazione viene accettata solo con joystick vicino al centro atteso e
// senza variazioni ampie. I valori vanno verificati sul controller fisico.
#define CALIBRATION_MAX_CENTER_OFFSET 70
#define CALIBRATION_MAX_SPREAD 40

// Prima di abilitare i comandi, joystick e pulsanti devono restare neutri.
#define NEUTRAL_ARMING_MS 400

// Il pulsante deve mantenere lo stesso livello per questo tempo prima che il
// suo stato venga considerato valido.
#define BUTTON_DEBOUNCE_MS 40

// I joystick sono montati ruotati: scambia fisicamente X con Y su entrambi.
#define DRIVE_SWAP_X_Y true
#define TURRET_SWAP_X_Y true

// Usa queste quattro costanti solo per cambiare il verso di un singolo asse.
// true = 0 diventa 1023 e 1023 diventa 0, mantenendo il centro a 512.
// DRIVE_X/Y_INVERTED sono l'unica sorgente di verita' per l'orientamento di Joy1:
// il tank riceve gia' assi normalizzati e corregge soltanto il cablaggio dei motori.
#define DRIVE_X_INVERTED false
#define DRIVE_Y_INVERTED false
#define TURRET_X_INVERTED false
#define ELEVATION_Y_INVERTED false

static int driveXCenter = JOYSTICK_CENTER;
static int driveYCenter = JOYSTICK_CENTER;
static int turretXCenter = JOYSTICK_CENTER;
static int elevationYCenter = JOYSTICK_CENTER;
static bool calibrationValid = false;
static bool commandsArmed = false;
static unsigned long neutralSince = 0;

struct DebouncedButton {
    uint8_t pin;
    bool candidatePressed;
    bool stablePressed;
    unsigned long candidateChangedAt;
};

static DebouncedButton zeroButton = {ZERO_BUTTON_PIN, false, false, 0};
static DebouncedButton fireButton = {FIRE_BUTTON_PIN, false, false, 0};

static int readRawJoystick(int pin) {
    int rawValue = analogRead(pin);

    // L'ADC ESP32 legge 0-4095; il firmware tank lavora in 0-1023.
    return constrain(map(rawValue, 0, 4095, AXIS_MIN, AXIS_MAX), AXIS_MIN, AXIS_MAX);
}

static bool calibrateAxisCenter(int pin, int& center) {
    long sum = 0;
    int minValue = AXIS_MAX;
    int maxValue = AXIS_MIN;

    for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
        int value = readRawJoystick(pin);
        sum += value;
        minValue = min(minValue, value);
        maxValue = max(maxValue, value);
        delay(2);
    }

    center = constrain(sum / CALIBRATION_SAMPLES, AXIS_MIN, AXIS_MAX);

    bool closeToExpectedCenter =
        abs(center - JOYSTICK_CENTER) <= CALIBRATION_MAX_CENTER_OFFSET;
    bool stableDuringSampling = maxValue - minValue <= CALIBRATION_MAX_SPREAD;
    return closeToExpectedCenter && stableDuringSampling;
}

// Legge, ricentra e normalizza un asse. inputDeadzone e' espressa nella scala UDP 0--1023
// ed e' limitata alla corsa disponibile, cosi' map() non riceve un intervallo degenerato.
static int readCalibratedJoystick(int pin, int center, int inputDeadzone) {
    int raw = readRawJoystick(pin);
    int availableBelowCenter = max(center - AXIS_MIN - 1, 0);
    int availableAboveCenter = max(AXIS_MAX - center - 1, 0);
    int deadzone = constrain(inputDeadzone, 0, min(availableBelowCenter, availableAboveCenter));

    // Zona morta attorno al centro reale misurato all'avvio.
    if (abs(raw - center) < deadzone) {
        return JOYSTICK_CENTER;
    }

    // Sotto il centro: usa tutta la corsa 0 -> centro per arrivare a 0 -> 512.
    // Sopra il centro: usa tutta la corsa centro -> 1023 per arrivare a 512 -> 1023.
    // Cosi' correggiamo il centro senza perdere gli estremi del joystick.
    if (raw < center) {
        int lowerCenter = max(center - deadzone, 1);
        return constrain(map(raw, AXIS_MIN, lowerCenter, AXIS_MIN, JOYSTICK_CENTER), AXIS_MIN,
                         JOYSTICK_CENTER);
    }

    int upperCenter = min(center + deadzone, AXIS_MAX - 1);
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

static bool calibrateJoysticks() {
    Serial.println();
    Serial.println("=== CALIBRAZIONE JOYSTICK ESP32 ===");
    Serial.println("Lascia Joy1 e Joy2 fermi al centro...");
    delay(600);

    bool driveXValid = calibrateAxisCenter(DRIVE_JOYSTICK_X_PIN, driveXCenter);
    bool driveYValid = calibrateAxisCenter(DRIVE_JOYSTICK_Y_PIN, driveYCenter);
    bool turretXValid = calibrateAxisCenter(TURRET_JOYSTICK_X_PIN, turretXCenter);
    bool elevationYValid = calibrateAxisCenter(TURRET_JOYSTICK_Y_PIN, elevationYCenter);

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

    bool valid = driveXValid && driveYValid && turretXValid && elevationYValid;
    if (!valid) {
        Serial.println("ERRORE: joystick non centrato o instabile.");
        Serial.println("Comandi inibiti: riavvia lasciando i joystick fermi al centro.");
    }

    return valid;
}

static void beginDebouncedButton(DebouncedButton& button) {
    bool pressed = digitalRead(button.pin) == LOW;
    button.candidatePressed = pressed;
    button.stablePressed = pressed;
    button.candidateChangedAt = millis();
}

static bool readDebouncedButton(DebouncedButton& button) {
    bool rawPressed = digitalRead(button.pin) == LOW;
    unsigned long now = millis();

    if (rawPressed != button.candidatePressed) {
        button.candidatePressed = rawPressed;
        button.candidateChangedAt = now;
    }

    if (button.stablePressed != button.candidatePressed &&
        now - button.candidateChangedAt >= BUTTON_DEBOUNCE_MS) {
        button.stablePressed = button.candidatePressed;
    }

    return button.stablePressed;
}

static ControllerData safeControllerData() {
    return {JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, JOYSTICK_CENTER, false, false};
}

static bool axesAreNeutral(int drivePhysicalX, int drivePhysicalY, int turretPhysicalX,
                           int turretPhysicalY) {
    return drivePhysicalX == JOYSTICK_CENTER && drivePhysicalY == JOYSTICK_CENTER &&
           turretPhysicalX == JOYSTICK_CENTER && turretPhysicalY == JOYSTICK_CENTER;
}

void JoystickReader_begin() {
    // INPUT_PULLUP evita resistenze esterne: il pin sta HIGH e va LOW quando premi.
    pinMode(ZERO_BUTTON_PIN, INPUT_PULLUP);
    pinMode(FIRE_BUTTON_PIN, INPUT_PULLUP);

    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    beginDebouncedButton(zeroButton);
    beginDebouncedButton(fireButton);
    calibrationValid = calibrateJoysticks();
    JoystickReader_requireNeutralBeforeCommands();
}

void JoystickReader_requireNeutralBeforeCommands() {
    commandsArmed = false;
    neutralSince = 0;
}

ControllerData JoystickReader_read() {
    int drivePhysicalX =
        readCalibratedJoystick(DRIVE_JOYSTICK_X_PIN, driveXCenter, DRIVE_INPUT_DEADZONE);
    int drivePhysicalY =
        readCalibratedJoystick(DRIVE_JOYSTICK_Y_PIN, driveYCenter, DRIVE_INPUT_DEADZONE);
    int turretPhysicalX =
        readCalibratedJoystick(TURRET_JOYSTICK_X_PIN, turretXCenter, TURRET_INPUT_DEADZONE);
    int turretPhysicalY =
        readCalibratedJoystick(TURRET_JOYSTICK_Y_PIN, elevationYCenter, TURRET_INPUT_DEADZONE);
    bool zeroPressed = readDebouncedButton(zeroButton);
    bool firePressed = readDebouncedButton(fireButton);

    if (!calibrationValid) {
        return safeControllerData();
    }

    if (!commandsArmed) {
        bool neutralAndReleased =
            axesAreNeutral(drivePhysicalX, drivePhysicalY, turretPhysicalX, turretPhysicalY) &&
            !zeroPressed && !firePressed;

        if (!neutralAndReleased) {
            neutralSince = 0;
            return safeControllerData();
        }

        unsigned long now = millis();
        if (neutralSince == 0) {
            neutralSince = now;
            return safeControllerData();
        }

        if (now - neutralSince < NEUTRAL_ARMING_MS) {
            return safeControllerData();
        }

        commandsArmed = true;
        Serial.println("Comandi joystick armati.");
    }

    ControllerData data;

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

    data.zeroPressed = zeroPressed;
    data.firePressed = firePressed;

    return data;
}
