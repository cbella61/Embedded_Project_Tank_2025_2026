#include "trackController.h"

/*
 * METODO DI FUNZIONAMENTO DEI CINGOLI DC
 *
 * Ogni motore giallo ha solo due fili. La shield gli da:
 * - direzione: avanti o indietro
 * - velocita: PWM dal minimo al massimo configurato per ogni cingolo
 *
 * Il codice non fa piu' fasi stepper. Ora manda semplicemente PWM ai motori
 * M1 e M3, con mixing differenziale per girare come un tank.
 */

// Puntatore al driver PWM ricevuto dal main in TrackController_begin().
static MotorController* motorController = nullptr;

// Prima di invertire un cingolo, il firmware applica una breve pausa a PWM zero.
// Il valore va validato sul driver reale: e' un miglioramento software, non sostituisce
// il cutoff hardware in caso di blocco del bus I2C.
#define TRACK_REVERSE_DEAD_TIME_MS 30

// La deadzone deve lasciare almeno un comando positivo e uno negativo disponibili.
static_assert(TRACK_COMMAND_DEADZONE > 0 && TRACK_COMMAND_DEADZONE < DRIVE_JOYSTICK_CENTER,
              "TRACK_COMMAND_DEADZONE must stay inside the joystick range");

struct TrackMotorState {
    // Ultimo verso passato a DCRun(). E' una richiesta software, non una misura del motore.
    int lastRequestedDirection;
    // Ultimo verso prima di DCbrake(). Resta memorizzato anche se il joystick torna al centro,
    // cosi' un'inversione immediata rispetta comunque il tempo di pausa.
    int directionBeforeStop;
    int pendingDirection;
    int pendingSpeed;
    bool waitingForReverse;
    unsigned long stoppedAt;
};

static TrackMotorState leftTrackState = {0, 0, 0, 0, false, 0};
static TrackMotorState rightTrackState = {0, 0, 0, 0, false, 0};

// Evita di riscrivere continuamente gli stessi quattro registri I2C mentre il
// joystick resta fermo. Il refresh periodico conserva comunque il controllo di
// salute della shield; uno stop bypassa questa limitazione.
static int lastDriveX = DRIVE_JOYSTICK_CENTER;
static int lastDriveY = DRIVE_JOYSTICK_CENTER;
static bool hasLastDriveCommand = false;
static unsigned long lastTrackCommandTime = 0;
static bool stopCommandIssued = false;
static unsigned long lastStopCommandTime = 0;

static TrackMotorState* stateForTrackMotor(int motorNumber) {
    if (motorNumber == LEFT_TRACK_MOTOR) {
        return &leftTrackState;
    }

    if (motorNumber == RIGHT_TRACK_MOTOR) {
        return &rightTrackState;
    }

    return nullptr;
}

// Decodifica un asse UDP 0--1023 in un comando firmato centrato su zero.
// Esempio: 512 diventa 0, 1023 diventa circa +511, 0 diventa -512.
// L'inversione dell'asse e' responsabilita' del controller ESP32, non del tank.
static int decodeDriveAxis(int value) {
    int centered = constrain(value, 0, 1023) - DRIVE_JOYSTICK_CENTER;

    // Primo filtro lato tank: protegge anche da sender UDP diversi dall'ESP32.
    // Il filtro finale di applyTrackMotorCommand() resta necessario dopo forward +/- turn.
    if (abs(centered) < TRACK_COMMAND_DEADZONE) {
        centered = 0;
    }

    return centered;
}

// Porta un cingolo a PWM zero e annulla un'eventuale inversione in attesa.
static void stopTrackMotor(int motorNumber) {
    if (motorController == nullptr) {
        return;
    }

    TrackMotorState* state = stateForTrackMotor(motorNumber);
    motorController->DCbrake(motorNumber);

    if (state != nullptr) {
        // Non azzerare directionBeforeStop: serve se dopo il centro viene chiesto il verso opposto.
        if (state->lastRequestedDirection != 0) {
            state->directionBeforeStop = state->lastRequestedDirection;
            state->stoppedAt = millis();
        }

        state->lastRequestedDirection = 0;
        state->pendingDirection = 0;
        state->pendingSpeed = 0;
        state->waitingForReverse = false;
    }
}

// Mappa avanti/indietro in modo lineare: Joy1 Y deve poter arrivare al massimo.
static int mapLinearTrackSpeed(int magnitude, int minPwm, int maxPwm) {
    int fullMagnitude = DRIVE_JOYSTICK_CENTER - 1;
    int limitedMagnitude = constrain(magnitude, TRACK_COMMAND_DEADZONE, fullMagnitude);

    return map(limitedMagnitude, TRACK_COMMAND_DEADZONE, fullMagnitude, minPwm, maxPwm);
}

// Applica un comando firmato a un cingolo, includendo PWM e pausa sicura di inversione.
static void applyTrackMotorCommand(int motorNumber, bool inverted, int command, int minPwm,
                                   int maxPwm, int pwmPercent) {
    if (motorController == nullptr) {
        return;
    }

    TrackMotorState* state = stateForTrackMotor(motorNumber);
    if (state == nullptr) {
        return;
    }

    command = constrain(command, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    minPwm = constrain(minPwm, 0, MAX_SPEED);
    maxPwm = constrain(maxPwm, minPwm, MAX_SPEED);
    pwmPercent = constrain(pwmPercent, 0, 150);

    // Secondo filtro lato tank: il mixing puo' lasciare piccolo un solo cingolo anche
    // quando forward e turn erano entrambi fuori dalla deadzone individuale.
    if (abs(command) < TRACK_COMMAND_DEADZONE) {
        stopTrackMotor(motorNumber);
        return;
    }

    int magnitude = abs(command);

    // Avanti/indietro e il comando finale dei motori restano lineari.
    int speed = mapLinearTrackSpeed(magnitude, minPwm, maxPwm);
    speed = constrain(static_cast<int>((static_cast<long>(speed) * pwmPercent) / 100), 0, MAX_SPEED);

    int direction = command > 0 ? FORWARD : BACKWARD;
    if (inverted) {
        direction = direction == FORWARD ? BACKWARD : FORWARD;
    }

    unsigned long now = millis();

    // Durante la pausa di inversione conserva soltanto l'ultimo comando,
    // senza riaccendere il ponte H prima che il tempo minimo sia trascorso.
    if (state->waitingForReverse) {
        state->pendingDirection = direction;
        state->pendingSpeed = speed;

        if (now - state->stoppedAt < TRACK_REVERSE_DEAD_TIME_MS) {
            return;
        }

        motorController->DCrun(motorNumber, state->pendingDirection, state->pendingSpeed);
        state->lastRequestedDirection = state->pendingDirection;
        state->directionBeforeStop = state->pendingDirection;
        state->waitingForReverse = false;
        return;
    }

    // Non invertire direttamente un motore in movimento: frena, attendi e poi riapplica.
    if (state->lastRequestedDirection != 0 && state->lastRequestedDirection != direction) {
        motorController->DCbrake(motorNumber);
        state->directionBeforeStop = state->lastRequestedDirection;
        state->lastRequestedDirection = 0;
        state->pendingDirection = direction;
        state->pendingSpeed = speed;
        state->waitingForReverse = true;
        state->stoppedAt = now;
        return;
    }

    // Se e' gia' stato fermato, anche il percorso centro -> verso opposto deve attendere.
    // Senza questo controllo il vecchio codice poteva bypassare i 30 ms dopo il centro.
    if (state->lastRequestedDirection == 0 && state->directionBeforeStop != 0 &&
        state->directionBeforeStop != direction &&
        now - state->stoppedAt < TRACK_REVERSE_DEAD_TIME_MS) {
        state->pendingDirection = direction;
        state->pendingSpeed = speed;
        state->waitingForReverse = true;
        return;
    }

    // Il comando viene aggiornato a intervalli controllati anche se invariato:
    // non fare caching permanente, altrimenti un guasto del bus puo' restare
    // invisibile al controllo di salute della shield.
    motorController->DCrun(motorNumber, direction, speed);
    state->lastRequestedDirection = direction;
    state->directionBeforeStop = direction;
}

void TrackController_begin(MotorController& controller) {
    // Salva il riferimento alla shield inizializzata dal main.
    motorController = &controller;
    hasLastDriveCommand = false;
    stopCommandIssued = false;

    // Parte sempre con entrambi i cingoli spenti.
    TrackController_stop();
}

void TrackController_update(int driveX, int driveY) {
    unsigned long now = millis();
    driveX = constrain(driveX, 0, 1023);
    driveY = constrain(driveY, 0, 1023);

    bool commandChanged =
        !hasLastDriveCommand || driveX != lastDriveX || driveY != lastDriveY;
    if (!commandChanged && now - lastTrackCommandTime < TRACK_COMMAND_REFRESH_INTERVAL_MS) {
        return;
    }

    lastDriveX = driveX;
    lastDriveY = driveY;
    hasLastDriveCommand = true;
    lastTrackCommandTime = now;
    stopCommandIssued = false;

    // Joy1 Y: avanti/indietro. Joy1 X: sterzata.
    int forward = decodeDriveAxis(driveY);
    int turn = decodeDriveAxis(driveX);

    // Mixing differenziale:
    // - avanti dritto: entrambi i motori girano uguali
    // - sterzata: un lato accelera e l'altro rallenta
    // - solo X: un motore avanti e uno indietro, quindi ruota sul posto
    int leftCommand = constrain(forward + turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    int rightCommand = constrain(forward - turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);

    applyTrackMotorCommand(LEFT_TRACK_MOTOR, LEFT_TRACK_INVERTED, leftCommand, LEFT_TRACK_MIN_PWM,
                           LEFT_TRACK_MAX_PWM, LEFT_TRACK_PWM_PERCENT);
    applyTrackMotorCommand(RIGHT_TRACK_MOTOR, RIGHT_TRACK_INVERTED, rightCommand,
                           RIGHT_TRACK_MIN_PWM, RIGHT_TRACK_MAX_PWM, RIGHT_TRACK_PWM_PERCENT);
}

void TrackController_stop() {
    unsigned long now = millis();
    if (stopCommandIssued && now - lastStopCommandTime < TRACK_COMMAND_REFRESH_INTERVAL_MS) {
        return;
    }

    stopTrackMotor(LEFT_TRACK_MOTOR);
    stopTrackMotor(RIGHT_TRACK_MOTOR);
    hasLastDriveCommand = false;
    stopCommandIssued = true;
    lastStopCommandTime = now;
}
