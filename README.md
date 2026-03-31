# Remotely Controlled Tank - Embedded Systems Project 2025/2026

Welcome to the official repository for the **Remotely Controlled Tank**, a prototype developed for the Embedded Systems course (2025-2026). This project focuses on building a fully functional, network-controlled robotic vehicle with articulated movement and precise aiming capabilities.

## 📖 Table of Contents
- [Introduction](#introduction)
- [Hardware & Components](#hardware--components)
- [Mechanical Implementation](#mechanical-implementation)
- [Controller Architecture](#controller-architecture)
- [Communication Protocol](#communication-protocol)
- [Future Improvements](#future-improvements)
- [Team Members](#team-members)

## 🚀 Introduction
The core of this system is the **Arduino Uno R4 WiFi** microcontroller, which manages all operational aspects. By leveraging the integrated ESP32-S3 on the Arduino, the tank hosts a web server that serves as the primary control interface, allowing for remote operation via a network connection.

## 🛠 Hardware & Components
### Core Components:
- **Arduino Uno R4 WiFi**: Main microcontroller and web server host.
- **EmakeFun PS2X & Motor Drive Board**: Primary motor driver interface.
- **2x DC Motors**: For independent track movement.
- **2x Servomotors**: For the turret (horizontal rotation) and the cannon muzzle (vertical inclination).
- **Laser Module**: For pointing and aiming assistance.
- **Buzzer**: Functions as an audible signal/horn.

*Note: Power supply/batteries are currently under evaluation for type and voltage.*

## ⚙️ Mechanical Implementation
- **Mobility**: The tank utilizes **LEGO tracks** driven by two independent DC motors. This setup enables differential steering for agile maneuverability.
- **Weapon System**: The turret incorporates precise control mechanisms using servomotors for both horizontal panning and vertical tilting, ensuring accurate aiming.

## 🎮 Controller Architecture
The remote controller is custom-built using an **ESP32** and includes:
- **2x Analog Joysticks**: Used for tank movement (track control) and turret aiming.
- **Push Button**: For firing the cannon.
- **Switch**: To toggle between operating modes (e.g., movement mode vs. turret mode).
- **Status LED**: Indicates if the connection with the tank has been successfully established.

## 📡 Communication Protocol
Communication between the controller and the tank is handled via **UDP** over WiFi. 
- The tank acts as an **Access Point** with the static IP address: `192.168.4.115`.
- Data is transmitted using a specific 15-character formatted string:
  - `[0]` **Mode**: `m` (movement) or `t` (turret).
  - `[1-4]` **Speed 1**: First track speed/direction, or overall tank direction/speed (max 4096).
  - `[5-8]` **Speed 2**: Second track speed/direction, or turret vertical inclination (± degrees, max 4096).
  - `[9-12]` **Turret Pan**: Turret horizontal rotation (± degrees, max 4096).
  - `[13]` **Fire**: Firing action state.
  - `[14]` **Terminator**: String terminator character.

*(Note: The team is currently evaluating whether to handle string pre-processing on the controller side or directly on the tank).*

## 🔮 Future Improvements
- **Cannon Incline Calculator**: Integration of an accelerometer to calculate tilt.
- **Target Distance Measurement**: Using an ultrasound sensor to calculate the tank's distance from the target.
- **Automated Firing System**: Implementation of a state machine for automatic loading and firing of the cannon.
- **Web UI Enhancements**: Adding a trajectory angle suggestion feature via the web server interface.

## 👥 Team Members
- **Christian Bella**
- **Selmir Kusi**
- **Francesco Martella**
- **Alice Sedioli**
