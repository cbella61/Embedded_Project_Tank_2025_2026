# Tank 3D model
This folder contains the editable mechanical model of the tank.

## Folder structure

- `source/`: parametric sources and the native Autodesk Fusion file.
- `stl/`: parts ready for 3D printing, generated only after dimension confirmation.
- `reference/`: table of confirmed dimensions and assembly notes.

The model is divided into components:

1. lower deck with battery, Arduino, and DC motor cable routing;
2. upper deck with driver, turret PCB, and vertical cable passage;
3. rotating turret base driven by the stepper motor;
4. upper tilting support actuated by two servos;
5. straight cannon fixed to the tilting section, excluding the lateral straps/bars
   shown in the reference.

## Official mechanical references

The official Arduino UNO R4 WiFi STEP model is kept in
`reference/vendor/arduino_uno_r4_wifi/`. It is used only as a dimensional reference.

The TowerPro SG90 dimensions and the manufacturer link are in
`reference/vendor/towerpro_sg90/README.md`.
