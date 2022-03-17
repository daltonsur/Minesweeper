import random
import tkinter as tk
import time
import math
from queue import Queue


class Square:
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col
        self._seen_value = ''
        self._real_value = 0
        self._canvas = tk.Canvas(master=game_frame, width=25, height=25)
        self._canvas.create_image(0, 0, image=get(''), anchor=tk.NW)
        self.bind_left_click()

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    def reveal(self):
        self.set_seen(self._real_value)
        self.unbind_right_click()

    def set_seen(self, value):
        self._seen_value = value
        self._canvas.create_image(0, 0, image=get(value), anchor=tk.NW)

    def is_flagged(self):
        return self._seen_value == 'f'

    def is_revealed(self):
        return self._seen_value != '' and self._seen_value != 'f'

    def is_mine(self):
        return self._real_value == -1

    def is_empty(self):
        return self._real_value == 0

    def set_as_mine(self):
        self._real_value = -1

    def set_real(self, value):
        self._real_value = value

    def bind(self):
        self.bind_right_click()
        self.bind_left_click()

    def bind_right_click(self):
        self._canvas.bind("<3>", self.right_click)

    def bind_left_click(self):
        self._canvas.bind("<1>", self.left_click)

    def unbind(self):
        self.unbind_right_click()
        self.unbind_left_click()

    def unbind_right_click(self):
        self._canvas.unbind("<3>")

    def unbind_left_click(self):
        self._canvas.unbind("<1>")

    def left_click(self, event):
        game.left_click(self)

    def right_click(self, event):
        game.right_click(self)

    def is_fully_flagged(self):
        return game.num_neighbors_flagged(self) == self._real_value

    def remove_flag(self):
        self.set_seen('')
        self.bind_left_click()

    def flag(self):
        self.set_seen('f')
        self.unbind_left_click()

    def place_in_grid(self):
        self._canvas.grid(row=self.row, column=self.col)


class Game:
    def __init__(self, diff: str):

        # instantiate board

        self._num_mines = 0
        self.height, self.width = self.set_difficulty(diff)
        self.build_gui()
        self._board = [[Square(row, col) for col in range(self.width)] for row in range(self.height)]

        self._started = False
        self._vis = []
        self._flags = 0
        self.start_time = None
        self.timer_job = None

    def set_difficulty(self, diff: str):
        if diff == "Beginner":
            self._num_mines = 10
            return 9, 9
        elif diff == "Intermediate":
            self._num_mines = 40
            return 16, 16
        else:
            self._num_mines = 99
            return 16, 30

    def left_click(self, square: Square):
        # Fill board if haven't already
        if not self.is_started():
            self.start_game(square)

        if square.is_mine():
            self.set_game_over(False)
        else:
            if square.is_revealed() and square.is_fully_flagged():
                self.reveal_neighbors(square)
            else:
                self.reveal(square)
            if self.is_over():
                self.set_game_over(True)

    def is_started(self):
        return self._started

    def start_game(self, square: Square):
        self.fill_board(square)
        self.set_nums()
        self.start_timer()
        self.bind_all_right()
        self._started = True

    # Reveals neighbors
    def reveal_neighbors(self, square: Square):
        neighbors = self.get_neighbors(square)
        for neighbor in neighbors:
            if not neighbor.is_revealed() and not neighbor.is_flagged():
                self.reveal(neighbor)

    def set_game_over(self, won: bool):
        self.unbind_squares()
        self.reveal_all_mines()
        self.stop_timer()

    # Reveal a square
    def reveal(self, square: Square):
        # If empty space, reveal neighbors
        if square.is_empty():
            self.reveal_empty(square)
        # If mine and not flagged, game over
        elif square.is_mine() and not square.is_flagged():
            self.set_game_over(False)
        else:
            square.reveal()

    def is_over(self):
        count = 0

        # Check each cell
        for row in self._board:
            for square in row:
                # If cell not empty or flagged
                if square.is_revealed():
                    count += 1

        # Count comparison
        return count == self.width * self.height - self._num_mines

    def fill_board(self, square: Square):
        # Track of number of mines already set up
        num_mines_placed = 0
        while num_mines_placed < self._num_mines:

            # Random number from all possible grid positions
            val = random.randint(0, self.width * self.height - 1)

            # Generating row and column from the number
            r = val // self.width
            c = val % self.width

            # Place the mine, avoiding area around clicked square
            if (square.row + 1 >= r >= square.row - 1
                    and square.col + 1 >= c >= square.col - 1):
                continue
            elif not self._board[r][c].is_mine():
                num_mines_placed += 1
                self._board[r][c].set_as_mine()

    def set_nums(self):
        for row in self._board:
            for square in row:
                if square.is_mine():
                    continue

                neighbors = self.get_neighbors(square)
                num_mine_neighbors = 0
                for neighbor in neighbors:
                    if neighbor.is_mine():
                        num_mine_neighbors += 1
                square.set_real(num_mine_neighbors)

    def start_timer(self):
        self.start_time = time.time()
        time_label["text"] = '0'
        self.timer_job = window.after(1000, self.update_timer)

    def bind_all_right(self):
        for row in self._board:
            for square in row:
                square.bind_right_click()

    def get_neighbors(self, square: Square):
        neighbors = []

        for row in range(max(0, square.row - 1), min(self.height, square.row + 2)):
            for col in range(max(0, square.col - 1), min(self.width, square.col + 2)):
                if row == square.row and col == square.col:
                    continue
                neighbors.append(self._board[row][col])

        return neighbors

    def unbind_squares(self):
        for row in self._board:
            for square in row:
                square.unbind()

    def reveal_all_mines(self):
        for row in self._board:
            for square in row:
                if square.is_mine():
                    square.reveal()

    def stop_timer(self):
        window.after_cancel(self.timer_job)

    def reveal_empty(self, square: Square):
        # If cell already not visited
        vis = set()
        queue = Queue(maxsize=self.height * self.width)
        queue.put(square)
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

    def update_timer(self):
        time_label["text"] = str(math.floor(time.time() - self.start_time))
        self.timer_job = window.after(1000, self.update_timer)

    def right_click(self, square: Square):
        # If already flagged, remove flag
        if square.is_flagged():
            self.remove_flag(square)
        # If square is already revealed, do nothing
        elif square.is_revealed():
            return
        # If you haven't flagged too many, flag the square
        elif self._flags < self._num_mines:
            self.add_flag(square)

    def remove_flag(self, square: Square):
        square.remove_flag()
        self._flags -= 1
        self.set_mine_label()

    def add_flag(self, square: Square):
        square.flag()
        self._flags += 1
        self.set_mine_label()

    def set_mine_label(self):
        mines_label["text"] = str(self._num_mines - self._flags)

    def num_neighbors_flagged(self, square: Square):
        num_flags = 0
        neighbors = self.get_neighbors(square)
        for neighbor in neighbors:
            if neighbor.is_flagged():
                num_flags += 1
        return num_flags

    def build_gui(self):
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


# Referenced https://stackoverflow.com/questions/53861528/runtimeerror-too-early-to-create-image/53861790
image_list = {
    0: ['images/0.png', None],
    1: ['images/1.png', None],
    2: ['images/2.png', None],
    3: ['images/3.png', None],
    4: ['images/4.png', None],
    5: ['images/5.png', None],
    6: ['images/6.png', None],
    7: ['images/7.png', None],
    8: ['images/8.png', None],
    -1: ['images/bomb.png', None],
    'f': ['images/flagged.png', None],
    '': ['images/facingDown.png', None],
}


def get(name):
    if name in image_list:
        if image_list[name][1] is None:
            image_list[name][1] = tk.PhotoImage(file=image_list[name][0])
        return image_list[name][1]
    return None


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


if __name__ == '__main__':
    game = Game("Expert")
