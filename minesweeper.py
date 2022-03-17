import math
import random
import time
import tkinter as tk
from enum import IntEnum
from queue import Queue
from typing import Tuple, List


class SquareValue(IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    FLAG = 9
    COVERED = 10
    MINE = 11

    def __init__(self, *args):
        self.image = tk.PhotoImage(file=f"images/{self.name.lower}.png")


class Cell:
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col
        self._canvas = tk.Canvas(master=game_frame, width=25, height=25)
        self._real_value = SquareValue.ZERO
        self._seen_value = None
        self.set_seen(SquareValue.COVERED)
        self.bind_left_click()

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    def reveal(self) -> None:
        self.set_seen(self._real_value)
        self.unbind_right_click()

    def set_seen(self, value: SquareValue) -> None:
        self._seen_value = value
        self._canvas.create_image(0, 0, image=self._seen_value.image, anchor=tk.NW)

    def is_flagged(self) -> bool:
        return self._seen_value is SquareValue.FLAG

    def is_revealed(self) -> bool:
        return self._seen_value is not SquareValue.COVERED and self._seen_value is not SquareValue.FLAG

    def is_mine(self) -> bool:
        return self._real_value is SquareValue.MINE

    def is_empty(self) -> bool:
        return self._real_value is SquareValue.COVERED

    def set_as_mine(self) -> None:
        self._real_value = SquareValue.MINE

    def set_real(self, value: SquareValue) -> None:
        self._real_value = value

    def bind(self) -> None:
        self.bind_right_click()
        self.bind_left_click()

    def bind_right_click(self) -> None:
        self._canvas.bind("<3>", self.right_click)

    def bind_left_click(self) -> None:
        self._canvas.bind("<1>", self.left_click)

    def unbind(self) -> None:
        self.unbind_right_click()
        self.unbind_left_click()

    def unbind_right_click(self) -> None:
        self._canvas.unbind("<3>")

    def unbind_left_click(self) -> None:
        self._canvas.unbind("<1>")

    def left_click(self, event: tk.Event) -> None:
        game.left_click(self)

    def right_click(self, event: tk.Event) -> None:
        game.right_click(self)

    def is_fully_flagged(self) -> None:
        return game.num_neighbors_flagged(self) == self._real_value.value

    def remove_flag(self) -> None:
        self.set_seen(SquareValue.COVERED)
        self.bind_left_click()

    def flag(self) -> None:
        self.set_seen(SquareValue.FLAG)
        self.unbind_left_click()

    def place_in_grid(self) -> None:
        self._canvas.grid(row=self.row, column=self.col)


class Game:
    def __init__(self, diff: str):
        self._num_mines = 0
        height, width = self.set_difficulty(diff)
        self.build_gui()
        self._board = [[Cell(row, col) for col in range(width)]
                       for row in range(height)]

        self._started = False
        self._vis = []
        self._flags = 0
        self.start_time = None
        self.timer_job = None

    def set_difficulty(self, diff: str) -> Tuple[int, int]:
        if diff == "Beginner":
            self._num_mines = 10
            return 9, 9
        elif diff == "Intermediate":
            self._num_mines = 40
            return 16, 16
        else:
            self._num_mines = 99
            return 16, 30

    @property
    def height(self) -> int:
        return len(self._board)

    @property
    def width(self) -> int:
        return len(self._board[0])

    def left_click(self, cell: Cell) -> None:
        # Fill board if haven't already
        if not self.is_started():
            self.start_game(cell)

        if cell.is_mine():
            self.set_game_over(False)
        else:
            if cell.is_revealed() and cell.is_fully_flagged():
                self.reveal_neighbors(cell)
            else:
                self.reveal(cell)
            if self.is_over():
                self.set_game_over(True)

    def is_started(self) -> bool:
        return self._started

    def start_game(self, square: Cell) -> None:
        self.fill_board(square)
        self.set_nums()
        self.start_timer()
        self.bind_all_right()
        self._started = True

    # Reveals neighbors
    def reveal_neighbors(self, cell: Cell) -> None:
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            if not neighbor.is_revealed() and not neighbor.is_flagged():
                self.reveal(neighbor)

    def set_game_over(self, won: bool) -> None:
        self.unbind_squares()
        self.reveal_all_mines()
        self.stop_timer()

    # Reveal a square
    def reveal(self, cell: Cell) -> None:
        # If empty space, reveal neighbors
        if cell.is_empty():
            self.reveal_empty(cell)
        # If mine and not flagged, game over
        elif cell.is_mine() and not cell.is_flagged():
            self.set_game_over(False)
        else:
            cell.reveal()

    def is_over(self) -> bool:
        count = 0

        # Check each cell
        for row in self._board:
            for square in row:
                # If cell not empty or flagged
                if square.is_revealed():
                    count += 1

        # Count comparison
        return count == self.width * self.height - self._num_mines

    def fill_board(self, cell: Cell) -> None:
        # Track of number of mines already set up
        num_mines_placed = 0
        while num_mines_placed < self._num_mines:

            # Random number from all possible grid positions
            val = random.randint(0, self.width * self.height - 1)

            # Generating row and column from the number
            r = val // self.width
            c = val % self.width

            # Place the mine, avoiding area around clicked square
            if (cell.row + 1 >= r >= cell.row - 1
                    and cell.col + 1 >= c >= cell.col - 1):
                continue
            elif not self._board[r][c].is_mine():
                num_mines_placed += 1
                self._board[r][c].set_as_mine()

    def set_nums(self) -> None:
        for row in self._board:
            for cell in row:
                if cell.is_mine():
                    continue

                neighbors = self.get_neighbors(cell)
                num_mine_neighbors = 0
                for neighbor in neighbors:
                    if neighbor.is_mine():
                        num_mine_neighbors += 1
                cell.set_real(SquareValue(num_mine_neighbors))

    def start_timer(self) -> None:
        self.start_time = time.time()
        time_label["text"] = '0'
        self.timer_job = window.after(1000, self.update_timer)

    def bind_all_right(self) -> None:
        for row in self._board:
            for cell in row:
                cell.bind_right_click()

    def get_neighbors(self, cell: Cell) -> List[Cell]:
        neighbors = []

        for row in range(max(0, cell.row - 1), min(self.height, cell.row + 2)):
            for col in range(max(0, cell.col - 1), min(self.width, cell.col + 2)):
                if row == cell.row and col == cell.col:
                    continue
                neighbors.append(self._board[row][col])

        return neighbors

    def unbind_squares(self) -> None:
        for row in self._board:
            for cell in row:
                cell.unbind()

    def reveal_all_mines(self) -> None:
        for row in self._board:
            for cell in row:
                if cell.is_mine():
                    cell.reveal()

    def stop_timer(self) -> None:
        window.after_cancel(self.timer_job)

    def reveal_empty(self, cell: Cell) -> None:
        # If cell already not visited
        vis = set()
        queue = Queue(maxsize=self.height * self.width)
        queue.put(cell)
        while not queue.empty():
            curr = queue.get()
            curr.reveal()
            vis.add(curr)
            neighbors = self.get_neighbors(curr)
            for neighbor in neighbors:
                if neighbor in vis or neighbor.is_flagged():
                    continue
                elif neighbor.is_empty():
                    queue.put(neighbor)
                else:
                    vis.add(neighbor)
                    neighbor.reveal()

    def update_timer(self) -> None:
        time_label["text"] = str(math.floor(time.time() - self.start_time))
        self.timer_job = window.after(1000, self.update_timer)

    def right_click(self, cell: Cell) -> None:
        # If already flagged, remove flag
        if cell.is_flagged():
            self.remove_flag(cell)
        # If square is already revealed, do nothing
        elif cell.is_revealed():
            return
        # If you haven't flagged too many, flag the square
        elif self._flags < self._num_mines:
            self.add_flag(cell)

    def remove_flag(self, cell: Cell) -> None:
        cell.remove_flag()
        self._flags -= 1
        self.set_mine_label()

    def add_flag(self, cell: Cell) -> None:
        cell.flag()
        self._flags += 1
        self.set_mine_label()

    def set_mine_label(self) -> None:
        mines_label["text"] = str(self._num_mines - self._flags)

    def num_neighbors_flagged(self, cell: Cell) -> int:
        num_flags = 0
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            if neighbor.is_flagged():
                num_flags += 1
        return num_flags

    def build_gui(self) -> None:
        global window
        global control_frame
        global new_game_button
        global diff_menu
        global game_frame
        global mines_label
        global time_label
        global difficulty

        window = tk.Tk()
        window.resizable(False, False)

        control_frame = tk.Frame(master=window)
        control_frame.pack()

        new_game_button = tk.Button(master=control_frame, text="New Game", width=10, height=3)
        new_game_button.pack()
        new_game_button.bind("<1>", new_game)

        difficulties = ["Beginner", "Intermediate", "Expert"]
        difficulty = tk.StringVar(control_frame)
        difficulty.set(difficulties[2])
        diff_menu = tk.OptionMenu(control_frame, difficulty, *difficulties)
        diff_menu.pack()

        game_frame = tk.Frame(master=window)
        game_frame.pack()

        # Build the mines label
        mines_label = tk.Label(master=control_frame, text=str(self._num_mines))
        mines_label.config(font=("Impact", 44))
        mines_label.pack()

        time_label = tk.Label(master=control_frame, text="000")
        time_label.config(font=("Impact", 44))
        time_label.pack()

        # Configure the mine grid
        game_frame.columnconfigure([x for x in range(self.width)], minsize=25)
        game_frame.rowconfigure([y for y in range(self.height)], minsize=25)

        for row in range(self.height):
            for col in range(self.width):
                self._board[row][col].place_in_grid()

        window.mainloop()


def new_game(event):
    global game_frame
    global game

    mines_label.destroy()
    time_label.destroy()
    window.after_cancel(game.timer_job)

    game_frame.destroy()
    game_frame = tk.Frame(master=window)
    game_frame.pack()
    game = Game(difficulty.get())
    game.build_gui()


class GameController:
    def __init__(self):
        self._view = None
        self._game = Game("Expert")
        


if __name__ == '__main__':
    game = Game("Expert")
