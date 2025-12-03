import time
import math
import digitalio
from adafruit_adxl34x import ADXL345

import config


class InputManager:
    """
    Handles all physical inputs for the game:
    - Rotary encoder rotation (CW and CCW)
    - Rotary encoder push-button press
    - Accelerometer-based shake gesture

    This module abstracts raw hardware signals into clean event flags
    that the game engine can read each frame.
    """

    def __init__(self, i2c):
        """
        Initialize hardware interfaces for the encoder and accelerometer.
        """

        # Rotary encoder channel A (quadrature signal)
        self.encA = digitalio.DigitalInOut(config.ENCODER_PIN_A)
        self.encA.switch_to_input(pull=digitalio.Pull.UP)

        # Rotary encoder channel B (quadrature signal)
        self.encB = digitalio.DigitalInOut(config.ENCODER_PIN_B)
        self.encB.switch_to_input(pull=digitalio.Pull.UP)
        self.lastA = self.encA.value  # Track previous A state for direction detection

        # Rotary encoder push button (active low)
        self.button = digitalio.DigitalInOut(config.ENCODER_BUTTON)
        self.button.switch_to_input(pull=digitalio.Pull.UP)
        self._last_button = self.button.value  # Save previous button state

        # Initialize ADXL345 accelerometer
        # Compute initial magnitude for shake comparison
        self.accel = ADXL345(i2c)
        x, y, z = self.accel.acceleration
        mag = math.sqrt(x * x + y * y + z * z)
        self._last_mag = mag
        self._last_shake_time = time.monotonic()

        # Encoder rotation cooldown to prevent multiple triggers per step
        self._last_rotate_time = time.monotonic()

        # Initialize event flags
        self.reset_actions()

    def reset_actions(self):
        """
        Reset all per-frame input flags.
        This ensures that actions are only detected once per frame.
        """
        self.rotated_cw = False
        self.rotated_ccw = False
        self.button_pressed = False   # True only on rising edge (one-frame pulse)
        self.button_down = False      # True while held down
        self.shake_detected = False

    def update(self):
        """
        Poll all hardware inputs and update event flags.
        This method should be called once per frame from code.py.
        """
        self.reset_actions()

        # -------------------------------
        # Rotary Encoder Rotation
        # -------------------------------

        currentA = self.encA.value
        currentB = self.encB.value
        now = time.monotonic()

        # If A changed, a rotation occurred
        if currentA != self.lastA:
            # Apply cooldown so only one step is counted
            if now - self._last_rotate_time > config.ROTATE_COOLDOWN:
                # Determine direction using quadrature logic
                if currentA == currentB:
                    self.rotated_cw = True
                else:
                    self.rotated_ccw = True

                self._last_rotate_time = now

        self.lastA = currentA

        # -------------------------------
        # Button Press Detection
        # -------------------------------

        now_btn = self.button.value      # High = not pressed, Low = pressed
        self.button_down = (not now_btn)

        # Button press edge: last = high, now = low
        if self._last_button and not now_btn:
            self.button_pressed = True

        self._last_button = now_btn

        # -------------------------------
        # Accelerometer Shake Detection
        # -------------------------------

        try:
            x, y, z = self.accel.acceleration
        except OSError:
            # Sometimes the ADXL345 may fail to read briefly.
            # In that case, skip the shake detection for this frame.
            return

        # Compute magnitude and compare change since last frame
        mag = math.sqrt(x * x + y * y + z * z)
        delta_mag = abs(mag - self._last_mag)

        # Debug print used during tuning
        print("delta_mag =", delta_mag)

        self._last_mag = mag
        now = time.monotonic()

        # Detect shake only when above threshold and cooldown elapsed
        if (
            delta_mag >= config.SHAKE_DELTA_THRESHOLD
            and now - self._last_shake_time > config.SHAKE_COOLDOWN
        ):
            self.shake_detected = True
            self._last_shake_time = now
            print("SHAKE DETECTED, delta_mag =", delta_mag)
