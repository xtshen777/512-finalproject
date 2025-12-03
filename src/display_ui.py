import time
import board
import displayio
import terminalio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306


class Display:
    """
    Display controller for the 128x64 SSD1306 OLED.
    Responsible for rendering all UI states including:
    - Animated splash screen
    - Difficulty menu
    - Game HUD (levels and move instructions)
    - Game Over / Game Win screens
    """

    def __init__(self, i2c):
        """
        Initialize the OLED display through a shared I2C bus.
        The SSD1306 driver requires releasing any previously active
        display objects on CircuitPython before reinitializing.
        """
        displayio.release_displays()

        # Construct the display bus using the shared I2C instance
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)

        # Initialize the 128x64 OLED
        self.display = adafruit_displayio_ssd1306.SSD1306(
            display_bus, width=128, height=64
        )

        # Root group for all drawn elements
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

        # Clear screen on startup
        self.clear()

    # -----------------------------------------------------
    # Core Utility Methods
    # -----------------------------------------------------

    def clear(self):
        """
        Clears the screen by resetting the display group.
        Ensures new content draws cleanly without residual artifacts.
        """
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

    def _text_center(self, txt, y):
        """
        Draw centered text horizontally on the OLED.

        Parameters:
        - txt: string to render
        - y: vertical pixel coordinate
        """
        text_obj = label.Label(terminalio.FONT, text=txt)

        # Compute width using the label bounding box
        w = text_obj.bounding_box[2]
        text_obj.x = int((128 - w) / 2)  # Center horizontally
        text_obj.y = y

        self.main_group.append(text_obj)

    # Legacy absolute-position text method (kept for backward compatibility)
    def _text(self, txt, x, y):
        text_obj = label.Label(terminalio.FONT, text=txt, x=x, y=y)
        self.main_group.append(text_obj)

    # -----------------------------------------------------
    # Animated Splash Screen
    # -----------------------------------------------------

    def play_splash_animation(self):
        """
        Plays a short vertical slide-in animation for the startup screen.
        This animation only plays once at power-up (not on game restart).

        Implementation strategy:
        - Start title/subtitle below visible screen
        - Move upward for a fixed number of frames
        - Finish in static splash screen layout
        """

        self.clear()

        title = label.Label(terminalio.FONT, text="ACTION GBA")
        subtitle = label.Label(terminalio.FONT, text="Press to start")

        # Helper to center label horizontally
        def center_x(lbl):
            w = lbl.bounding_box[2]
            lbl.x = int((128 - w) / 2)

        center_x(title)
        center_x(subtitle)

        # Start positions (off-screen below)
        start_title_y = 80
        start_sub_y = 100

        # Target positions (final resting positions)
        target_title_y = 20
        target_sub_y = 42

        title.y = start_title_y
        subtitle.y = start_sub_y

        # Add labels to group so animation is visible
        self.main_group.append(title)
        self.main_group.append(subtitle)

        # Short, fast animation: ~0.3 seconds total
        frames = 15
        for i in range(frames):
            ratio = (i + 1) / frames
            title.y = int(start_title_y + (target_title_y - start_title_y) * ratio)
            subtitle.y = int(start_sub_y + (target_sub_y - start_sub_y) * ratio)
            time.sleep(0.02)

        # Snap to exact final location for clean result
        title.y = target_title_y
        subtitle.y = target_sub_y

        # Transition into the standard splash screen
        self.show_splash()

    # -----------------------------------------------------
    # UI Screens
    # -----------------------------------------------------

    def show_splash(self):
        """
        Static splash screen shown immediately after the animation.
        """
        self.clear()
        self._text_center("ACTION GBA", 20)
        self._text_center("Press to start", 42)

    def show_menu(self, difficulty):
        """
        Difficulty selection screen.

        Parameters:
        - difficulty: currently selected difficulty (EASY / MEDIUM / HARD)
        """
        self.clear()
        self._text_center("Select Difficulty", 12)
        self._text_center("> " + difficulty, 32)
        self._text_center("Press to confirm", 52)

    def show_game_over(self):
        """
        Game Over screen displayed when the player runs out of time
        or performs the wrong move.
        """
        self.clear()
        self._text_center("GAME OVER", 22)
        self._text_center("Press to retry", 44)

    def show_game_win(self):
        """
        Screen displayed when the player clears all 10 levels.
        """
        self.clear()
        self._text_center("YOU WIN!", 22)
        self._text_center("Press to replay", 44)

    def show_level(self, level, difficulty, seq_len, index, move, ratio_unused):
        """
        HUD shown during gameplay, updated each time the expected move changes.

        Parameters:
        - level: current level (1–10)
        - difficulty: selected difficulty
        - seq_len: total actions in this level
        - index: current action number
        - move: move name (ROTATE, PRESS, SHAKE, etc.)
        - ratio_unused: placeholder for potential progress bar
        """
        self.clear()
        self._text_center(f"Diff: {difficulty}", 10)
        self._text_center(f"Level: {level}", 22)
        self._text_center(f"Move: {index + 1}/{seq_len}", 34)
        self._text_center("Do: " + move, 46)
