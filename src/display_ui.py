# display_ui.py
import time
import board
import displayio
import terminalio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306


class Display:
    def __init__(self, i2c):
        displayio.release_displays()

        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
        self.display = adafruit_displayio_ssd1306.SSD1306(
            display_bus, width=128, height=64
        )

        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

        self.clear()

    def clear(self):
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

    def _text_center(self, txt, y):
        text_obj = label.Label(terminalio.FONT, text=txt)
        w = text_obj.bounding_box[2]
        text_obj.x = int((128 - w) / 2)
        text_obj.y = y
        self.main_group.append(text_obj)

    # 給舊代碼用的接口, 你也可以不再用
    def _text(self, txt, x, y):
        text_obj = label.Label(terminalio.FONT, text=txt, x=x, y=y)
        self.main_group.append(text_obj)

    # 開機動畫, 只在 Game.__init__ 裡被叫一次
    def play_splash_animation(self):

        self.clear()

        title = label.Label(terminalio.FONT, text="ACTION GBA")
        subtitle = label.Label(terminalio.FONT, text="Press to start")

        def center_x(lbl):
            w = lbl.bounding_box[2]
            lbl.x = int((128 - w) / 2)

        center_x(title)
        center_x(subtitle)

        # 起始位置在屏幕下方
        start_title_y = 80
        start_sub_y = 100

        # 目标位置
        target_title_y = 20
        target_sub_y = 42

        title.y = start_title_y
        subtitle.y = start_sub_y

        self.main_group.append(title)
        self.main_group.append(subtitle)

        # 用較少幀數, 每幀移動更大一步, 等待時間也縮短
        frames = 15  # 原來大約 30+ 幀, 現在只用 15 幀
        for i in range(frames):
            ratio = (i + 1) / frames
            title.y = int(start_title_y + (target_title_y - start_title_y) * ratio)
            subtitle.y = int(start_sub_y + (target_sub_y - start_sub_y) * ratio)
            time.sleep(0.02)  # 每幀 0.02 秒, 總長大約 0.3 秒

        # 最後保險起見, 把位置設成精確的目標值
        title.y = target_title_y
        subtitle.y = target_sub_y

        # 動畫結束後用標準的靜態開機畫面收尾
        self.show_splash()


    def show_splash(self):
        self.clear()
        self._text_center("ACTION GBA", 20)
        self._text_center("Press to start", 42)

    def show_menu(self, difficulty):
        self.clear()
        self._text_center("Select Difficulty", 12)
        self._text_center("> " + difficulty, 32)
        self._text_center("Press to confirm", 52)

    def show_game_over(self):
        self.clear()
        self._text_center("GAME OVER", 22)
        self._text_center("Press to retry", 44)

    def show_game_win(self):
        self.clear()
        self._text_center("YOU WIN!", 22)
        self._text_center("Press to replay", 44)

    def show_level(self, level, difficulty, seq_len, index, move, ratio_unused):
        self.clear()
        self._text_center(f"Diff: {difficulty}", 10)
        self._text_center(f"Level: {level}", 22)
        self._text_center(f"Move: {index + 1}/{seq_len}", 34)
        self._text_center("Do: " + move, 46)

