# LEMAT – Piano Teaching Aid

**LEMAT (Learn Easy Music Any Time)** is an embedded piano teaching aid designed to help beginners learn key placement and note sequences through real-time sensing and visual guidance.

The system uses multiple Time-of-Flight sensors to detect hand and finger interaction across piano keys and provides real-time guidance through individually addressable LEDs, an embedded display, and audio feedback.

This project was developed for **UNSW ELEC3117 – Electrical Engineering Design Proficiency** in collaboration with [Matthew Nassif](https://www.linkedin.com/).

---

## 📄 Project Report

A complete technical report covering the system design, hardware development, firmware, testing, engineering decisions, and project outcomes is available here:

### **[View the full LEMAT Project Report](./LEMAT%20Report.pdf)**

The report provides substantially more detail on the engineering process behind LEMAT, including the design and integration of the sensing system, PCB and power system, embedded software, user interface, and prototype evaluation.

---

## Project Overview

LEMAT was designed as a compact embedded learning system that sits above a piano keyboard and guides beginner users through simple songs and exercises.

Rather than modifying the piano itself, the system uses external sensors positioned above the keys to detect interaction and provide feedback.

The device combines:

* Real-time piano key interaction sensing
* LED-based note guidance
* Song sequencing and lesson logic
* Display-based user feedback
* Audio output
* Custom embedded hardware
* Battery-powered operation
* Custom PCB and power management design

The project was developed as a complete **hardware-software embedded system**, involving sensor integration, firmware development, UI design, power management, PCB design, prototyping, testing, and debugging.

---

## Features

* **13-key real-time sensing** using VL53L1X Time-of-Flight sensors
* **WS2812 addressable LEDs** for visual note guidance
* Interactive song and lesson modes
* Embedded graphical user interface
* ILI9488 colour display
* Audio feedback
* Battery-powered operation
* Modular sensor architecture
* Custom PCB and sensor distribution hardware
* Multi-device I²C management
* Standalone embedded firmware

---

## Hardware

### Main Controller

* RP2040 microcontroller

### Sensors

* 13 × VL53L1X Time-of-Flight sensors

Each sensor monitors an individual piano key region and detects hand/finger interaction using distance measurements.

### Visual Feedback

* WS2812 individually addressable LEDs

The LEDs provide visual guidance by indicating which piano key the user should play.

### Display

* ILI9488 SPI colour display

The display provides the primary user interface for selecting lessons, songs, and interacting with the device.

### Audio

* PAM8302 audio amplifier
* Integrated speaker

### Power

* 2-cell Li-ion battery system
* TPS562200 buck converter
* TPS2121 power multiplexer

The power architecture supports portable battery operation while supplying the different voltage and current requirements of the controller, sensors, display, LEDs, and audio subsystem.

### PCB / Interconnect

* Custom 2-layer PCB
* Dedicated sensor distribution board
* JST-SH connectors for modular sensor connection

---

## Software Structure

The embedded firmware is organised into separate modules to isolate hardware control, sensing, UI operation, and lesson logic.

```text
main.py
│
├── config.py
│   └── System configuration and constants
│
├── hardware.py
│   └── Hardware initialisation and control
│
├── hardware_tests.py
│   └── Hardware testing routines
│
├── sensors.py
│   └── Multi-sensor management
│
├── vl53l1x.py
│   └── VL53L1X Time-of-Flight sensor driver
│
├── ui.py
│   └── User interface logic
│
├── ili9488.py
│   └── ILI9488 display driver
│
├── songs.py
│   └── Song definitions and note sequences
│
└── lessons.py
    └── Lesson and teaching logic
```

---

## Key Engineering Challenges

### Multi-Sensor I²C Addressing

All VL53L1X sensors use the same I²C address after power-up.

To operate **13 sensors simultaneously on the same I²C bus**, each sensor must first be individually controlled using its **XSHUT** pin.

During startup, the firmware:

1. Holds the sensors in shutdown.
2. Enables one sensor.
3. Assigns it a unique I²C address.
4. Repeats the process for each remaining sensor.

This allows all sensors to subsequently operate on the same bus without address conflicts.

---

### Sensor Reliability

The VL53L1X sensors rely on reflected infrared light to measure distance.

Sensor performance was therefore affected by factors including:

* Surface reflectivity
* Finger position
* Sensor mounting position
* Ambient conditions
* Detection threshold selection

Testing and calibration were required to achieve sufficiently reliable key interaction detection.

---

### Power Integrity

LEMAT combines several electrically different subsystems:

* RP2040 controller
* 13 Time-of-Flight sensors
* WS2812 LEDs
* Colour display
* Audio amplifier
* Speaker

Operating these simultaneously introduced challenges involving:

* Power distribution
* Voltage regulation
* Noise
* Current transients
* Battery operation

These required iterative hardware testing and power-system refinement.

---

### LED Stability

The WS2812 LEDs exhibited unstable behaviour under some battery-powered operating conditions.

This required investigation into:

* Supply voltage stability
* Grounding
* Power distribution
* Data signal integrity

The issue formed part of the wider hardware debugging and integration process.

---

## System Architecture

```text
                         ┌─────────────────┐
                         │      RP2040     │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
      VL53L1X Sensors       ILI9488 Display       WS2812 LEDs
        ×13 via I²C              via SPI
              │
              │
       Piano Key Sensing
              │
              ▼
        Lesson / Song
            Logic
              │
              ├───────────────────────────────┐
              │                               │
              ▼                               ▼
       Visual Guidance                  Audio Feedback
                                            │
                                      PAM8302 + Speaker
```

---

## Engineering Areas

The project involved work across several areas of electrical and computer engineering:

* Embedded systems
* Microcontroller programming
* Digital communication protocols
* I²C device management
* SPI peripherals
* Sensor integration
* PCB design
* Power electronics
* Battery-powered system design
* Hardware debugging
* Firmware architecture
* Human-machine interfaces
* Prototype development and testing

---

## Repository Contents

| File                   | Description                         |
| ---------------------- | ----------------------------------- |
| `main.py`              | Main firmware entry point           |
| `config.py`            | System configuration                |
| `hardware.py`          | Hardware initialisation and control |
| `hardware_tests.py`    | Hardware test routines              |
| `sensors.py`           | Sensor management                   |
| `vl53l1x.py`           | VL53L1X sensor driver               |
| `ui.py`                | User interface logic                |
| `ili9488.py`           | ILI9488 display driver              |
| `songs.py`             | Song definitions                    |
| `lessons.py`           | Lesson implementation               |
| **`LEMAT Report.pdf`** | **Full project technical report**   |

---

## Project Status

✅ **Completed**

LEMAT was successfully developed as a functional embedded-system prototype combining sensing, visual feedback, audio, UI, custom hardware, and embedded software.

Further technical details, design decisions, testing results, and project evaluation can be found in the:

### 📘 **[LEMAT Technical Project Report](./LEMAT%20Report.pdf)**

---

## Authors

**Leo** - 
Electrical Engineering / Computer Science
University of New South Wales

**Matthew Nassif** - 
Electrical Engineering
University of New South Wales

---

*LEMAT — Learn Easy Music Any Time*
