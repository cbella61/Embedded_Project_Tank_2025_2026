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

// Puntatore alla shield ricevuta dal main in TrackController_begin().
static MotorController* shield = nullptr;

// Converte un asse joystick 0-1023 in un valore centrato attorno a zero.
// Esempio: 512 diventa 0, 1023 diventa circa +511, 0 diventa -512.
static int centeredAxis(int value, bool inverted) {
    int centered = constrain(value, 0, 1023) - DRIVE_JOYSTICK_CENTER;

    // Pulisce il rumore del joystick prima del mixing differenziale.
    // Cosi' un piccolo errore su X non fa partire un cingolo quando vuoi andare dritto.
    if (abs(centered) < DRIVE_DEADZONE) {
        centered = 0;
    }

    return inverted ? -centered : centered;
}

// Ferma un motore DC della shield.
static void stopTrackMotor(int motorNumber) {
    if (shield == nullptr) {
        return;
    }

    shield->DCbrake(motorNumber);
}

// Mappa avanti/indietro in modo lineare: Joy1 Y deve poter arrivare al massimo.
static int mapLinearTrackSpeed(int magnitude, int minPwm, int maxPwm) {
    int fullMagnitude = DRIVE_JOYSTICK_CENTER - 1;
    int limitedMagnitude = constrain(magnitude, DRIVE_DEADZONE, fullMagnitude);

    return map(limitedMagnitude, DRIVE_DEADZONE, fullMagnitude, minPwm, maxPwm);
}

// Applica la curva solo al comando di sterzata Joy1 X.
// Cosi' avanti/indietro resta normale, mentre la rotazione ha piu' livelli medi.
static int shapeTurnCommand(int turnCommand) {
    if (turnCommand == 0) {
        return 0;
    }

    int sign = turnCommand > 0 ? 1 : -1;
    int magnitude = abs(turnCommand);

    int midMagnitude =
        abs(constrain(TRACK_TURN_MID_JOYSTICK_VALUE, 0, 1023) - DRIVE_JOYSTICK_CENTER);
    int preMaxMagnitude =
        abs(constrain(TRACK_TURN_PRE_MAX_JOYSTICK_VALUE, 0, 1023) - DRIVE_JOYSTICK_CENTER);
    int fullSpeedMagnitude =
        abs(constrain(TRACK_TURN_FULL_SPEED_JOYSTICK_VALUE, 0, 1023) - DRIVE_JOYSTICK_CENTER);

    int fullOutputMagnitude = DRIVE_JOYSTICK_CENTER - 1;
    int midOutputMagnitude =
        (fullOutputMagnitude * constrain(TRACK_TURN_MID_SPEED_PERCENT, 0, 100)) / 100;
    int preMaxOutputMagnitude =
        (fullOutputMagnitude * constrain(TRACK_TURN_PRE_MAX_SPEED_PERCENT, 0, 100)) / 100;

    midMagnitude = constrain(midMagnitude, DRIVE_DEADZONE + 1, fullOutputMagnitude - 2);
    preMaxMagnitude = constrain(preMaxMagnitude, midMagnitude + 1, fullOutputMagnitude - 1);
    fullSpeedMagnitude = constrain(fullSpeedMagnitude, preMaxMagnitude + 1, fullOutputMagnitude);
    midOutputMagnitude = constrain(midOutputMagnitude, DRIVE_DEADZONE, fullOutputMagnitude - 2);
    preMaxOutputMagnitude =
        constrain(preMaxOutputMagnitude, midOutputMagnitude + 1, fullOutputMagnitude - 1);

    int limitedMagnitude = constrain(magnitude, DRIVE_DEADZONE, fullSpeedMagnitude);
    int shapedMagnitude = DRIVE_DEADZONE;

    if (limitedMagnitude <= midMagnitude) {
        long input = limitedMagnitude - DRIVE_DEADZONE;
        long inputRange = midMagnitude - DRIVE_DEADZONE;
        long outputRange = midOutputMagnitude - DRIVE_DEADZONE;

        long linearOutput = (input * outputRange) / inputRange;
        long curvedOutput = (input * input * outputRange) / (inputRange * inputRange);
        long curvePercent = constrain(TRACK_TURN_CURVE_PERCENT, 0, 100);
        long mixedOutput =
            (linearOutput * (100 - curvePercent) + curvedOutput * curvePercent) / 100;

        shapedMagnitude = DRIVE_DEADZONE + mixedOutput;
    } else if (limitedMagnitude <= preMaxMagnitude) {
        long input = limitedMagnitude - midMagnitude;
        long inputRange = preMaxMagnitude - midMagnitude;
        long outputRange = preMaxOutputMagnitude - midOutputMagnitude;

        shapedMagnitude = midOutputMagnitude + (input * outputRange) / inputRange;
    } else {
        long highInput = limitedMagnitude - preMaxMagnitude;
        long highInputRange = fullSpeedMagnitude - preMaxMagnitude;
        long highOutputRange = fullOutputMagnitude - preMaxOutputMagnitude;

        shapedMagnitude =
            preMaxOutputMagnitude + (highInput * highOutputRange) / highInputRange;
    }

    return sign * constrain(shapedMagnitude, 0, fullOutputMagnitude);
}

// Trasforma un comando joystick positivo/negativo in direzione e PWM motore.
static void updateTrackMotor(int motorNumber, bool inverted, int command, int minPwm, int maxPwm,
                             int pwmPercent) {
    if (shield == nullptr) {
        return;
    }

    command = constrain(command, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    minPwm = constrain(minPwm, 0, MAX_SPEED);
    maxPwm = constrain(maxPwm, minPwm, MAX_SPEED);
    pwmPercent = constrain(pwmPercent, 0, 150);

    // Dentro la deadzone il motore resta spento.
    if (abs(command) < DRIVE_DEADZONE) {
        stopTrackMotor(motorNumber);
        return;
    }

    int magnitude = abs(command);

    // Avanti/indietro e il comando finale dei motori restano lineari.
    int speed = mapLinearTrackSpeed(magnitude, minPwm, maxPwm);
    speed = constrain((speed * pwmPercent) / 100, 0, MAX_SPEED);

    int direction = command > 0 ? FORWARD : BACKWARD;
    if (inverted) {
        direction = direction == FORWARD ? BACKWARD : FORWARD;
    }

    shield->DCrun(motorNumber, direction, speed);
}

void TrackController_begin(MotorController& controller) {
    // Salva il riferimento alla shield inizializzata dal main.
    shield = &controller;

    // Parte sempre con entrambi i cingoli spenti.
    TrackController_stop();
}

void TrackController_update(int driveX, int driveY) {
    // Joy1 Y: avanti/indietro. Joy1 X: sterzata.
    int forward = centeredAxis(driveY, DRIVE_Y_INVERTED);
    int turn = centeredAxis(driveX, DRIVE_X_INVERTED);

    // La curva dei livelli medi vale solo per la rotazione/sterzata.
    turn = shapeTurnCommand(turn);

    // Mixing differenziale:
    // - avanti dritto: entrambi i motori girano uguali
    // - sterzata: un lato accelera e l'altro rallenta
    // - solo X: un motore avanti e uno indietro, quindi ruota sul posto
    int leftCommand = constrain(forward + turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);
    int rightCommand = constrain(forward - turn, -DRIVE_JOYSTICK_CENTER, DRIVE_JOYSTICK_CENTER);

    updateTrackMotor(LEFT_TRACK_MOTOR, LEFT_TRACK_INVERTED, leftCommand, LEFT_TRACK_MIN_PWM,
                     LEFT_TRACK_MAX_PWM, LEFT_TRACK_PWM_PERCENT);
    updateTrackMotor(RIGHT_TRACK_MOTOR, RIGHT_TRACK_INVERTED, rightCommand, RIGHT_TRACK_MIN_PWM,
                     RIGHT_TRACK_MAX_PWM, RIGHT_TRACK_PWM_PERCENT);
}

void TrackController_stop() {
    stopTrackMotor(LEFT_TRACK_MOTOR);
    stopTrackMotor(RIGHT_TRACK_MOTOR);
}
