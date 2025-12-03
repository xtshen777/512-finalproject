import board

# ----------------------------------------
# Rotary Encoder Pin Assignments
# ----------------------------------------
# Quadrature encoder output pins A and B.
# Values are read to detect clockwise and counterclockwise rotation.
ENCODER_PIN_A = board.D1
ENCODER_PIN_B = board.D2

# Encoder push-button (active low).
# This is used for both the MENU long-press confirmation
# and the in-game "PRESS" action.
ENCODER_BUTTON = board.D9


# ----------------------------------------
# NeoPixel Configuration
# ----------------------------------------
# RGB LED pin and count.
# These LEDs are used for game feedback:
# - Rainbow for splash/menu
# - Color-coded move indications
# - Red for game over, etc.
NEOPIXEL_PIN = board.D10
NEOPIXEL_COUNT = 4


# ----------------------------------------
# Difficulty Settings
# ----------------------------------------
# Each difficulty defines:
# - base_moves: number of moves in Level 1
# - level_time: total time budget per level
#
# Each subsequent level increases move count by +1.
# Per-move time = level_time / number_of_moves.
DIFFICULTIES = {
    "EASY": {
        "base_moves": 2,      # Level 1 contains 2 actions
        "level_time": 60.0,   # Total time allowed for each level
    },
    "MEDIUM": {
        "base_moves": 4,      # Level 1 contains 4 actions
        "level_time": 60.0,   # Total time allowed for each level
    },
    "HARD": {
        "base_moves": 6,      # Level 1 contains 6 actions
        "level_time": 120.0,  # Total time allowed for each level
    },
}

# Number of levels per difficulty
TOTAL_LEVELS = 10


# ----------------------------------------
# Move Identifiers
# ----------------------------------------
# These string constants are used by the game engine
# to match player input with the expected action.
MOVE_CW = "ROTATE_RIGHT"   # Clockwise rotation
MOVE_CCW = "ROTATE_LEFT"   # Counter-clockwise rotation
MOVE_PRESS = "PRESS"       # Encoder button press
MOVE_SHAKE = "SHAKE"       # Accelerometer shake gesture

# The set of all possible actions the game may generate
ALL_MOVES = [MOVE_CW, MOVE_CCW, MOVE_PRESS, MOVE_SHAKE]


# ----------------------------------------
# Shake Detection Parameters
# ----------------------------------------
# Based on collected accelerometer samples:
# - Normal resting noise frequently falls between ~0.1–1.0
# - Desk vibration spikes can reach 3–7
# To reliably detect only intentional strong shakes,
# a high threshold is required.
SHAKE_DELTA_THRESHOLD = 2.0     # Minimum delta magnitude required to count as a shake
SHAKE_MAX_DELTA = 100.0         # Discard extreme spikes as sensor noise or error
SHAKE_COOLDOWN = 0.3            # Prevent repeated triggering from a single shake


# ----------------------------------------
# Rotary Encoder Cooldown
# ----------------------------------------
# Prevent multiple rotation events being triggered
# from a single physical detent or due to bouncing.
ROTATE_COOLDOWN = 0.5


# ----------------------------------------
# Menu Press Hold Time
# ----------------------------------------
# Duration the encoder button must be held
# in the difficulty menu to start the game.
MENU_PRESS_HOLD = 0.2


# ----------------------------------------
# In-Game Move Cooldown
# ----------------------------------------
# Prevents a single gesture from being interpreted
# as multiple valid actions in rapid succession.
ACTION_COOLDOWN = 0.25
