# code.py
import time
import board

from inputs import InputManager
from display_ui import Display
from lights import Lights
from game_engine import Game


def main():
    # 在这里只创建一次 I2C
    i2c = board.I2C()  # 共享 SCL D5 和 SDA D4

    inputs = InputManager(i2c)
    display = Display(i2c)
    lights = Lights()
    game = Game(inputs, display, lights)

    last = time.monotonic()

    while True:
        now = time.monotonic()
        dt = now - last
        last = now

        inputs.update()
        game.update(dt)
        lights.update(dt)

        time.sleep(0.01)


main()
 
