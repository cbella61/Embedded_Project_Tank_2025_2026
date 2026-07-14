#ifndef UDP_SENDER_H
#define UDP_SENDER_H

#include <Arduino.h>

#include "joystickReader.h"

/*
 * INVIO UDP ESP32
 *
 * Questo modulo prende i dati letti da joystickReader e li manda al tank.
 * Il controller non controlla direttamente i motori: spedisce solo coordinate
 * e pulsanti usando il protocollo V1.
 */

// Avvia la connessione al tank. Se il WiFi cade, il modulo ritenta senza bloccare il loop.
void UdpSender_begin();

// Invia un comando ControllerData usando il protocollo UDP V1.
void UdpSender_send(const ControllerData& data);

#endif
