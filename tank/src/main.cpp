/*#include <Arduino.h>
#include <Wire.h>
//#include "PWMController.h"
#include "motorController.h"

// PWM FUNZIONA!!!!


MotorController MC = MotorController(50);

void setup() {
  Wire.begin();
  Serial.begin(9600);
  MC.begin();
}
//da
void loop() {

  MC.servoTurn(S1, 180);

  MC.DCrun(M2, FORWARD, 3200);
  MC.DCrun(M4, FORWARD, 3200);
  delay(1000);
  MC.DCbrakeAll();
  delay(500);
  MC.DCrun(M2, FORWARD, 3200);
  MC.DCrun(M4, BACKWARD, 3200); 
  delay(1000);
  MC.DCbrakeAll();
  delay(500);
  MC.DCrun(M2, BACKWARD, 3200);
  MC.DCrun(M4, BACKWARD, 3200);
  delay(1000);
  MC.DCbrakeAll();
  MC.servoTurn(S1, 0);
  delay(500);

  
}*/