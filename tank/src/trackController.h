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

// Protezione finale del comando cingolo nella scala UDP 0--1023.
// Viene applicata sia prima sia dopo il mixing differenziale: non deve coincidere
// con DRIVE_INPUT_DEADZONE dell'ESP32, che filtra soltanto il rumore del joystick.
// Se da fermo un lato prova ancora a muoversi, aumenta di 10/20 e riprova sul tank fisico.
#define TRACK_COMMAND_DEADZONE 40

// Ogni cingolo usa una porta motore DC della shield.
// M2 resta libero: usa M3 per il sinistro e M1 per il destro.
#define LEFT_TRACK_MOTOR M1
#define RIGHT_TRACK_MOTOR M3

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

// Frequenza massima di refresh I2C quando il comando resta invariato.
// Un nuovo comando e uno stop di sicurezza non aspettano il periodo successivo.
#define TRACK_COMMAND_REFRESH_INTERVAL_MS 20

// Lo sterzo Joy1 X e' lineare: nessuna curva o soglia intermedia nascosta.
// La sua intensita' entra direttamente nel mixing differenziale sotto.

// L'orientamento degli assi del joystick viene corretto una sola volta sull'ESP32.
// Qui restano esclusivamente le inversioni dovute al cablaggio dei due motori.
#define LEFT_TRACK_INVERTED false
#define RIGHT_TRACK_INVERTED false

// Inizializza i due motori DC dei cingoli sulla shield.
void TrackController_begin(MotorController& controller);

// Applica il mixing differenziale lineare di Joy1 ai due cingoli.
void TrackController_update(int driveX, int driveY);

// Porta entrambi i cingoli a PWM zero tramite DCbrake().
void TrackController_stop();

#endif
