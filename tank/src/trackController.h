#ifndef TRACK_CONTROLLER_H
#define TRACK_CONTROLLER_H

#include <Arduino.h>

#include "motorController.h"

/*
 * CONTROLLO CINGOLI CON MOTORI DC
 *
 * I motori gialli in foto sono motori DC a 2 fili, non stepper.
 * Quindi ogni cingolo usa una sola porta motore della shield:
 * - sinistro: M3
 * - destro:   M1
 *
 * M2 viene lasciato libero perche' sulla shield del progetto quella porta
 * tende a girare anche a joystick fermo.
 *
 * Il joystick Joy1 viene trasformato in guida differenziale:
 * - driveY decide avanti/indietro
 * - driveX decide la sterzata
 * - comando sinistro = avanti + sterzo
 * - comando destro   = avanti - sterzo
 */

// ===== CONFIGURAZIONE GUIDA CINGOLI =====

// I joystick arrivano dal controller gia' scalati da 0 a 1023.
// Il centro ideale e' 512.
#define DRIVE_JOYSTICK_CENTER 512

// Zona morta: se il joystick resta vicino al centro, il cingolo e' fermo.
// Se da fermo un lato prova ancora a muoversi, aumenta di 10/20.
#define DRIVE_DEADZONE 100

// Ogni cingolo usa una porta motore DC della shield.
// M2 resta libero: usa M3 per il sinistro e M1 per il destro.
#define LEFT_TRACK_MOTOR M3
#define RIGHT_TRACK_MOTOR M1

// PWM minimo e massimo separato per ogni cingolo.
// I due motori DC non sono mai identici: uno puo' partire prima o girare piu'
// forte dell'altro anche con lo stesso comando.
//
// Come regolare:
// - un cingolo non parte ai piccoli movimenti: aumenta il suo MIN_PWM di 50;
// - un cingolo parte troppo presto/strappa: abbassa il suo MIN_PWM di 50;
// - un cingolo e' piu' veloce dell'altro: abbassa il suo MAX_PWM o PWM_PERCENT.
#define LEFT_TRACK_MIN_PWM 900
#define RIGHT_TRACK_MIN_PWM 900
#define LEFT_TRACK_MAX_PWM MAX_SPEED
#define RIGHT_TRACK_MAX_PWM MAX_SPEED

// Trim percentuale finale.
// 100 = normale, 90 = quel cingolo va al 90%, 110 = quel cingolo spinge di piu'.
// Se M1/destro corre piu' di M3/sinistro, abbassa RIGHT_TRACK_PWM_PERCENT.
#define LEFT_TRACK_PWM_PERCENT 100
#define RIGHT_TRACK_PWM_PERCENT 100

// Curva solo per la sterzata/rotazione su Joy1 X.
// Avanti/indietro su Joy1 Y resta lineare e puo' arrivare al massimo.
#define TRACK_TURN_CURVE_PERCENT 75

// Fasce della sterzata differenziale:
// - fino a 700: sale progressivamente fino al 55%;
// - da 700 a 999: sale progressivamente dal 55% al 70%;
// - da 1000 in poi: passa al 100%.
#define TRACK_TURN_MID_JOYSTICK_VALUE 700
#define TRACK_TURN_MID_SPEED_PERCENT 55
#define TRACK_TURN_PRE_MAX_JOYSTICK_VALUE 999
#define TRACK_TURN_PRE_MAX_SPEED_PERCENT 70
#define TRACK_TURN_FULL_SPEED_JOYSTICK_VALUE 1000

// Cambia questi valori solo se direzione o sterzo sono invertiti.
#define DRIVE_X_INVERTED false
#define DRIVE_Y_INVERTED false
#define LEFT_TRACK_INVERTED false
#define RIGHT_TRACK_INVERTED false

// Inizializza i due motori DC dei cingoli sulla shield.
void TrackController_begin(MotorController& controller);

// Applica il mixing differenziale di Joy1 ai due cingoli.
void TrackController_update(int driveX, int driveY);

// Disalimenta entrambi i cingoli.
void TrackController_stop();

#endif
