# ACTION GBA

An interactive physical rhythm and reaction game inspired 90s style game with the shape of enclosure of the classic game console Game Boy Advance.

## Overview

`ACTION GBA` is a hardware based reaction game that challenges players to complete a sequence of physical actions under time pressure.
The device displays each required action on a SSD1306 128x64 OLED screen, and the player must respond correctly using:

- A rotary encoder (rotate left or right, press)

- A shake gesture detected through an ADXL345 accelerometer

Each new level increases difficulty by adding more moves and reducing available time per action.
The game also includes animated startup spash, colorful NeoPixel feedback, and multiple difficulty modes.

## File Structure
```
512-finalproject/
│
├── README.md                 # Project overview and instructions
│
├── src/                      # All source code files and libraries
│   ├── code.py
│   ├── inputs.py
│   ├── display_ui.py
│   ├── lights.py
│   ├── game_engine.py
│   ├── config.py
│   └── lib/                  # Any CircuitPython libraries used
│       ├── adafruit_adxl34x.mpy
│       ├── adafruit_displayio_ssd1306.mpy
│       ├── neopixel_spi.mpy
│       ├── neopixel.mpy
│       ├── rainbow.mpy
│       └── adafruit_bus_device/    
│
└── Documentation/            # Circuit Diagram + System Diagram
    ├── Circuit Diagram.jpg
    ├── Circuit Diagram.kicad_sch
    └── Sysrtem Diagram.jpg
```

## Features
### Core Gameplay

- Randomized action sequences each level

- Real time gesture detection

- Game states: Splash screen, Menu, Level start, Gameplay, Game over, Game win

- Per move time limits based on difficulty

- 4 supported actions:

    - Rotate right

    - Rotate left

    - Button press

    - Shake

### Interface and Visual Feedback

- OLED centered UI layout

- Boot animation only when powered on

- Dynamic NeoPixel modes:

    - Rainbow during splash and menu

    - Static colors during gameplay

    - Individual colors for each move

    - Red for game over

## Difficulty Modes

Each difficulty determines both the starting number of moves per level and the total time available per level.

| Difficulty | Level 1 | Level 10 | Total Time per Level |
| ---------- | --------| -------- | -------------------- |
| **Easy**   | 2 moves | 12 moves | **20 seconds**       |
| **Medium** | 4 moves | 14 moves | **20 seconds**       |
| **Hard**   | 6 moves | 16 moves | **20 seconds**       |

Each new level adds one more move, extending the sequence and reducing time per move.

## User Controls

### Supported Actions

- Rotate Right: Turn encoder clockwise

- Rotate Left: Turn encoder counterclockwise

- Press: Press down the encoder button

- Shake: Shake the enclosure and strong shake detected by ADXL345

### Menu Navigation

- Rotate to switch difficulty

- Long press to start game

## Hardware Used

- Xiao ESP32C3 Microcontroller running CircuitPython

- ADXL345 accelerometer

- Rotary encoder with push button

- SSD1306 128x64 OLED display

- NeoPixel RGB LED 

- LiPo Battery

- On/Off Switch

## Gameplay Flow

### 1. Power On

- Animated splash screen

- NeoPixel rainbow effect

### 2. Menu

- Rotate encoder to choose difficulty

- Long press to begin

### 3. Level Start

- Random sequence generated

- Time per move calculated

### 4. Gameplay

- Perform the shown action

- Complete all moves to advance

### 5. Game Win / Game Over

- Press to return to menu

## Running the Game

1. Copy the entire `src/` folder into your CircuitPython device.

2. Ensure the `lib` contains all required CircuitPython libraries.

3. Power the device via USB or battery.

4. Play **ACTION GBA**!