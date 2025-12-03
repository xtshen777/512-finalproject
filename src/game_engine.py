import time
import random
import config


class Game:
    """
    Core game state machine.

    This class coordinates:
    - High level game states (splash, menu, level start, wait input, win, game over)
    - Difficulty and level progression
    - Move sequence generation and timing
    - Communication with input manager, display, and light controller
    """

    def __init__(self, inputs, display, lights):
        """
        Initialize the game with shared subsystems.

        Parameters:
        - inputs: InputManager instance for rotary encoder, button, and shake
        - display: Display instance for OLED output
        - lights: Lights instance for NeoPixel effects
        """
        self.inputs = inputs
        self.display = display
        self.lights = lights

        # Initial high level state
        self.state = "SPLASH"
        self.difficulty = "EASY"
        self.level = 1

        # Sequence of moves for the current level
        self.sequence = []
        self.seq_index = 0

        # Move timing parameters
        self.current_move = config.MOVE_PRESS
        self.per_move_time = 1.0
        self.move_start_time = time.monotonic()

        # Menu UI flags and button hold tracking
        self.menu_needs_redraw = True
        self.menu_press_start = None  # Time stamp when button is first held in the menu

        # Cooldown window to avoid one action being counted multiple times
        self.action_cooldown_until = 0.0

        # Power on animation and splash:
        # Start in splash light mode and play the animated splash screen once.
        self.lights.set_mode("splash")
        self.display.play_splash_animation()

    def update(self, dt):
        """
        Main update entry point for the game state machine.

        Called every frame from code.py, with dt being the elapsed time
        since the previous frame. Each high level state is handled by
        its own private method.
        """
        if self.state == "SPLASH":
            self._state_splash()
        elif self.state == "MENU":
            self._state_menu()
        elif self.state == "LEVEL_START":
            self._state_level_start()
        elif self.state == "WAIT_INPUT":
            self._state_wait_input()
        elif self.state == "GAME_OVER":
            self._state_game_over()
        elif self.state == "GAME_WIN":
            self._state_game_win()

    def render(self):
        """
        Optional render hook.

        Currently all drawing is triggered directly inside each state method
        by calling Display methods, so this function is kept as a placeholder
        for possible future separation of update and render.
        """
        pass

    # --------------- State: Splash Screen ---------------

    def _state_splash(self):
        """
        Splash state shown only on power up.

        The animated splash has already been played in __init__.
        Here we just:
        - Keep NeoPixel in splash mode
        - Wait for a single button press to enter the menu
        """
        # Keep rainbow splash lights active
        self.lights.set_mode("splash")

        # Single press on the encoder button jumps to the difficulty menu
        if self.inputs.button_pressed:
            print("SPLASH: button pressed, go to MENU")
            self.state = "MENU"
            self.menu_needs_redraw = True
            # Use a different rainbow mode for the menu
            self.lights.set_mode("menu")

    # --------------- State: Difficulty Menu ---------------

    def _state_menu(self):
        """
        Difficulty selection state.

        Player uses the rotary encoder to cycle through difficulty options.
        Long press on the encoder button starts the game.
        """
        # During menu, use menu style rainbow lights
        self.lights.set_mode("menu")

        # Redraw only when needed to avoid display flickering
        if self.menu_needs_redraw:
            self.display.show_menu(self.difficulty)
            self.menu_needs_redraw = False

        # Use encoder rotation to change difficulty
        if self.inputs.rotated_cw:
            self.difficulty = self._next_difficulty()
            self.menu_needs_redraw = True
            print("MENU: rotate CW, diff =", self.difficulty)
        elif self.inputs.rotated_ccw:
            self.difficulty = self._prev_difficulty()
            self.menu_needs_redraw = True
            print("MENU: rotate CCW, diff =", self.difficulty)

        # Long press detection for starting the game
        if self.inputs.button_down:
            # First frame where the button is detected as down
            if self.menu_press_start is None:
                self.menu_press_start = time.monotonic()
            else:
                # Compute how long the button has been held
                held = time.monotonic() - self.menu_press_start
                if held >= config.MENU_PRESS_HOLD:
                    print("MENU: long press to start game, held =", held)
                    self.level = 1
                    self.state = "LEVEL_START"
                    # Actual light mode switch for gameplay happens in _state_level_start
                    self.menu_press_start = None
        else:
            # Button released, reset long press timer
            self.menu_press_start = None

    # --------------- State: Start a New Level ---------------

    def _state_level_start(self):
        """
        Level setup state.

        This state:
        - Configures level length and timing based on difficulty
        - Randomly generates a sequence of moves
        - Resets sequence index and timers
        - Switches light mode to gameplay and then transitions to WAIT_INPUT
        """
        # Switch lights to standard playing mode for active gameplay
        self.lights.set_mode("playing")

        # Look up difficulty parameters
        params = config.DIFFICULTIES[self.difficulty]
        base_moves = params["base_moves"]
        total_time = params["level_time"]

        # Each level adds one extra move on top of the base
        # Level 1: base_moves
        # Level 2: base_moves + 1
        # Level 3: base_moves + 2
        seq_len = base_moves + (self.level - 1)

        # Randomly generate a sequence of moves for this level
        self.sequence = [random.choice(config.ALL_MOVES) for _ in range(seq_len)]
        self.seq_index = 0
        self.current_move = self.sequence[0]

        # Per move time budget is the total time divided by number of moves
        self.per_move_time = total_time / seq_len
        self.move_start_time = time.monotonic()

        print(
            "LEVEL_START:",
            "difficulty =", self.difficulty,
            "level =", self.level,
            "seq_len =", seq_len,
            "total_time =", total_time,
            "per_move_time =", self.per_move_time,
        )

        # Update HUD and lights for the first move in this level
        self.display.show_level(
            self.level,
            self.difficulty,
            len(self.sequence),
            self.seq_index,
            self.current_move,
            1.0,
        )
        self.state = "WAIT_INPUT"
        self.lights.set_mode("move", self.current_move)

        # Reset inter move cooldown for the new level
        self.action_cooldown_until = 0.0

    # --------------- State: Wait for Player Input ---------------

    def _state_wait_input(self):
        """
        Active gameplay state.

        Logic:
        - Check if the current move has timed out
        - Respect a cooldown window so a single action cannot advance multiple steps
        - Check if the player performed the correct input
        - Advance to the next move or next level or win / game over
        """
        now = time.monotonic()

        # Check per move timeout first
        if now - self.move_start_time > self.per_move_time:
            print("WAIT_INPUT: time up, game over")
            self.state = "GAME_OVER"
            self.display.show_game_over()
            self.lights.set_mode("game_over")
            return

        # Ignore inputs during cooldown to avoid double counting a single action
        if now < self.action_cooldown_until:
            return

        # Check if the expected move has been completed
        if self._is_move_correct(self.current_move):
            print("WAIT_INPUT: correct move", self.current_move)

            # Start cooldown window before accepting the next move
            self.action_cooldown_until = now + config.ACTION_COOLDOWN

            self.seq_index += 1

            # All moves for this level are complete
            if self.seq_index >= len(self.sequence):
                self.level += 1
                if self.level > config.TOTAL_LEVELS:
                    # Player has completed all levels
                    print("GAME_WIN: passed all levels")
                    self.state = "GAME_WIN"
                    self.display.show_game_win()
                    self.lights.set_mode("game_win")
                else:
                    # Advance to the next level
                    self.state = "LEVEL_START"
                return

            # Move to the next action within the current level
            self.current_move = self.sequence[self.seq_index]
            self.move_start_time = now  # Reset timing for the next move
            self.display.show_level(
                self.level,
                self.difficulty,
                len(self.sequence),
                self.seq_index,
                self.current_move,
                1.0,
            )
            self.lights.set_mode("move", self.current_move)

    # --------------- State: Game Over / Win ---------------

    def _state_game_over(self):
        """
        Game over state.

        The light mode has already been set to "game_over".
        A single button press returns the player to the menu and re enables
        the menu rainbow lights.
        """
        if self.inputs.button_pressed:
            self.state = "MENU"
            self.menu_needs_redraw = True
            self.display.show_menu(self.difficulty)
            self.lights.set_mode("menu")

    def _state_game_win(self):
        """
        Game win state.

        Similar to game over, a button press sends the player back to
        the difficulty menu.
        """
        if self.inputs.button_pressed:
            self.state = "MENU"
            self.menu_needs_redraw = True
            self.display.show_menu(self.difficulty)
            self.lights.set_mode("menu")

    # --------------- Difficulty Cycling and Move Checking ---------------

    def _next_difficulty(self):
        """
        Cycle difficulty to the next value in the fixed order.
        EASY -> MEDIUM -> HARD -> EASY
        """
        order = ["EASY", "MEDIUM", "HARD"]
        idx = order.index(self.difficulty)
        return order[(idx + 1) % len(order)]

    def _prev_difficulty(self):
        """
        Cycle difficulty to the previous value in the fixed order.
        EASY <- MEDIUM <- HARD <- EASY
        """
        order = ["EASY", "MEDIUM", "HARD"]
        idx = order.index(self.difficulty)
        return order[(idx - 1) % len(order)]

    def _is_move_correct(self, move_name):
        """
        Check if the player's input matches the expected move.

        Mapping:
        - MOVE_CW    uses inputs.rotated_cw
        - MOVE_CCW   uses inputs.rotated_ccw
        - MOVE_PRESS uses a single press edge, not just button down
        - MOVE_SHAKE uses the shake flag from the accelerometer
        """
        if move_name == config.MOVE_CW:
            return self.inputs.rotated_cw
        if move_name == config.MOVE_CCW:
            return self.inputs.rotated_ccw
        if move_name == config.MOVE_PRESS:
            # Only respond to the press edge, not a held button
            return self.inputs.button_pressed
        if move_name == config.MOVE_SHAKE:
            return self.inputs.shake_detected
        return False
