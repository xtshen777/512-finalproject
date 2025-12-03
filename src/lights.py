# Handles all LED feedback for the device, including rainbow animations,
# static colors during gameplay, and move-specific color indicators.

import time
import board
import neopixel
from rainbowio import colorwheel
import config


class Lights:
    def __init__(self):
        # Initialize NeoPixel (1 LED) on pin D10
        self.pixels = neopixel.NeoPixel(
            board.D10,
            1,
            brightness=0.3,
            auto_write=False
        )

        # Current lighting behavior mode
        self.mode = "idle"

        # Stores the current move color when in "move" mode
        self.current_move = None

        # Internal counter used for smooth rainbow animation
        self._rainbow_pos = 0.0

    # Set a single RGB color on the LED
    def _set_color(self, color):
        self.pixels[0] = color
        self.pixels.show()

    # Set color based on the required move type
    def _set_move_color(self, move):
        # Map each gameplay action to a specific color
        if move == config.MOVE_CW:
            color = (255, 255, 0)          # Rotate right: yellow
        elif move == config.MOVE_CCW:
            color = (0, 255, 255)          # Rotate left: cyan
        elif move == config.MOVE_PRESS:
            color = (0, 255, 0)            # Button press: green
        elif move == config.MOVE_SHAKE:
            color = (255, 255, 255)        # Shake: white
        else:
            color = (0, 0, 0)              # Fallback: off

        self._set_color(color)

    def set_mode(self, mode, move=None):
        """
        Called by game_engine to change light behavior.

        Modes:
            "splash"      Startup screen rainbow animation
            "menu"        Difficulty selection rainbow animation
            "playing"     Game has started, static background color
            "move"        Show the color associated with the current move
            "game_start"  Flash color when entering the first level
            "game_over"   Red indicator when time is up
            "idle"        LED off
        """
        self.mode = mode
        self.current_move = move

        # Splash and menu both use continuous rainbow animations
        if mode in ("splash", "menu"):
            # Rainbow is handled inside update()
            return

        # Other modes use static single colors
        if mode == "idle":
            self._set_color((0, 0, 0))

        elif mode == "game_start":
            # Entry effect when beginning a level
            self._set_color((0, 0, 150))

        elif mode == "playing":
            # Dim blue background during gameplay
            self._set_color((0, 0, 40))

        elif mode == "move":
            # Show action feedback color
            self._set_move_color(move)

        elif mode == "game_over":
            # Solid red indicator
            self._set_color((200, 0, 0))

        else:
            # Default off for any unknown mode
            self._set_color((0, 0, 0))

    def update(self, dt):
        """
        Called every frame in code.py.
        Used for non-blocking animations like rainbow cycling.

        dt = time elapsed since last frame, used to control speed smoothly.
        """

        # Rainbow animation only applies in certain UI screens
        if self.mode in ("splash", "menu"):
            # Move the rainbow cursor based on passed time
            # Adjust 120 to change the animation speed
            self._rainbow_pos = (self._rainbow_pos + 120 * dt) % 255

            # Convert position to colorwheel value
            idx = int(self._rainbow_pos) & 255
            self.pixels[0] = colorwheel(idx)
            self.pixels.show()

