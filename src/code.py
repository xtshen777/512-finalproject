import time
import board

from inputs import InputManager
from display_ui import Display
from lights import Lights
from game_engine import Game


def main():
    """
    Main entry point of the Rhythm GBA game.
    Initializes all hardware interfaces and managers, then enters
    the main update loop that keeps the game running.
    """

    # Initialize a shared I2C bus used by both OLED and accelerometer
    # The ESP32 board maps SCL to D5 and SDA to D4 in this project
    i2c = board.I2C()

    # Input manager handles rotary encoder input, button press,
    # and accelerometer-based shake detection
    inputs = InputManager(i2c)

    # Display controller manages the SSD1306 OLED screen
    display = Display(i2c)

    # LED controller manages NeoPixel lighting effects for the game
    lights = Lights()

    # Game engine handles all game states, difficulty logic,
    # sequences, timers, and interactions with input and display
    game = Game(inputs, display, lights)

    # Track time between frames for delta-time updates
    last = time.monotonic()

    # Main game loop
    while True:
        now = time.monotonic()
        dt = now - last   # Time elapsed since previous frame
        last = now

        # Read inputs from encoder, button, and accelerometer
        inputs.update()

        # Update the game state machine
        game.update(dt)

        # Update lighting animations
        lights.update(dt)

        # Reduce CPU load and stabilize update frequency
        time.sleep(0.01)


# Run the application
main()
