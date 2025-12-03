# config.py
import board

# 旋钮引脚
ENCODER_PIN_A = board.D1
ENCODER_PIN_B = board.D2
ENCODER_BUTTON = board.D9   # 旋钮按下开关

# NeoPixel 引脚
NEOPIXEL_PIN = board.D10
NEOPIXEL_COUNT = 4

# 难度设定
DIFFICULTIES = {
    "EASY": {
        "base_moves": 2,     # Level 1 有 2 个动作
        "level_time": 60.0,  # 每關總時間 15 秒
    },
    "MEDIUM": {
        "base_moves": 4,     # Level 1 有 4 個動作
        "level_time": 60.0,  # 每關總時間 20 秒
    },
    "HARD": {
        "base_moves": 6,     # Level 1 有 6 個動作
        "level_time": 120.0,  # 每關總時間 25 秒
    },
}

TOTAL_LEVELS = 10

# 动作常量
MOVE_CW = "ROTATE_RIGHT"   # 右转
MOVE_CCW = "ROTATE_LEFT"   # 左转
MOVE_PRESS = "PRESS"       # 按下旋钮
MOVE_SHAKE = "SHAKE"       # 摇晃

ALL_MOVES = [MOVE_CW, MOVE_CCW, MOVE_PRESS, MOVE_SHAKE]

# 摇晃检测參數
# 你的數據裡，桌面的小抖動常常在 3～7 之間
# 所以把門檻設得非常高，只把「很用力的大晃動」算作 SHAKE
SHAKE_DELTA_THRESHOLD = 2.0   # 超過 10 才有機會判定為 SHAKE
SHAKE_MAX_DELTA = 100.0        # 大於 35 當成異常尖峰，直接忽略
SHAKE_COOLDOWN = 0.3         # 一次 SHAKE 成功後 0.6 秒內不再觸發


# 旋钮冷却时间 秒
ROTATE_COOLDOWN = 0.5

# 菜单里长按多少秒才开始游戏
MENU_PRESS_HOLD = 0.2

# 游戏中两次动作之间的冷却时间
ACTION_COOLDOWN = 0.25   # 可以之后按手感微调


