#ifndef UDP_RECEIVER_H
#define UDP_RECEIVER_H

#include <Arduino.h>

/*
 * RICEVITORE UDP DEL TANK
 *
 * Questo modulo crea la rete WiFi del tank e legge i comandi del controller.
 * Il main non deve sapere come funziona WiFi/UDP: riceve solo un TankCommand
 * gia' pronto da usare.
 */

// Comando completo ricevuto dal controller ESP32.
// Tutti gli assi sono in scala 0-1023, con centro a circa 512.
struct TankCommand {
    // Joy1: guida differenziale.
    int driveX;
    int driveY;

    // Joy2: torretta orizzontale ed elevazione.
    int turretX;
    int elevationY;

    // Pulsanti.
    bool zeroPressed;
    bool firePressed;

    // true solo quando i pacchetti validi sono recenti e il riarmo neutro
    // e' stato completato. false significa che nessun attuatore va comandato.
    bool connected;
};

// Inizializza AP/UDP in stato disarmato; le attese tra retry non bloccano e
// i tentativi vengono eseguiti da UdpReceiver_update().
void UdpReceiver_begin();

// Legge il pacchetto piu' recente o restituisce valori sicuri se scatta il timeout.
TankCommand UdpReceiver_update();

#endif
