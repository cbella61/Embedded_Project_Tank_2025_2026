
#include <Arduino.h>
#include <Wire.h>
#include "servoTorreta.h"
#include "udpReceiver.h"
#include <iostream>
using namespace std;



static unsigned long autoReturnTimer = 5;


#define JOYSTICK_X_PIN A0
#define ZERO_BUTTON_PIN 7

void setup() {
    Serial.begin(9600);

    pinMode(ZERO_BUTTON_PIN, INPUT_PULLUP);

    StepperTorretta_begin();
    UdpReceiver_begin();

    Serial.println("Stepper torretta pronto");
    Serial.println("Muovi il joystick a sinistra/destra");
    Serial.println("Premi il pulsante ZERO per impostare la posizione attuale come 0 gradi");
}

void loop() {
    TankCommand command = UdpReceiver_update();
    int joystickValue = command.joyX;
    StepperTorretta_updateJoystick(command.joyX);

    if (command.zeroPressed) {
        StepperTorretta_setZero();
        Serial.println("Zero impostato");
        delay(300);
    }

    static unsigned long lastPrint = 0;
    if (millis() - lastPrint > 500) {
        lastPrint = millis();

        Serial.print("Joystick: ");
        Serial.print(joystickValue);

        Serial.print(" | Angolo: ");
        Serial.println(StepperTorretta_getAngle());


        Serial.print(" | Connected: ");
        Serial.println(command.connected ? "Yes" : "No");
    }

}