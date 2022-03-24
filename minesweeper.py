import random
import tkinter as tk
import time
import math
from enum import IntEnum
from queue import Queue
from typing import List, Dict


class CellValue(IntEnum):
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


class Cell:
    game = None

    def __init__(self, row: int, col: int, parent):
        self._row = row
        self._col = col
        self._seen_value = CellValue.COVERED
        self._real_value = CellValue.ZERO
        self._canvas = tk.Canvas(parent, width=25, height=25)
        self.set_seen(self._seen_value)
        self.place_in_grid()
        self.bind_left_click()

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    def reveal(self) -> None:
        self.set_seen(self._real_value)
        self.unbind_right_click()

    def set_seen(self, value: CellValue) -> None:
        self._seen_value = value
        self._canvas.create_image(0, 0, image=get(value), anchor=tk.NW)

    def is_flagged(self) -> bool:
        return self._seen_value is CellValue.FLAG

    def is_revealed(self) -> bool:
        return self._seen_value is not CellValue.COVERED and self._seen_value is not CellValue.FLAG

    def is_mine(self) -> bool:
        return self._real_value is CellValue.MINE

    def is_empty(self) -> bool:
        return self._real_value is CellValue.ZERO

    def set_real(self, value: CellValue) -> None:
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
        self.game.left_click(self)

    def right_click(self, event: tk.Event) -> None:
        self.game.right_click(self)

    def is_fully_flagged(self) -> bool:
        return self.game.num_neighbors_flagged(self) == self._real_value.value

    def remove_flag(self) -> None:
        self.set_seen(CellValue.COVERED)
        self.bind_left_click()

    def flag(self) -> None:
        self.set_seen(CellValue.FLAG)
        self.unbind_left_click()

    def place_in_grid(self) -> None:
        self._canvas.grid(row=self.row, column=self.col)


class Game:
    def __init__(self, diff: str):
        self._num_mines = 0
        self._height = 0
        self._width = 0
        self._difficulty = None
        self.set_difficulty(diff)
        self.view = GameView(self)
        Cell.game = self
        self._board = [[Cell(row, col, self.view.game_frame) for col in range(self._width)]
                       for row in range(self._height)]
        self._started = False
        self._vis = []
        self._flags = 0
        self.view.start_view()

    def set_difficulty(self, diff: str) -> [int, int]:
        self._difficulty = diff
        if diff == "Beginner":
            self._num_mines = 10
            self._height, self._width = 9, 9
        elif diff == "Intermediate":
            self._num_mines = 40
            self._height, self._width = 16, 16
        else:
            self._num_mines = 99
            self._height, self._width = 16, 30

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def num_mines(self) -> int:
        return self._num_mines

    def left_click(self, cell: Cell) -> None:
        # Fill board if haven't already
        if not self.is_started():
            self.start_game(cell)

        if cell.is_mine():
            self.set_game_over()
        else:
            if cell.is_revealed() and cell.is_fully_flagged():
                self.reveal_neighbors(cell)
            else:
                self.reveal(cell)
            if self.is_over():
                self.set_game_over()

    def is_started(self) -> bool:
        return self._started

    def start_game(self, cell: Cell) -> None:
        self.fill_board(cell)
        self.set_nums()
        self.view.start_timer()
        self.bind_all_right()
        self._started = True

    # Reveals neighbors
    def reveal_neighbors(self, cell: Cell) -> None:
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            if not neighbor.is_revealed() and not neighbor.is_flagged():
                self.reveal(neighbor)

    def set_game_over(self) -> None:
        self.unbind_cells()
        self.reveal_all_mines()
        self.view.stop_timer()

    # Reveal a cell
    def reveal(self, cell: Cell) -> None:
        # If empty space, reveal neighbors
        if cell.is_empty():
            self.reveal_empty(cell)
        # If mine and not flagged, game over
        elif cell.is_mine() and not cell.is_flagged():
            self.set_game_over()
        else:
            cell.reveal()

    def is_over(self) -> bool:
        count = 0

        # Check each cell
        for row in self._board:
            for cell in row:
                # If cell not empty or flagged
                if cell.is_revealed():
                    count += 1

        # Count comparison
        return count == self._width * self._height - self._num_mines

    def fill_board(self, cell: Cell) -> None:
        # Track of number of mines already set up
        num_mines_placed = 0
        while num_mines_placed < self._num_mines:

            # Random number from all possible grid positions
            val = random.randint(0, self._width * self._height - 1)
            # Generating row and column from the number
            r = val // self._width
            c = val % self._width

            # Place the mine, avoiding area around clicked cell
            if (cell.row + 1 >= r >= cell.row - 1
                    and cell.col + 1 >= c >= cell.col - 1):
                continue
            elif not self._board[r][c].is_mine():
                num_mines_placed += 1
                self._board[r][c].set_real(CellValue.MINE)

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
                cell.set_real(CellValue(num_mine_neighbors))

    def bind_all_right(self) -> None:
        for row in self._board:
            for cell in row:
                cell.bind_right_click()

    def get_neighbors(self, cell: Cell) -> List[Cell]:
        neighbors = []

        for row in range(max(0, cell.row - 1), min(self._height, cell.row + 2)):
            for col in range(max(0, cell.col - 1), min(self._width, cell.col + 2)):
                if row == cell.row and col == cell.col:
                    continue
                neighbors.append(self._board[row][col])

        return neighbors

    def unbind_cells(self) -> None:
        for row in self._board:
            for cell in row:
                cell.unbind()

    def reveal_all_mines(self) -> None:
        for row in self._board:
            for cell in row:
                if cell.is_mine():
                    cell.reveal()

    def reveal_empty(self, cell: Cell) -> None:
        vis = set()
        queue = Queue(maxsize=self._height * self._width)
        queue.put(cell)
        vis.add(cell)
        while not queue.empty():
            curr = queue.get()
            curr.reveal()
            neighbors = self.get_neighbors(curr)
            for neighbor in neighbors:
                if neighbor in vis or neighbor.is_flagged():
                    continue
                elif neighbor.is_empty():
                    vis.add(neighbor)
                    queue.put(neighbor)
                else:
                    vis.add(neighbor)
                    neighbor.reveal()

    def right_click(self, cell: Cell) -> None:
        # If already flagged, remove flag
        if cell.is_flagged():
            self.remove_flag(cell)
        # If cell is already revealed, do nothing
        elif cell.is_revealed():
            return
        # If you haven't flagged too many, flag the cell
        elif self._flags < self._num_mines:
            self.add_flag(cell)

    def remove_flag(self, cell: Cell) -> None:
        cell.remove_flag()
        self._flags -= 1
        self.view.set_mines_label(self._num_mines - self._flags)

    def add_flag(self, cell: Cell) -> None:
        cell.flag()
        self._flags += 1
        self.view.set_mines_label(self._num_mines - self._flags)

    def num_neighbors_flagged(self, cell: Cell) -> int:
        num_flags = 0
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            if neighbor.is_flagged():
                num_flags += 1
        return num_flags

    def new_game(self, event: tk.Event) -> None:
        self.view.stop_timer()
        old_difficulty = self._difficulty
        self.set_difficulty(self.view.get_difficulty())
        if old_difficulty != self._difficulty:
            self.view.resize_board()
            self._board = [[Cell(row, col, self.view.game_frame) for col in range(self._width)]
                           for row in range(self._height)]
        else:
            for row in self._board:
                for cell in row:
                    cell.set_real(CellValue.ZERO)
                    cell.set_seen(CellValue.COVERED)
                    cell.bind_left_click()
        self._started = False
        self._flags = 0
        self._vis = []
        self.view.reset_timer()


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
        self.columnconfigure([x for x in range(width)], minsize=25)
        self.rowconfigure([y for y in range(height)], minsize=25)
        self.pack()

    def resize(self, height, width):
        self.columnconfigure([x for x in range(width)], minsize=25)
        self.rowconfigure([y for y in range(height)], minsize=25)


# Referenced https://stackoverflow.com/questions/53861528/runtimeerror-too-early-to-create-image/53861790
image_list: Dict[CellValue, list] = {
    CellValue.ZERO: ['images/zero.png', None],
    CellValue.ONE: ['images/one.png', None],
    CellValue.TWO: ['images/two.png', None],
    CellValue.THREE: ['images/three.png', None],
    CellValue.FOUR: ['images/four.png', None],
    CellValue.FIVE: ['images/five.png', None],
    CellValue.SIX: ['images/six.png', None],
    CellValue.SEVEN: ['images/seven.png', None],
    CellValue.EIGHT: ['images/eight.png', None],
    CellValue.MINE: ['images/mine.png', None],
    CellValue.FLAG: ['images/flag.png', None],
    CellValue.COVERED: ['images/covered.png', None],
}


def get(value: CellValue) -> tk.PhotoImage:
    if value in image_list:
        if image_list[value][1] is None:
            image_list[value][1] = tk.PhotoImage(file=image_list[value][0])
        return image_list[value][1]


if __name__ == '__main__':
    Game("Expert")
