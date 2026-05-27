#include "messageEncode.h"

void messageEncode(message* message){
    char value[3];
    uint16_t track = 0;

    toString(message->mode, 1, value);
    message->string[track] = value[0];
    track ++;

    toString(message->lev1, 3, value);
    for(int i=0; i<3; i++){
        message->string[track] = value[i];
        track++;
    }

    toString(message->lev2, 3, value);
    for(int i=0; i<3; i++){
        message->string[track] = value[i];
        track++;
    }

    toString(message->lev3, 3, value);
    for(int i=0; i<3; i++){
        message->string[track] = value[i];
        track++;
    }

    toString(message->lev4, 3, value);
    for(int i=0; i<3; i++){
        message->string[track] = value[i];
        track++;
    }

    toString(message->fire, 1, value);
    message->string[track] = value[0];
    track ++;

    toString(message->horn, 1, value);
    message->string[track] = value[0];
    track++;

    message->string[track] = '\0';
}

void toString(uint16_t value, uint16_t size, char* message){
    uint16_t dim = 0;
    do{
        uint16_t digit = (value % 10);
        message[size - dim - 1] = digit + '0';
        value -= digit;
        value /= 10;
        dim++;
    }while(value > 0);

    uint16_t diff = size - dim;
    
    if(diff >= 0){
        for(int i=0; i<diff; i++){
            message[i] = '0';
        }
    }
}