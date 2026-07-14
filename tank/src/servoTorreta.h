#ifndef SERVO_TORRETA_H
#define SERVO_TORRETA_H

#include <Arduino.h>

#include "motorController.h"

/*
 * TORRETTA
 *
 * Questo modulo gestisce due movimenti diversi:
 *
 * 1. Torretta orizzontale:
 *    - e' uno stepper con driver esterno
 *    - i segnali del driver sono collegati ai pin digitali D2-D5
 *    - usa la sequenza A, B, C, D come nel vecchio codice che funzionava
 *
 * 2. Elevazione:
 *    - usa due servo collegati alla shield su S5 e S6
 *    - i due servo si muovono specchiati per alzare/abbassare insieme
 */

// ===== CONFIGURAZIONE TORRETTA ORIZZONTALE =====

// Numero di step usato per convertire la posizione logica della torretta in gradi.
#define STEPS_PER_REV 2048

// Mappa fisica: driver torretta A/B/C/D collegato alle porte digitali della shield.
#define TURRET_DRIVER_A_PIN 2
#define TURRET_DRIVER_B_PIN 3
#define TURRET_DRIVER_C_PIN 4
#define TURRET_DRIVER_D_PIN 5

// Piu' alto significa torretta piu' lenta.
#define TURRET_STEP_INTERVAL_MS 2

// Valori joystick vicino al centro che non muovono torretta o elevazione.
#define TURRET_JOYSTICK_DEADZONE 200

// Inizializza lo stepper orizzontale della torretta.
void StepperTorretta_begin();

// Legge Joy2 X: sotto centro gira a sinistra, sopra centro gira a destra.
void StepperTorretta_updateJoystick(int joystickValue);

// Azzera solo il conteggio logico, non muove fisicamente il motore.
void StepperTorretta_setZero();

// Spegne tutti i segnali A/B/C/D del driver.
void StepperTorretta_stop();

// Ritorna l'angolo logico calcolato dagli step fatti.
int StepperTorretta_getAngle();

// Inizializza i due servo che alzano e abbassano la torretta.
void ServoTorretta_begin(MotorController& controller);

// Legge Joy2 Y e cambia gradualmente l'angolo dei servo.
void ServoTorretta_updateJoystick(int joystickValue);

// Imposta direttamente l'angolo di elevazione, rispettando i limiti.
void ServoTorretta_setAngle(int angle);

// Porta l'elevazione alla posizione logica minima.
void ServoTorretta_setZero();

// Ritorna l'angolo logico attuale dei servo.
int ServoTorretta_getAngle();

#endif
