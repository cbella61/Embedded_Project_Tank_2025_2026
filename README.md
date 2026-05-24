# Remotely Controlled Tank - Embedded Systems Project 2025/2026

Welcome to the official repository for the **Remotely Controlled Tank**, a prototype developed for the Embedded Systems course (2025-2026). This project focuses on building a fully functional, network-controlled robotic vehicle with articulated movement and precise aiming capabilities.

## 📖 Table of Contents
- [Introduction](#introduction)
- [Hardware & Components](#hardware--components)
- [Mechanical Implementation](#mechanical-implementation)
- [Controller Architecture](#controller-architecture)
- [Communication Protocol](#communication-protocol)
- [How to Run / Installation](#how-to-run--installation)
- [Future Improvements](#future-improvements)
- [Team Members](#team-members)

## 🚀 Introduction
The core of this system is the **Arduino Uno R4 WiFi** microcontroller, which manages all operational aspects. By leveraging the integrated ESP32-S3 on the Arduino, the tank hosts a web server that serves as the primary control interface, allowing for remote operation via a network connection.

## 🛠 Hardware & Components
### Core Components:
- **Arduino Uno R4 WiFi**: Main microcontroller and web server host.
- **EmakeFun PS2X & Motor Drive Board**: Primary motor driver interface.
- **2x DC Motors**: For independent track movement.
- **2x Servomotors**: Dedicated to the vertical inclination of the cannon muzzle (maximum vertical rotation of 45 degrees).
- **1x Stepper Motor & Driver**: Used for the lateral/horizontal rotation of the turret, allowing a rotation of 45 degrees to both sides.
- **High-Voltage Electromagnetic Cannon DIY Kit**: Serving as the main firing mechanism (DC3V).
- **Battery**: 3300mAh capacity, 7.4V to power the system.

## ⚙️ Mechanical Implementation
- **Mobility**: The tank utilizes **LEGO tracks** driven by two independent DC motors. This setup enables differential steering for agile maneuverability.
- **Weapon System**: The turret incorporates precise control mechanisms. The stepper motor provides accurate lateral panning (±45 degrees), while the two servomotors handle the vertical tilting of the muzzle (max 45 degrees). The main payload is an electromagnetic cannon kit.

## 🎮 Controller Architecture
The remote controller is custom-built using an **ESP32** and includes:
- **2x Analog Joysticks**: Used for tank movement (track control) and turret aiming.
- **Switch**: To toggle between operating modes (e.g., movement mode vs. turret mode).
- **Status LED**: Indicates if the connection with the tank has been successfully established.

## 📡 Communication Protocol
Communication between the controller and the tank is handled via **UDP** over WiFi. 
- The tank acts as an **Access Point** with the static IP address: `192.168.4.115`.
- Data is transmitted using a specific 15-character formatted string:
  - `[0]` **Mode**: `m` (movement) or `t` (turret).
  - `[1-4]` **Speed 1**: First track speed/direction, or overall tank direction/speed (max 4096).
  - `[5-8]` **Speed 2**: Second track speed/direction, or turret vertical inclination (± degrees, max 4096).
  - `[9-12]` **Turret Pan**: Turret horizontal rotation (± 180degrees, for a 360spin).
  - `[13]` **Fire**: Firing action state.
  - `[14]` **Terminator**: String terminator character.

*(Note: The team is currently evaluating whether to handle string pre-processing on the controller side or directly on the tank).*

## 💻 How to Run / Installation

This project is built using **PlatformIO** within **Visual Studio Code (VSCode)**. 

### Prerequisites
1. Download and install [Visual Studio Code](https://code.visualstudio.com/).
2. Install the **PlatformIO IDE** extension from the VSCode Extensions Marketplace.
3. Make sure you have the required USB drivers installed for both the ESP32 (Controller) and the Arduino Uno R4 WiFi (Tank).

### Setup and Build Instructions
1. **Clone the Repository**:
   Open your terminal and run:
   ```bash
   git clone https://github.com/Cbella61/Embedded_Project_Tank_2025_2026.git
   ```
2. **Open Project**:
   Open the cloned folder in VSCode. PlatformIO will automatically read the `platformio.ini` file and configure the project (downloading toolchains and library dependencies).
3. **Select the Environment**: 
   Since this repository contains code for both the ESP32 (controller) and the Arduino Uno R4 (tank), make sure to select the correct build environment from the PlatformIO project taskbar at the bottom of the screen (e.g., `env:esp32` or `env:uno_r4_wifi`).
4. **Compile / Build**:
   Click the **"Build"** icon (the checkmark `✓` in the bottom bar) to compile the code. Ensure there are no compilation errors.
5. **Upload Firmware**:
   Connect your target microcontroller (ESP32 or Arduino) via USB. Click the **"Upload"** icon (the right arrow `→` in the bottom bar) to flash the compiled code.
6. **Serial Monitor** (Optional):
   Use the **"Serial Monitor"** icon (the plug shape) to view debug prints over UART.

## 🔮 Future Improvements
- **Cannon Incline Calculator**: Integration of an accelerometer to calculate tilt.
- **Target Distance Measurement**: Using an ultrasound sensor to calculate the tank's distance from the target.
- **Automated Firing System**: Implementation of a state machine for automatic loading and firing of the cannon.


## 👥 Team Members
- **Christian Bella**
- **Selmir Kusi**
- **Francesco Martella**
- **Alice Sedioli**
