#include "servoTorreta.h"

/*
 * METODO DI FUNZIONAMENTO DELLA TORRETTA
 *
 * Torretta orizzontale:
 * - il driver esterno riceve quattro segnali: A, B, C, D
 * - ad ogni step accendiamo una sola uscita alla volta
 * - la sequenza in avanti e': A -> B -> C -> D -> A
 * - la sequenza indietro e': D -> C -> B -> A -> D
 *
 * Elevazione:
 * - i due servo sono collegati alla PCA9685 della shield su S5 e S6
 * - il primo servo riceve l'angolo normale
 * - il secondo servo riceve un angolo specchiato: ELEVATION_MIRROR_BASE - angolo
 */

// ===== LIMITI MECCANICI =====

// La torretta orizzontale si ferma a mezzo giro per lato.
#define TURRET_MIN_ANGLE -180
#define TURRET_MAX_ANGLE 180

// I due servo di elevazione non devono superare questo intervallo meccanico.
// Range richiesto per la torretta: 0 gradi = basso, 47 gradi = alto.
#define ELEVATION_MIN_ANGLE 0
#define ELEVATION_MAX_ANGLE 47
#define ELEVATION_MIRROR_BASE 90
#define ELEVATION_SERVO_A S5
#define ELEVATION_SERVO_B S6

// Centro logico dei joystick dopo conversione 0-1023.
#define JOYSTICK_CENTER 512

// I servo vengono aggiornati piu' lentamente dello stepper per restare stabili.
#define SERVO_INTERVAL_MS 30

// Conversione dei limiti in gradi nei limiti in step.
#define TURRET_MIN_STEPS ((STEPS_PER_REV * TURRET_MIN_ANGLE) / 360)
#define TURRET_MAX_STEPS ((STEPS_PER_REV * TURRET_MAX_ANGLE) / 360)

// Puntatore alla shield ricevuta dal main. Serve solo per i servo S5/S6.
static MotorController* shield = nullptr;

// Stato logico dello stepper orizzontale.
static int currentSteps = 0;
static int stepIndex = 0;
static unsigned long lastStepTime = 0;
static bool stepperEnabled = false;

// Stato logico dei servo di elevazione.
static int currentServoAngle = 0;
static unsigned long lastServoUpdateTime = 0;

// Scrive fisicamente una fase sul driver della torretta.
// Questa e' la stessa sequenza a una bobina del vecchio codice diretto Arduino.
static void writeTurretStep(int phase) {
    switch (phase) {
    case 0:
        digitalWrite(TURRET_DRIVER_A_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 1:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 2:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, HIGH);
        digitalWrite(TURRET_DRIVER_D_PIN, LOW);
        break;
    case 3:
        digitalWrite(TURRET_DRIVER_A_PIN, LOW);
        digitalWrite(TURRET_DRIVER_B_PIN, LOW);
        digitalWrite(TURRET_DRIVER_C_PIN, LOW);
        digitalWrite(TURRET_DRIVER_D_PIN, HIGH);
        break;
    }

    stepperEnabled = true;
}

// Fa uno step verso destra, se non siamo al limite software.
static void stepRight() {
    if (currentSteps >= TURRET_MAX_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex = (stepIndex + 1) % 4;
    writeTurretStep(stepIndex);
    currentSteps++;
}

// Fa uno step verso sinistra, se non siamo al limite software.
static void stepLeft() {
    if (currentSteps <= TURRET_MIN_STEPS) {
        StepperTorretta_stop();
        return;
    }

    stepIndex = (stepIndex + 3) % 4;
    writeTurretStep(stepIndex);
    currentSteps--;
}

void StepperTorretta_begin() {
    // I pin D2-D5 escono dalla shield come pin digitali Arduino.
    pinMode(TURRET_DRIVER_A_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_B_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_C_PIN, OUTPUT);
    pinMode(TURRET_DRIVER_D_PIN, OUTPUT);

    // Forza subito tutte le uscite a LOW e riparte dalla fase 0.
    stepperEnabled = true;
    StepperTorretta_stop();
    currentSteps = 0;
    stepIndex = 0;
}

void StepperTorretta_updateJoystick(int joystickValue) {
    unsigned long now = millis();

    // Limita la velocita: se non e' passato abbastanza tempo, non fa step.
    if (now - lastStepTime < TURRET_STEP_INTERVAL_MS) {
        return;
    }

    lastStepTime = now;

    // Joy2 X sotto il centro gira a sinistra, sopra il centro gira a destra.
    // Dentro la deadzone spegne il driver per evitare vibrazione.
    if (joystickValue < JOYSTICK_CENTER - TURRET_JOYSTICK_DEADZONE) {
        stepLeft();
    } else if (joystickValue > JOYSTICK_CENTER + TURRET_JOYSTICK_DEADZONE) {
        stepRight();
    } else {
        StepperTorretta_stop();
    }
}

void StepperTorretta_setZero() {
    // Azzera la posizione logica senza muovere il motore.
    currentSteps = 0;
}

void StepperTorretta_stop() {
    if (!stepperEnabled) {
        return;
    }

    // Tutte le uscite basse: il driver non alimenta nessuna bobina.
    digitalWrite(TURRET_DRIVER_A_PIN, LOW);
    digitalWrite(TURRET_DRIVER_B_PIN, LOW);
    digitalWrite(TURRET_DRIVER_C_PIN, LOW);
    digitalWrite(TURRET_DRIVER_D_PIN, LOW);
    stepperEnabled = false;
}

int StepperTorretta_getAngle() {
    return (currentSteps * 360L) / STEPS_PER_REV;
}

void ServoTorretta_begin(MotorController& controller) {
    // Salva la shield e porta i servo alla posizione iniziale.
    shield = &controller;
    ServoTorretta_setZero();
}

void ServoTorretta_updateJoystick(int joystickValue) {
    unsigned long now = millis();

    // I servo non vengono aggiornati ad ogni loop: 30 ms e' piu' stabile.
    if (now - lastServoUpdateTime < SERVO_INTERVAL_MS) {
        return;
    }

    lastServoUpdateTime = now;

    int nextAngle = currentServoAngle;

    // Joy2 Y abbassa/alza di un grado alla volta.
    if (joystickValue < JOYSTICK_CENTER - TURRET_JOYSTICK_DEADZONE) {
        nextAngle--;
    } else if (joystickValue > JOYSTICK_CENTER + TURRET_JOYSTICK_DEADZONE) {
        nextAngle++;
    }

    if (nextAngle != currentServoAngle) {
        ServoTorretta_setAngle(nextAngle);
    }
}

void ServoTorretta_setAngle(int angle) {
    if (shield == nullptr) {
        return;
    }

    // Blocca l'angolo dentro i limiti meccanici e comanda i due servo specchiati.
    currentServoAngle = constrain(angle, ELEVATION_MIN_ANGLE, ELEVATION_MAX_ANGLE);
    shield->servoPairTurn(ELEVATION_SERVO_A, ELEVATION_SERVO_B, currentServoAngle,
                          ELEVATION_MIRROR_BASE);
}

void ServoTorretta_setZero() {
    ServoTorretta_setAngle(ELEVATION_MIN_ANGLE);
}

int ServoTorretta_getAngle() {
    return currentServoAngle;
}
