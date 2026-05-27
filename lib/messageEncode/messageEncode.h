/*
This library will be used by the controller to encode the command values into a string.
That string will be sent to the Tank via UDP.

The string will be formatted:
0 mode -> 0 freerange, 1 turret
1 dir1 -> direction of axis b of joystick d, 1 FORWARD, 2 BACKWARD, 3 BRAKE
2 - 3 level1 -> level of movement speed, from 0 to 10 for axis b of joystick d
4 dir2 -> direction of axis c of joystick d, 1 FORWARD, 2 BACKWARD, 3 BRAKE
5 - 6 level2 -> level of movement speed, from 0 to 10 for axis c of joystick d
7 dir3 -> direction of axis b of joystick e, 1 FORWARD, 2 BACKWARD, 3 BRAKE
8 - 9 level3 -> level of movement speed, from 0 to 10 for axis b of joystick e
10 dir4 -> direction of axis c of joystick e, 1 FORWARD, 2 BACKWARD, 3 BRAKE
11 - 12 level4 -> level of movement speed, from 0 to 10 for axis c of joystick e
13 fire -> button for cannon fire, 0 nothing, 1 fire
14 horn -> button for horn, 0 mute, 1 noise
15 string terminator
 */

#include "Arduino.h"

typedef struct message{
    uint16_t mode;
    uint16_t lev1; 
    uint16_t lev2; 
    uint16_t lev3; 
    uint16_t lev4;
    uint16_t fire;
    uint16_t horn;
    char* string;
}message;

void messageEncode(message* message);
void toString(uint16_t value, uint16_t size, char* message);