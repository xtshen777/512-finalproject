# inputs.py
import time
import math
import digitalio
from adafruit_adxl34x import ADXL345

import config


class InputManager:
    def __init__(self, i2c):
        # 旋钮 A 相
        self.encA = digitalio.DigitalInOut(config.ENCODER_PIN_A)
        self.encA.switch_to_input(pull=digitalio.Pull.UP)

        # 旋钮 B 相
        self.encB = digitalio.DigitalInOut(config.ENCODER_PIN_B)
        self.encB.switch_to_input(pull=digitalio.Pull.UP)
        self.lastA = self.encA.value

        # 旋钮按键
        self.button = digitalio.DigitalInOut(config.ENCODER_BUTTON)
        self.button.switch_to_input(pull=digitalio.Pull.UP)
        self._last_button = self.button.value

        # 加速度计
        self.accel = ADXL345(i2c)
        x, y, z = self.accel.acceleration
        mag = math.sqrt(x * x + y * y + z * z)
        self._last_mag = mag
        self._last_shake_time = time.monotonic()

        # 旋钮冷却时间
        self._last_rotate_time = time.monotonic()

        self.reset_actions()

    def reset_actions(self):
        self.rotated_cw = False
        self.rotated_ccw = False
        self.button_pressed = False   # 本帧是否检测到“按下瞬间”
        self.button_down = False      # 本帧是否处于按住状态
        self.shake_detected = False

    def update(self):
        self.reset_actions()

        # 旋钮左右: 简单检测 + 冷却时间，避免一转算多次
        currentA = self.encA.value
        currentB = self.encB.value
        now = time.monotonic()

        if currentA != self.lastA:
            if now - self._last_rotate_time > config.ROTATE_COOLDOWN:
                if currentA == currentB:
                    self.rotated_cw = True
                    # print("ENC: CW")
                else:
                    self.rotated_ccw = True
                    # print("ENC: CCW")
                self._last_rotate_time = now
        self.lastA = currentA

        # 按钮: 只认 高 -> 低 的“按下瞬间”，避免抖动和松手也触发
        now_btn = self.button.value          # 未按 True, 按下 False
        self.button_down = (not now_btn)

        if self._last_button and not now_btn:
            self.button_pressed = True
            # print("BTN pressed edge")

        self._last_button = now_btn

        # 摇晃检测，加异常保护
        try:
            x, y, z = self.accel.acceleration
        except OSError:
            return

        mag = math.sqrt(x * x + y * y + z * z)
        delta_mag = abs(mag - self._last_mag)

        print("delta_mag =", delta_mag)

        self._last_mag = mag
        now = time.monotonic()

        # 只有在超過下限才視為 SHAKE，並且加冷卻時間
        if (
            delta_mag >= config.SHAKE_DELTA_THRESHOLD
            and now - self._last_shake_time > config.SHAKE_COOLDOWN
        ):
            self.shake_detected = True
            self._last_shake_time = now
            print("SHAKE DETECTED, delta_mag =", delta_mag)

