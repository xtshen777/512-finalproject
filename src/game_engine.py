# game_engine.py
import time
import random
import config


class Game:
    def __init__(self, inputs, display, lights):
        self.inputs = inputs
        self.display = display
        self.lights = lights

        self.state = "SPLASH"
        self.difficulty = "EASY"
        self.level = 1

        self.sequence = []
        self.seq_index = 0

        self.current_move = config.MOVE_PRESS
        self.per_move_time = 1.0
        self.move_start_time = time.monotonic()

        # 菜單相關
        self.menu_needs_redraw = True
        self.menu_press_start = None  # 菜單裡長按的起始時間

        # 動作冷卻, 防止一次操作吃多步
        self.action_cooldown_until = 0.0

        # 上電時播放一次開機動畫
        self.lights.set_mode("splash")          # 這裡可以保持彩虹燈
        self.display.play_splash_animation()    # 動畫裡面最後會顯示靜態的 splash


    def update(self, dt):
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
        # 目前顯示在各個 state 裡直接呼叫 display
        pass

    # --------------- 狀態: 開機畫面 ---------------

    def _state_splash(self):
        # 開機畫面已經在 __init__ 畫過了, 這裡只維持彩虹燈並等待按下
        self.lights.set_mode("splash")

        # 主畫面按一下進入菜單
        if self.inputs.button_pressed:
            print("SPLASH: button pressed, go to MENU")
            self.state = "MENU"
            self.menu_needs_redraw = True
            # 進菜單後改用 menu 彩虹模式
            self.lights.set_mode("menu")

    # --------------- 狀態: 難度選擇菜單 ---------------

    def _state_menu(self):
        # 難度選擇期間使用彩虹燈
        self.lights.set_mode("menu")

        # 只在需要的時候重畫畫面, 避免閃爍
        if self.menu_needs_redraw:
            self.display.show_menu(self.difficulty)
            self.menu_needs_redraw = False

        # 旋鈕切換難度
        if self.inputs.rotated_cw:
            self.difficulty = self._next_difficulty()
            self.menu_needs_redraw = True
            print("MENU: rotate CW, diff =", self.difficulty)
        elif self.inputs.rotated_ccw:
            self.difficulty = self._prev_difficulty()
            self.menu_needs_redraw = True
            print("MENU: rotate CCW, diff =", self.difficulty)

        # 長按按鈕才開始遊戲
        if self.inputs.button_down:
            # 第一次檢測到按下, 記錄時間
            if self.menu_press_start is None:
                self.menu_press_start = time.monotonic()
            else:
                # 已經按住一段時間, 檢查是否超過長按時間
                held = time.monotonic() - self.menu_press_start
                if held >= config.MENU_PRESS_HOLD:
                    print("MENU: long press to start game, held =", held)
                    self.level = 1
                    self.state = "LEVEL_START"
                    # 真正進關卡時, 在 _state_level_start 裡切到 playing 模式
                    self.menu_press_start = None
        else:
            # 鬆開就重置長按計時
            self.menu_press_start = None

    # --------------- 狀態: 開始一關 ---------------

    def _state_level_start(self):
        # 一旦真正進入遊戲, 不再用彩虹燈, 改為遊戲狀態燈光
        self.lights.set_mode("playing")

        # 根據難度和當前 level 計算關卡設計
        params = config.DIFFICULTIES[self.difficulty]
        base_moves = params["base_moves"]
        total_time = params["level_time"]

        # 每個 level 比上一個多一個動作
        # Level 1: base_moves
        # Level 2: base_moves + 1
        # ...
        seq_len = base_moves + (self.level - 1)

        # 動作序列隨機生成
        self.sequence = [random.choice(config.ALL_MOVES) for _ in range(seq_len)]
        self.seq_index = 0
        self.current_move = self.sequence[0]

        # 每一步的時間限制 = 整關總時間 / 動作數
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

        # 更新畫面和燈光
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

        # 新開一關時, 不額外等待冷卻
        self.action_cooldown_until = 0.0

    # --------------- 狀態: 等待玩家輸入 ---------------

    def _state_wait_input(self):
        now = time.monotonic()

        # 先檢查是否超時
        if now - self.move_start_time > self.per_move_time:
            print("WAIT_INPUT: time up, game over")
            self.state = "GAME_OVER"
            self.display.show_game_over()
            self.lights.set_mode("game_over")
            return

        # 冷卻期內忽略輸入, 避免一次操作吃多步
        if now < self.action_cooldown_until:
            return

        # 判斷當前動作是否完成
        if self._is_move_correct(self.current_move):
            print("WAIT_INPUT: correct move", self.current_move)

            # 設置下一次動作冷卻
            self.action_cooldown_until = now + config.ACTION_COOLDOWN

            self.seq_index += 1

            # 這一關所有動作完成
            if self.seq_index >= len(self.sequence):
                self.level += 1
                if self.level > config.TOTAL_LEVELS:
                    print("GAME_WIN: passed all levels")
                    self.state = "GAME_WIN"
                    self.display.show_game_win()
                    self.lights.set_mode("game_win")
                else:
                    self.state = "LEVEL_START"
                return

            # 進入這一關的下一步動作
            self.current_move = self.sequence[self.seq_index]
            self.move_start_time = now  # 下一步計時從現在開始
            self.display.show_level(
                self.level,
                self.difficulty,
                len(self.sequence),
                self.seq_index,
                self.current_move,
                1.0,
            )
            self.lights.set_mode("move", self.current_move)

    # --------------- 狀態: 遊戲失敗 / 勝利 ---------------

    def _state_game_over(self):
        # Game Over 畫面時, 燈已經在 _state_wait_input 裡設為 "game_over"
        if self.inputs.button_pressed:
            # 回到菜單, 再次跑彩虹燈
            self.state = "MENU"
            self.menu_needs_redraw = True
            self.display.show_menu(self.difficulty)
            self.lights.set_mode("menu")

    def _state_game_win(self):
        if self.inputs.button_pressed:
            # 回到菜單, 再次跑彩虹燈
            self.state = "MENU"
            self.menu_needs_redraw = True
            self.display.show_menu(self.difficulty)
            self.lights.set_mode("menu")

    # --------------- 難度切換與動作判定 ---------------

    def _next_difficulty(self):
        order = ["EASY", "MEDIUM", "HARD"]
        idx = order.index(self.difficulty)
        return order[(idx + 1) % len(order)]

    def _prev_difficulty(self):
        order = ["EASY", "MEDIUM", "HARD"]
        idx = order.index(self.difficulty)
        return order[(idx - 1) % len(order)]

    def _is_move_correct(self, move_name):
        if move_name == config.MOVE_CW:
            return self.inputs.rotated_cw
        if move_name == config.MOVE_CCW:
            return self.inputs.rotated_ccw
        if move_name == config.MOVE_PRESS:
            # 只認「按下的瞬間」
            return self.inputs.button_pressed
        if move_name == config.MOVE_SHAKE:
            return self.inputs.shake_detected
        return False

