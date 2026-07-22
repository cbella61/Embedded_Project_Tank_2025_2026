# Wi-Fi Remote-Controlled Tank

Embedded project for a Wi-Fi remote-controlled tank. An ESP32 controller reads two joysticks and two buttons, then sends UDP commands to an Arduino Uno R4 WiFi mounted on the tank. The Arduino controls the tracks, turret rotation and elevation, and the cannon relay.

> YouTube video: [Project demonstration](https://youtu.be/Sw5uwZuhA9w)

> Project presentation: [Group presentation](docs/tank_wifi_embedded_project.pdf)

## Features

- differential drive for the two tracks.
- horizontal turret rotation using a stepper motor.
- turret elevation using two mirrored servo motors.
- logical zeroing of turret and elevation.
- relay control with a limited pulse and cooldown interval.
- Wi-Fi/UDP communication between the controller and the tank.
- safe stop and rearming after a communication loss.
- editable CAD model and exports for manufacturing/3D printing.

## Requirements

### Hardware

The project uses the following hardware components:

| Quantity | Component | Purpose |
| ---: | --- | --- |
| 1 | Arduino Uno R4 WiFi | Tank controller and Wi-Fi access point |
| 1 | ESP32 Dev Module | Handheld controller |
| 1 | Emakefun PS2X & Motor Drive Board | Drives the DC motors and servos; includes a PCA9685 PWM chip |
| 2 | DC motors with tracks | Tank movement |
| 1 | 28BYJ-48 stepper motor with driver | Horizontal turret rotation |
| 2 | TowerPro SG90 servos, or equivalent | Turret elevation |
| 2 | Analog joystick modules | Driving, turret rotation, and elevation |
| 2 | Momentary push buttons | Zeroing and relay control |
| 1 | 5 V relay module | Controls the cannon load |
| 1 | 7.4 V battery | Tank and servo power supply |
| - | Wires, connectors, screws, and printed parts | Wiring and mechanical assembly |

For pin assignments, power supply, jumpers, and safety precautions, see the [wiring guide](docs/tank_shield_wiring_guide.md) and its [PDF version](docs/tank_shield_wiring_guide.pdf).

### Software

- [Visual Studio Code](https://code.visualstudio.com/) with the PlatformIO extension, or PlatformIO Core.
- Arduino framework, installed automatically by PlatformIO.
- appropriate USB drivers for the serial ports of both boards.
- [Autodesk Fusion 360](https://www.autodesk.com/products/fusion-360/overview) on Windows or alternative softwares (like [FreeCAD](https://www.freecad.org/)) on Linux, to design and edit the CAD model.
- [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) to prepare the parts for 3D printing.

The repository includes the project's application code, including the local `PWMController` and `motorController` drivers. Platform dependencies (Arduino core, WiFiS3, and WiFi/ESP32) are provided by the PlatformIO-selected frameworks and are not duplicated in this repository.

### Tools used by the team

- Visual Studio Code and PlatformIO for firmware development and upload.
- Autodesk Fusion 360 for the mechanical CAD design and editable assemblies.
- OrcaSlicer for slicing and preparing the components for 3D printing.


## Project Layout

```text
.
├── tank/                       # Arduino Uno R4 WiFi firmware on the tank
│   ├── src/                    # UDP receiver, tracks, turret, and relay
│   └── lib/                    # Local PCA9685 and motor-shield drivers
├── controller-esp32/           # ESP32 handheld-controller firmware
│   └── src/                    # Joystick reading and UDP transmission
├── cad/                        # Source files, editable assemblies, and 3D exports
│   ├── source/                 # Parametric Fusion 360/OpenSCAD sources
│   ├── stl/                    # 3D-printable parts
│   └── reference/              # Technical notes and component references
├── docs/                       # Project presentation, wiring guide and motor-shield manual
└── README.md                   # This guide
```

## Essential Wiring

| Function | Connection |
| --- | --- |
| Left track | Shield port `M3` |
| Right track | Shield port `M1` |
| Turret stepper driver | Arduino `D2`–`D5` to `IN1`–`IN4`, with a common GND |
| Elevation servo A | Shield port `S5` |
| Elevation servo B | Shield port `S6` |
| Relay | `D7` signal, 5 V, and GND |
| Controller joystick 1 | ESP32 GPIO `34` and `32` |
| Controller joystick 2 | ESP32 GPIO `35` and `33` |
| Zero button | ESP32 GPIO `25` to GND |
| Fire button | ESP32 GPIO `26` to GND |

Do not power motors and servos from USB alone. Before the first test, lift the tracks off the ground and follow the verification section of the [wiring guide](docs/tank_shield_wiring_guide.md).

## Build, Flash, and Run

### 1. Setup

1. Clone the repository and open its root folder in VS Code/PlatformIO.
2. Connect the Arduino Uno R4 WiFi to the PC using USB.
3. Connect the ESP32 to the PC using USB.
4. Verify that the hardware connections match the wiring guide.

### 2. Build

From PowerShell in the repository root:

```powershell
pio run -d tank
pio run -d controller-esp32
```

Alternatively, use the **Build** command in PlatformIO after opening `tank` and `controller-esp32`, respectively.

### 3. Flash

Upload each firmware to its corresponding board:

```powershell
pio run -d tank --target upload
pio run -d controller-esp32 --target upload
```

If both boards are connected, select the correct serial port in PlatformIO or temporarily add `upload_port` to the relevant `platformio.ini` file.

### 4. Run

1. Power the tank on: the Arduino and shield initialize the motors and create the `Tank_AP` access point on UDP port `4210`.
2. Power the ESP32 controller on while keeping both joysticks centered.
3. The controller calibrates the joysticks and connects to `Tank_AP` automatically.
4. Once the system receives consecutive neutral commands, the actuators are armed.

## User Guide

| Control | Action |
| --- | --- |
| Joy1 Y | Forward/reverse driving |
| Joy1 X | Differential steering or turn-in-place |
| Joy2 X | Horizontal turret rotation |
| Joy2 Y | Raise/lower the turret |
| Zero button (GPIO25) | Sets the logical zero position of turret and elevation |
| Fire button (GPIO26) | Activates a 200 ms relay pulse |

The relay only accepts a new command after a 12-second cooldown. If the tank does not receive valid UDP packets within the configured timeout, it stops motion and disables the relay. After a timeout or reconnection, release the buttons and center the joysticks to allow rearming.

## Documentation and Materials

- [Editable wiring guide](docs/tank_shield_wiring_guide.md)
- [Wiring guide PDF](docs/tank_shield_wiring_guide.pdf)
- [Emakefun PS2X & Motor Drive Board manual](docs/PS2X_MotorDriveBoard_InstructionManual_V1.4.pdf)
- [YouTube project demonstration](https://youtu.be/Sw5uwZuhA9w)


## Team Members and Contributions

Most of the project work was carried out collaboratively by the whole team. The file and subsystem division below identifies the main responsibility or the most significant contribution of each member; it is not intended to imply that the other members did not participate in, review, test, or support those activities.

| Team member | Contribution |
| --- | --- |
| Francesco Martellla | `controller-esp32/src/main.cpp` and `tank/src/main.cpp`, technical drawing, CAD work with Alice and Selmir, 3D-printing work with Alice |
| Alice Sedioli | `controller-esp32/src/joystickReader.*`, `controller-esp32/src/udpSender.*`, and `tank/src/udpReceiver.*`, UDP communication with Selmir and Christian, CAD work with Francesco and Selmir, 3D-printing work with Francesco |
| Christian Bella | `tank/lib/PWMController/*` and `tank/lib/motorController/*`; UDP communication with Alice and Selmir, component selection, local hardware-library implementation |
| Selmir Kusi | `tank/src/servoTorretta.*` and `tank/src/trackController.*`, UDP communication with Alice and Christian, turret and track control, CAD work with Alice and Francesco |

### Shared contributions

- **Technical drawing:** Francesco prepared the technical drawings.
- **Component selection:** Christian contributed to selecting the electronic and electromechanical components.
- **CAD design:** Alice, Selmir, and Francesco collaborated on the Fusion 360 model design.
- **3D printing:** Alice and Francesco prepared the parts' models using OrcaSlicer and printed them at FabLab UniTrento.
- **UDP communication:** Alice, Selmir, and Christian collaborated on the communication path between the ESP32 controller and the Arduino tank, including packet transmission, reception, and safe timeout behavior.
- **Turret and tracks:** Selmir implemented the turret and track-control logic.
- **Libraries:** Christian implemented the local PWM and motor-control libraries used by the tank firmware.

## License

See [LICENSE](docs/license).
