#include "PWMController.h"
#include <Wire.h>
#if defined(ARDUINO_SAM_DUE) //Checks if the code is being compiled for an Arduino Due (SAM architecture)
 #define WIRE Wire1 //The Due usually uses Wire1 for standard I2C, so we alias WIRE to Wire1
#else //For all other standard Arduino boards (Uno, Mega, Nano, etc.)
 #define WIRE Wire //Alias WIRE to the standard Wire object
#endif


PWMController::PWMController(uint8_t addr) { //Class constructor taking the I2C address as an argument
  _i2caddr = addr; //Stores the provided address into the private class variable '_i2caddr'
}

void PWMController::begin(void) {
 WIRE.begin(); //Initializes the I2C bus as a master device
 reset(); //Calls the class reset method to put the IC in a known default state
}


void PWMController::reset(void) { //Method to software-reset the PCA9685 chip
 write8(PCA9685_MODE1, 0x0); //Writes 0x00 to the MODE1 register, waking it up and clearing special modes
}

/*
This function sets the PWM frequency on the IC, based on its 25MHz internal clock.
The 0.98 multiplier is used to correct for slight inaccuracies and overshooting of the internal oscillator.
Prescaleval is based on the formula prescaleval = round((25000000 / (4096 * freq))) - 1
*/
void PWMController::setPWMFreq(float freq){
  freq *= 0.98; //For frequency overshoot prevention

  //The end_freq variable is used to set the frequency of the PWM signal
  // Calculates the raw prescaler value needed to achieve the target frequency
  float endFreqVal = (25000000 / (4096 * freq)) - 1; //25MHz clock / (12-bit resolution * freq) minus 1
  uint8_t endFreq = floor(endFreqVal + 0.5); //Adds 0.5 and floors the result to mathematically round to the nearest integer

  
  uint8_t oldMode = read8(PCA9685_MODE1); //Reads the current configuration from the MODE1 register
  uint8_t newMode = (oldMode&0x7F) | 0x10; //Masks out the restart bit (0x7F) and sets the sleep bit (0x10) to prepare for prescaler update
  write8(PCA9685_MODE1, newMode); //Writes the new mode, putting the IC into sleep mode (oscillator off)
  write8(PCA9685_PRESCALE, endFreq); //Writes the calculated prescaler value to the PRESCALE register (only works during sleep)
  write8(PCA9685_MODE1, oldMode); //Restores the previous mode, waking the IC back up (clears sleep bit)
  delay(5); //Waits 5 milliseconds to allow the internal oscillator to stabilize after waking up
  write8(PCA9685_MODE1, oldMode | 0xa1); //Writes the old mode back while explicitly setting the Auto-Increment (0x20) and Restart (0x80) bits (0x80+0x20+0x01=0xa1)

}

void PWMController::setPWM(uint8_t num, uint16_t on, uint16_t off) { //Method to set the ON and OFF points for a specific channel (0-15)
  //Serial.print("Setting PWM "); Serial.print(num); Serial.print(": "); Serial.print(on); Serial.print("->"); Serial.println(off);

  WIRE.beginTransmission(_i2caddr); //Starts an I2C transmission to the device's address
  WIRE.write(LED0_ON_L+4*num); //Writes the base register address for the targeted channel (calculates offset using 'num')
  WIRE.write(on); //Writes the lower 8 bits of the 12-bit 'ON' time value
  WIRE.write(on>>8); //Bitwise shifts the 'ON' value right by 8 to w
  WIRE.write(off); //Writes the lower 8 bits of the 12-bit 'OFF' time value
  WIRE.write(off>>8); //Bitwise shifts the 'OFF' value right by 8 to write the upper 4 bits
  WIRE.endTransmission(); //Completes the I2C transmission and pushes the data onto the bus
}

uint8_t PWMController::read8(uint8_t addr) { //Helper method to read a single byte from a specific IC register
  WIRE.beginTransmission(_i2caddr); //Starts an I2C transmission to the device
  WIRE.write(addr); //Writes the target register address we want to read from
  WIRE.endTransmission(); //Ends the transmission, effectively setting the register pointer inside the IC

  WIRE.requestFrom((uint8_t)_i2caddr, (uint8_t)1); //Requests exactly 1 byte of data from the device address
  return WIRE.read(); //Reads and returns the requested byte from the I2C buffer
}

void PWMController::write8(uint8_t addr, uint8_t d) { //Helper method to write a single byte to a specific IC register
  WIRE.beginTransmission(_i2caddr); //Starts an I2C transmission to the device
  WIRE.write(addr); //Writes the target register address we want to write to
  WIRE.write(d); //Writes the single byte of data 'd' into the previously specified register
  WIRE.endTransmission(); //Completes the transmission and pushes the data to the device
}
