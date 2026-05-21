/*
PWM controller PCA9685

The PCA9685 is able to generate 16 indipendent channels PWM signals, with a 12 bit resolution, 4096 levels.
It has an internal clock at 25 MHz, and accept a clock signal of maximum 50 MHz.
Its output frequency can vary from 40 Hz to 1 kHz.
The IC is controlled through I2C protocol.

--CONFIGURATION--
The frequency is the same for all channels.
To set it we need to put the IC in sleep mode. This is possible by setting to TRUE the sleep bit in the MODE1 register.
Once the IC is in sleep mode we can write the frequency value inside the PRESCALE register (oxFE).
After that the IC is restarted by setting the bit RESTART in the MODE1 register.
Then it is set the auto-increment (AI) with bit 5 in MODE1 register.
Auto-increment is used to optimize channels activation.

--SINGLE CHANNEL ACTIONING--
The IC has 4 consecutive registers per channel.

Register	Dimension	Adress (per LED0)	Description
LED0_ON_L	8 bit (low)	0x6	                Low part of the value ON
LED0_ON_H	8 bit (high)	0x7	                High part of the value ON
LED0_OFF_L	8 bit (low)	0x8	                Low part of the value OFF
LED0_OFF_H	8 bit (high)	0x9	                High part of the value OFF

To get the right channel adress, we use the formula:
        adress = LED0_ON_L + (4 * channel_number)

To write the values in the register the uC uses the I2C library.
The first thing being sent to the IC is the register adress, then are sent the 4 bytes signal for that channel working mode.
The auto-incremet lets the uC send a 4 bytes signal instead than 4 byes separately, because it automatically increases the register adress.


--CONNECTIONS--

            PCA9685
        ---------------
     SCA|             |PWM0
     ---|             |-----
     SCL|             |PWM1
     ---|             |-----
        |             |PWM2
        |             |-----
        |             |PWM3
        |             |-----
        |             |PWM4
        |             |-----
        |             |PWM5
        |             |-----
        |             |PWM6
        |             |-----
        |             |PWM7
        |             |-----
        |             |PWM8
        |             |-----
        |             |PWM9
        |             |-----
        |             |PWM10
        |             |-----
        |             |PWM11
        |             |-----
        |             |PWM12
        |             |-----
        |             |PWM13
        |             |-----
        |             |PWM14
        |             |-----
        |             |PWM15
        |             |-----
        ---------------

*/




#ifndef __PWM_CONTROLLER_H__
#define __PWM_CONTROLLER_H__

#include "Arduino.h"

#define PCA9685_SUBADR1 0x2 //I2C Subaddress 1 for the PWM chip (used for grouping devices)
#define PCA9685_SUBADR2 0x3 //I2C Subaddress 2 for the PWM chip (used for grouping devices) 
#define PCA9685_SUBADR3 0x4 //I2C Subaddress 3 for the PWM chip (used for grouping devices)

#define PCA9685_MODE1 0x0 //Address of the MODE1 register used for principal mode configuration
#define PCA9685_PRESCALE 0xFE //Address of the PRESCALE register used for setting the PWM frequency

/*
Registers for the ON and OFF timing for channel 0.
Starting from these base addresses, you can calculate the addresses for the other 15 channels.
*/
#define LED0_ON_L 0x6 // Address for the low byte of channel 0's turn-on time
#define LED0_ON_H 0x7 // Address for the high byte of channel 0's turn-on time
#define LED0_OFF_L 0x8 // Address for the low byte of channel 0's turn-off time
#define LED0_OFF_H 0x9 // Address for the high byte of channel 0's turn-off time

/*
Register to control the ON and OFF time for all channels at the same time
*/
#define ALLLED_ON_L 0xFA // Address for the low byte of all channels' turn-on time
#define ALLLED_ON_H 0xFB // Address for the high byte of all channels' turn-on time
#define ALLLED_OFF_L 0xFC // Address for the low byte of all channels' turn-off time
#define ALLLED_OFF_H 0xFD // Address for the high byte of all channels' turn-off time


class PWMController {
 public:
  PWMController(uint8_t addr = 0x40); // Constructor, defaults to the standard 0x40 I2C address of the PCA9685
  void begin(void); //Function to initialize the I2C communication and resets the IC
  void reset(void); //Function to reset the IC by writing 0x0 to the main MODE1 register
  void setPWMFreq(float freq); //Function to set the IC PWM frequency (applied equally to all channels)
  void setPWM(uint8_t num, uint16_t on, uint16_t off); //Function to set the specific ON and OFF ticks for a single channel

 private:
  uint8_t _i2caddr; //Private variable to store the I2C address of the specific IC instance

  uint8_t read8(uint8_t addr); //Internal helper function to read a single byte from a specific IC register address
  void write8(uint8_t addr, uint8_t d); //Internal helper function to write a single byte 'd' to a specific IC register address 'addr'
};

#endif