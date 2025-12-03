# lights.py
import time
import board
import neopixel
from rainbowio import colorwheel
import config


class Lights:
    def __init__(self):
        # 你的 NeoPixel 在 D10
        self.pixels = neopixel.NeoPixel(
            board.D10, 1, brightness=0.3, auto_write=False
        )

        self.mode = "idle"
        self.current_move = None

        # 用來做彩虹動畫的位置
        self._rainbow_pos = 0.0

    # 小工具: 設置單一顏色
    def _set_color(self, color):
        self.pixels[0] = color
        self.pixels.show()

    # 小工具: 根據動作名設置顏色
    def _set_move_color(self, move):
        if move == config.MOVE_CW:
            # 左旋: 黃色
            color = (255, 255, 0)
        elif move == config.MOVE_CCW:
            # 右旋: 青色
            color = (0, 255, 255)
        elif move == config.MOVE_PRESS:
            # 按下: 綠色
            color = (0, 255, 0)
        elif move == config.MOVE_SHAKE:
            # 晃動: 白色
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)
        self._set_color(color)

    def set_mode(self, mode, move=None):
        """由 game_engine 控制模式:
        - "splash"   開機畫面 彩虹旋轉
        - "menu"     難度選擇 彩虹旋轉
        - "playing"  剛進遊戲 狀態色
        - "move"     根據當前動作顯示顏色
        - "game_start"  開始提示
        - "game_over"   結束紅燈
        - "idle"        熄燈
        """
        self.mode = mode
        self.current_move = move

        if mode in ("splash", "menu"):
            # 進入這兩個模式時 開始跑彩虹動畫
            # 顏色在 update 裡實時更新 這裡先不強制改顏色
            return

        # 其他模式都是「靜態顏色」 不再顯示彩虹
        if mode == "idle":
            self._set_color((0, 0, 0))

        elif mode == "game_start":
            # 開始提示: 藍色
            self._set_color((0, 0, 150))

        elif mode == "playing":
            # 遊戲進行中 可以用淡藍色作背景狀態
            self._set_color((0, 0, 40))

        elif mode == "move":
            # 每個動作顯示不同顏色
            self._set_move_color(move)

        elif mode == "game_over":
            # Game Over: 紅色常亮
            self._set_color((200, 0, 0))

        else:
            # 未知模式當作熄燈
            self._set_color((0, 0, 0))

    def update(self, dt):
        """在 code.py 裡每一幀都會被呼叫 用來更新動畫效果"""
        # 只有在開機畫面和難度菜單 才跑彩虹
        if self.mode in ("splash", "menu"):
            # 參考你之前的 rainbow_cycle
            # 這裡不用 for 迴圈 而是用時間累積 非阻塞
            # 調整 120 這個數可以改變彩虹旋轉速度
            self._rainbow_pos = (self._rainbow_pos + 120 * dt) % 255
            idx = int(self._rainbow_pos) & 255
            self.pixels[0] = colorwheel(idx)
            self.pixels.show()
        # 其他模式是靜態顏色 不需要在這裡做事
