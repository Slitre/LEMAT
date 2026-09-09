# LEMAT – Piano Teaching Aid

LEMAT is an embedded piano teaching aid designed to help beginners learn key placement and note sequences through real-time sensing and visual guidance.

The system uses multiple time-of-flight sensors to detect hand/finger interaction across piano keys and provides feedback using individually addressable LEDs, with additional display and audio support.

This project was completed for a university course (ELEC3117). The partner of the project was Matthew Nassif [(LinkedIn Profile)](https://www.linkedin.com/in/matthew-nassif-742663318/). 

---

## Project Overview

The aim of this project was to create a compact embedded learning system that could sit above a piano keyboard and guide the user through simple songs and exercises.

The device combines:

- Real-time key interaction sensing
- LED-based note guidance
- Song sequencing
- Display-based user feedback
- Audio output
- Custom embedded hardware and power design

The project was developed as a complete hardware-software system, including sensor integration, embedded firmware, UI logic, power management and PCB design.

---

## Features

- Multi-key sensing using VL53L1X Time-of-Flight sensors
- LED guidance using WS2812 addressable LEDs
- Song playback and lesson sequencing
- Embedded user interface
- Display output
- Audio feedback
- Modular sensor control
- Custom hardware integration

---

## Hardware

### Main Controller
- RP2040 microcontroller

### Sensors
- 13 × VL53L1X Time-of-Flight sensors

### Visual Feedback
- WS2812 addressable LEDs

### Display
- ILI9488 SPI display

### Audio
- PAM8302 audio amplifier
- Small speaker

### Power
- 2-cell Li-ion battery system
- TPS562200 buck converter
- TPS2121 power multiplexer

### PCB / Interconnect
- Custom 4-layer PCB
- Dedicated sensor distribution board
- JST-SH connectors for sensor modules

---

## Software Structure

The firmware is split into multiple modules:

- `main.py` – main application entry point
- `config.py` – system configuration
- `hardware.py` – hardware initialisation and control
- `hardware_tests.py` – hardware test routines
- `sensors.py` – sensor management
- `vl53l1x.py` – VL53L1X sensor driver
- `ui.py` – user interface logic
- `ili9488.py` – display driver
- `songs.py` – song definitions
- `lessons.py` – lesson and teaching logic

---

## Key Engineering Challenges

### Multi-Sensor I2C Addressing

All VL53L1X sensors start with the same default I2C address, so each sensor must be enabled individually using the XSHUT pin and assigned a unique address during startup.

This required careful sequencing and debugging to ensure all sensors initialised reliably.

### Sensor Reliability

Reflective surfaces and physical sensor positioning affected distance measurements, requiring calibration and testing to improve detection consistency.

### Power Integrity

Running multiple sensors, LEDs, the display and audio hardware from the same power system introduced power and noise issues.

These were addressed through power distribution design, regulation and hardware debugging.

### LED Stability

LED behaviour became unstable under certain battery-powered conditions, requiring investigation into supply integrity and signal behaviour.

---

## System Architecture

```text
                    ┌─────────────────┐
                    │     RP2040      │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
      VL53L1X Sensors    ILI9488 Display   WS2812 LEDs
         (x13, I2C)          (SPI)            │
             │                                │
             └───────────────┬────────────────┘
                             │
                          User Input

                    ┌─────────────────┐
                    │   Audio Output  │
                    │ PAM8302 + Spk   │
                    └─────────────────┘
