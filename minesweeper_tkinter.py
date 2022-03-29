import math
import tkinter as tk
import time
from minesweeper import Game


class GameView:
    def __init__(self, game: Game):
        self.game = game

        self.window = tk.Tk()
        self.window.resizable(False, False)

        self.control_frame = tk.Frame(self.window)
        self.control_frame.pack()

        self.diff_menu = DifficultyMenu(self.control_frame)
        self.new_game_button = NewGameButton(self.control_frame, self.game.new_game)
        self.mines_label = MinesLabel(self.control_frame, self.game.num_mines)
        self.timer_label = TimerLabel(self.control_frame)

        self.game_frame = GameBoardFrame(self.window, self.game.height, self.game.width)

    def start_view(self):
        self.window.mainloop()

    def start_timer(self):
        self.timer_label.start_timer()

    def stop_timer(self):
        self.timer_label.stop_timer()

    def set_mines_label(self, value: int):
        self.mines_label.set_mine_label(str(value))

    def get_difficulty(self):
        return self.diff_menu.get_difficulty()

    def resize_board(self):
        self.game_frame.resize(self.game.height, self.game.width)

    def reset_timer(self):
        self.timer_label.reset_timer()


class DifficultyMenu(tk.OptionMenu):
    def __init__(self, parent):
        difficulties = ["Beginner", "Intermediate", "Expert"]
        self.difficulty = tk.StringVar(value=difficulties[2])
        super().__init__(parent, self.difficulty, *difficulties)
        self.pack()

    def get_difficulty(self):
        return self.difficulty.get()


class NewGameButton(tk.Button):
    def __init__(self, parent, func):
        super().__init__(parent, text="New Game", width=10, height=3)
        self.bind("<1>", func)
        self.pack()


class TimerLabel(tk.Label):
    def __init__(self, parent):
        super().__init__(parent, font=("Impact", 44), text="00")
        self.start_time = None
        self.timer_job = None
        self.pack()

    def start_timer(self) -> None:
        self.start_time = time.time()
        self["text"] = "00"
        self.timer_job = self.after(1000, self.update_timer)

    def update_timer(self) -> None:
        self["text"] = str(math.floor(time.time() - self.start_time))
        self.timer_job = self.after(1000, self.update_timer)

    def stop_timer(self) -> None:
        self.after_cancel(self.timer_job)

    def reset_timer(self):
        self["text"] = "00"


class MinesLabel(tk.Label):
    def __init__(self, parent, num_mines):
        super().__init__(parent, font=("Impact", 44), text=num_mines)
        self.pack()

    def set_mine_label(self, value: str) -> None:
        self["text"] = value


class GameBoardFrame(tk.Frame):
    def __init__(self, parent, height, width):
        super().__init__(parent)
        self.columnconfigure(int(width - 1))
        self.rowconfigure(int(height - 1))
        self.pack()

    def resize(self, height, width):
        self.columnconfigure(int(width - 1))
        self.rowconfigure(int(height - 1))
