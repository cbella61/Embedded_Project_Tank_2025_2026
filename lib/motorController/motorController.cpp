#include "motorController.h"

MotorController::MotorController(int freq){
    this->freq = freq;
    PWM = PWMController(0x60);
}

void MotorController::begin(){
    /*
    PWM controller initialization
    */
    PWM.begin();
    PWM.setPWMFreq(freq);
}

void MotorController::DCrun(int motorNumber, int direction, int speed){
    int vel = speed;
    if(vel > MAX_SPEED) vel = MAX_SPEED;
    switch(motorNumber){
        case M1:
            setPWM(PWM1, vel);
            if(direction == FORWARD) setPin(IN1, HIGH);
            else setPin(IN1, LOW);
            break;

        case M2:
            setPWM(PWM2, vel);
            if(direction == FORWARD) setPin(IN2, HIGH);
            else setPin(IN2, LOW);
            break;

        case M3:
            setPWM(PWM3, vel);
            if(direction == FORWARD) setPin(IN3, HIGH);
            else setPin(IN3, LOW);
            break;

        case M4:
            setPWM(PWM4, vel);
            if(direction == FORWARD) setPin(IN4, HIGH);
            else setPin(IN4, LOW);

    }
}

void MotorController::DCbrake(int motorNumber){
    switch(motorNumber){
        case M1:
            setPWM(PWM1, 0);
            setPin(IN1, LOW);
            break;

        case M2:
            setPWM(PWM2, 0);
            setPin(IN2, LOW);
            break;

        case M3:
            setPWM(PWM3, 0);
            setPin(IN3, LOW);
            break;

        case M4:
            setPWM(PWM4, 0);
            setPin(IN4, LOW);

    }
}
void MotorController::DCbrakeAll(){
    setPWM(PWM1, 0);
    setPin(IN1, LOW);
    setPWM(PWM2, 0);
    setPin(IN2, LOW);
    setPWM(PWM3, 0);
    setPin(IN3, LOW);
    setPWM(PWM4, 0);
    setPin(IN4, LOW);
}

void MotorController::setPin(int pin, bool value){
    if(value == HIGH)
        PWM.setPWM(pin, 4096, 0);
    else    
        PWM.setPWM(pin, 0, 0);
}

void MotorController::setPWM(int pin, int value){
    if(value > 4095)
        PWM.setPWM(pin, 4096, 0);
    else    
        PWM.setPWM(pin, 0, value);
}

/*
 * 
 * SERVO
 * 
 */

 
/*
Servo degree -> pulse
p = 1ms -90deg, p = 1.5ms 0 deg, p = 2ms 90deg
f = 50Hz, T = 20ms
d 1% = 0,2ms
d 10% = 2ms max
d 5% = 1ms min
Levels -> 4096
lmax = 4096/10 = 409
lmin = 4096/20 = 205
degrees from 0 to 180.
ldiff = lmax - lmin = 204
l = (ldiff / 180) * deg + lmin
*/
void MotorController::servoTurn(int servoNumber, int degree){
    int deg = degree;
    if(deg > 180) deg = 180;
    float level = LMAX - LMIN;
    level /= 180;
    level *= deg;
    level += LMIN;
    int l = level;
    Serial.println(level);
    Serial.println(l);
    switch(servoNumber){
        case S1:
            setPWM(S1, l);
            break;
        case S2:
            setPWM(S2, l);
            break;
        case S3:
            setPWM(S3, l);
            break;
        case S4:
            setPWM(S4, l);
            break;
        case S5:
            setPWM(S5, l);
            break;
        case S6:
            setPWM(S6, l);
            break;
        case S7:
            setPWM(S7, l);
            break;
        case S8:
            setPWM(S8, l);
    }


}

/*
 * 
 * STEPPER
 * 
 */

void MotorController::setStepperMotors(int stepper, int motor1, int motor2){
    switch (stepper)
    {
    case SM1:
        steppers[0][0] = motor1;
        steppers[0][1] = motor2;
        stepIndex[0] = 1;
        break;

    case SM2:
        steppers[1][0] = motor1;
        steppers[1][1] = motor2;
        stepIndex[1] = 1;
        break;
    
    default:
        break;
    }
}

void MotorController::stepperTurn(int stepper, int steps, int direction, int mode){

    switch(direction){
        case FORWARD:
            stepIndex[stepper-1] += 2;
            if(stepIndex[stepper-1] > 7) stepIndex[stepper-1] = 0; //Gets back to sequence start
            break;

        case BACKWARD:
            stepIndex[stepper-1] -= 2;
            if(stepIndex[stepper-1] < 0) stepIndex[stepper-1] = 7; //Gets back to sequence end
            break;
        
        default:

            break;
    }

}

void MotorController::singleStep(int stepper, int mode){
    uint8_t latch_state = 0; //Sets all motors to 0
    switch(mode){
        case SINGLE:
            if(stepIndex[stepper-1] % 2) stepIndex[stepper-1]++; //If not on even step
            if(stepIndex[stepper-1] > 7) stepIndex[stepper-1] = 0; //Gets back to sequence start
            break;

        case DOUBLE:
            if(!(stepIndex[stepper-1] % 2)) stepIndex[stepper-1]++; //If not on odd step
            if(stepIndex[stepper-1] > 7) stepIndex[stepper-1] = 1; //Gets back to sequence start
            break;

        default:
            break;
    }

    switch (stepIndex[stepper-1]) {
      case 0:
        latch_state |= 0x1; // energize coil 1 only
        break;
      case 1:
        latch_state |= 0x3; // energize coil 1+2
        break;
      case 2:
        latch_state |= 0x2; // energize coil 2 only
        break;
      case 3:
        latch_state |= 0x6; // energize coil 2+3
        break;
      case 4:
        latch_state |= 0x4; // energize coil 3 only
        break;
      case 5:
        latch_state |= 0xC; // energize coil 3+4
        break;
      case 6:
        latch_state |= 0x8; // energize coil 4 only
        break;
      case 7:
        latch_state |= 0x9; // energize coil 1+4
        break;
    }

    if (latch_state & 0x1) {
      DCrun(steppers[stepper-1][0], FORWARD, 4095);
    }
    if (latch_state & 0x2) {
      DCrun(steppers[stepper-1][1], FORWARD, 4095);
    }
    if (latch_state & 0x4) {
      DCrun(steppers[stepper-1][0], BACKWARD, 4095);
    }
    if (latch_state & 0x8) {
      DCrun(steppers[stepper-1][1], BACKWARD, 4095);
    }
}

void MotorController::stepperRelease(int stepper){
    DCbrake(steppers[stepper][0]);
    DCbrake(steppers[stepper][1]);
}

