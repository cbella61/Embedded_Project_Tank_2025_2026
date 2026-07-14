# Remotely Controlled Tank

Firmware project for a tank based on an Arduino Uno R4 WiFi, an Emakefun PS2X & Motor Drive Board, and an ESP32 hand controller.

## Projects

- `tank/`: firmware for the Arduino Uno R4 WiFi on the tank.
- `controller-esp32/`: firmware for the ESP32 controller.
- `docs/tank_shield_wiring_guide.md`: current wiring and configuration guide.
- `docs/tank_shield_wiring_guide.pdf`: printable copy of the wiring guide.
- `docs/code_report.html`: complete explanation of the current firmware.
- `docs/code_report.pdf`: printable code report.

## Controls

| Input | Function |
| --- | --- |
| Joy1 X/Y | Differential drive for the two DC track motors |
| Joy2 X | Horizontal turret stepper |
| Joy2 Y | Paired elevation servos |
| GPIO25 button | Set logical turret zero and elevation zero |
| GPIO26 button | Fire relay pulse |

Both joystick modules are mounted rotated, so the controller firmware swaps
physical X and Y before sending the logical controls. The ESP32 calibrates all
four centers at startup; keep both sticks centered while it boots.

The ESP32 sends UDP packets to the tank access point:

```text
V1;driveX;driveY;turretX;elevationY;zero;fire
```

The tank creates the `Tank_AP` WiFi network and listens on UDP port `4210`.
If the connection drops, the ESP32 keeps running and retries the WiFi connection
every `3 seconds`; the tank stops safely after its `500 ms` UDP timeout.

## Build

```powershell
C:\Users\selmi\.platformio\penv\Scripts\pio.exe run -d tank
C:\Users\selmi\.platformio\penv\Scripts\pio.exe run -d controller-esp32
```

## Hardware Notes

- Left track DC motor: shield `M3`.
- Right track DC motor: shield `M1` (`M2` left unused if it spins by itself).
- Fire relay signal on tank: Arduino/shield `D7`.
- Relay module: `+` to 5V, `-` to GND, `S` to `D7`.
- Cannon output: use relay `COM` and `NO`; `NO` goes toward the cannon/load.
- Fire cooldown: one shot every `12 seconds`.
- Horizontal turret driver: `D2-D5` to driver `IN1-IN4`, with common ground.
- Elevation servos: `S5` and `S6`.
- Servo A uses `0-47` degrees; servo B is mirrored around `90` degrees.
- Differential turning reaches 55% at logical X 700, 70% at 999, and 100% from 1000.
- The tank firmware checks for the PCA9685 shield at I2C address `0x60`, `0x40`, or `0x7F` during startup.

Use the wiring guide for supply, jumper, and signal-pin details.
