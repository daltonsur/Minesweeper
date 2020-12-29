import os
import random
import sys
import tkinter as tk


class Square:
    def __init__(self, row, col, game):
        self.seen = ' '
        self.real = 0
        self.flagged = False
        self.row = row
        self.col = col
        self.game = game
        self.canvas = tk.Canvas(window, width=25, height=25)
        self.canvas.create_image(0, 0, image=get(' '), anchor=tk.NW)
        self.canvas.bind("<1>", self.left_click)
        self.canvas.bind("<3>", self.right_click)

    def left_click(self, event):
        self.game.left_click(self.row, self.col)

    def right_click(self, event):
        self.game.right_click(self.row, self.col)


class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        if self.difficulty == "Beginner":
            self.height = 9
            self.width = 9
            self.num_mines = 10
        elif self.difficulty == "Intermediate":
            self.height = 16
            self.width = 16
            self.num_mines = 40
        elif self.difficulty == "Expert":
            self.height = 16
            self.width = 30
            self.num_mines = 99
        self.board = [[Square(row, col, self) for col in range(self.width)] for row in range(self.height)]
        self.filled = False
        self.vis = []
        self.flags = 0
        self.game_over = False

    def left_click(self, row, col):
        if self.game_over:
            return
        square = self.board[row][col]
        if square.flagged:
            return
        if square.seen != ' ':
            if self.check_full(row, col):
                self.reveal_neighbors(row, col)
            return
        if not self.filled:
            self.fill_board(row, col)
            self.set_nums()
            self.filled = True
        if square.real == -1:
            self.show_mines()
        elif square.real == 0:
            self.neighbours(row, col)
        else:
            self.reveal(row, col)
        self.check_over()

    def check_full(self, row, col):
        num_flags = 0
        # Check up
        if row > 0 and self.board[row - 1][col].flagged:
            num_flags += 1
        # Check down
        if row < self.height - 1 and self.board[row + 1][col].flagged:
            num_flags += 1
        # Check left
        if col > 0 and self.board[row][col - 1].flagged:
            num_flags += 1
        # Check right
        if col < self.width - 1 and self.board[row][col + 1].flagged:
            num_flags += 1
        # Check top-left
        if row > 0 and col > 0 and self.board[row - 1][col - 1].flagged:
            num_flags += 1
        # Check top-right
        if row > 0 and col < self.width - 1 and self.board[row - 1][col + 1].flagged:
            num_flags += 1
        # Check below-left
        if row < self.height - 1 and col > 0 and self.board[row + 1][col - 1].flagged:
            num_flags += 1
        # Check below-right
        if row < self.height - 1 and col < self.width - 1 and self.board[row + 1][col + 1].flagged:
            num_flags += 1

        return num_flags == self.board[row][col].real

    def reveal_neighbors(self, row, col):
        if row > 0:
            if self.board[row - 1][col].real == 0:
                self.neighbours(row - 1, col)
            elif self.board[row - 1][col].real == -1:
                if not self.board[row - 1][col].flagged:
                    self.show_mines()
            else:
                self.reveal(row - 1, col)
        # Check down
        if row < self.height - 1:
            if self.board[row + 1][col].real == 0:
                self.neighbours(row + 1, col)
            elif self.board[row + 1][col].real == -1:
                if not self.board[row + 1][col].flagged:
                    self.show_mines()
            else:
                self.reveal(row + 1, col)
        # Check left
        if col > 0:
            if self.board[row][col - 1].real == 0:
                self.neighbours(row, col - 1)
            elif self.board[row][col - 1].real == -1:
                if not self.board[row][col - 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row, col - 1)
        # Check right
        if col < self.width - 1:
            if self.board[row][col + 1].real == 0:
                self.neighbours(row, col + 1)
            elif self.board[row][col + 1].real == -1:
                if not self.board[row][col + 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row, col + 1)
        # Check top-left
        if row > 0 and col > 0:
            if self.board[row - 1][col - 1].real == 0:
                self.neighbours(row - 1, col - 1)
            elif self.board[row - 1][col - 1].real == -1:
                if not self.board[row - 1][col - 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row - 1, col - 1)
        # Check top-right
        if row > 0 and col < self.width - 1:
            if self.board[row - 1][col + 1].real == 0:
                self.neighbours(row - 1, col + 1)
            elif self.board[row - 1][col + 1].real == -1:
                if not self.board[row - 1][col + 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row - 1, col + 1)
        # Check below-left
        if row < self.height - 1 and col > 0:
            if self.board[row + 1][col - 1].real == 0:
                self.neighbours(row + 1, col - 1)
            elif self.board[row + 1][col - 1].real == -1:
                if not self.board[row + 1][col - 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row + 1, col - 1)
        # Check below-right
        if row < self.height - 1 and col < self.width - 1:
            if self.board[row + 1][col + 1].real == 0:
                self.neighbours(row + 1, col + 1)
            elif self.board[row + 1][col + 1].real == -1:
                if not self.board[row + 1][col + 1].flagged:
                    self.show_mines()
            else:
                self.reveal(row + 1, col + 1)

    def right_click(self, row, col):
        if self.game_over:
            return
        square = self.board[row][col]
        if not self.filled:
            return
        if square.flagged:
            square.flagged = False
            self.flags -= 1
            self.set_seen(row, col, ' ')
        elif square.seen != ' ':
            return
        elif self.flags < self.num_mines:
            square.flagged = True
            self.flags += 1
            self.set_seen(row, col, 'f')

    def reveal(self, row, col):
        self.set_seen(row, col, self.board[row][col].real)

    def set_seen(self, row, col, value):
        square = self.board[row][col]
        square.seen = value
        square.canvas.create_image(0, 0, image=get(value), anchor=tk.NW)

    def fill_board(self, row, col):
        # Track of number of mines already set up
        count = 0
        while count < self.num_mines:

            # Random number from all possible grid positions
            val = random.randint(0, self.width * self.height - 1)

            # Generating row and column from the number
            r = val // self.width
            c = val % self.width

            # Place the mine, if it doesn't already have one
            if row + 1 >= r >= row - 1 and col + 1 >= c >= c - 1:
                continue
            elif self.board[r][c].real != -1:
                count += 1
                self.board[r][c].real = -1

    def get_neighbours(self, row, col):
        neighbours = []
        if row > 0:
            neighbours.append(self.board[row - 1][col])
        # Check down
        if row < self.height - 1:
            neighbours.append(self.board[row + 1][col])
        # Check left
        if col > 0:
            neighbours.append(self.board[row][col - 1])
        # Check right
        if col < self.width - 1:
            neighbours.append(self.board[row][col + 1])
        # Check top-left
        if row > 0 and col > 0:
            neighbours.append(self.board[row - 1][col - 1])
        # Check top-right
        if row > 0 and col < self.width - 1:
            neighbours.append(self.board[row - 1][col + 1])
        # Check below-left
        if row < self.height - 1 and col > 0:
            neighbours.append(self.board[row + 1][col - 1])
        # Check below-right
        if row < self.height - 1 and col < self.width - 1:
            neighbours.append(self.board[row + 1][col + 1])
        return neighbours

    def set_nums(self):
        for row in range(self.height):
            for col in range(self.width):

                if self.board[row][col].real == -1:
                    continue

                # Check up
                if row > 0 and self.board[row - 1][col].real == -1:
                    self.board[row][col].real += 1
                # Check down
                if row < self.height - 1 and self.board[row + 1][col].real == -1:
                    self.board[row][col].real += 1
                # Check left
                if col > 0 and self.board[row][col - 1].real == -1:
                    self.board[row][col].real += 1
                # Check right
                if col < self.width - 1 and self.board[row][col + 1].real == -1:
                    self.board[row][col].real += 1
                # Check top-left
                if row > 0 and col > 0 and self.board[row - 1][col - 1].real == -1:
                    self.board[row][col].real += 1
                # Check top-right
                if row > 0 and col < self.width - 1 and self.board[row - 1][col + 1].real == -1:
                    self.board[row][col].real += 1
                # Check below-left
                if row < self.height - 1 and col > 0 and self.board[row + 1][col - 1].real == -1:
                    self.board[row][col].real += 1
                # Check below-right
                if row < self.height - 1 and col < self.width - 1 and self.board[row + 1][col + 1].real == -1:
                    self.board[row][col].real += 1

    def neighbours(self, row, col):
        # If cell already not visited
        if [row, col] not in self.vis:

            # Mark cell visited
            self.vis.append([row, col])

            # If cell is zero
            if self.board[row][col].real == 0:
                # Display it to user
                self.reveal(row, col)

                # Recursive call on neighbors
                if row > 0:
                    self.neighbours(row - 1, col)
                if row < self.height - 1:
                    self.neighbours(row + 1, col)
                if col > 0:
                    self.neighbours(row, col - 1)
                if col < self.width - 1:
                    self.neighbours(row, col + 1)
                if row > 0 and col > 0:
                    self.neighbours(row - 1, col - 1)
                if row > 0 and col < self.width - 1:
                    self.neighbours(row - 1, col + 1)
                if row < self.height - 1 and col > 0:
                    self.neighbours(row + 1, col - 1)
                if row < self.height - 1 and col < self.width - 1:
                    self.neighbours(row + 1, col + 1)

            # If cell not zero
            if self.board[row][col].real != 0:
                self.reveal(row, col)

    def check_over(self):
        count = 0

        # Check each cell
        for row in range(self.height):
            for col in range(self.width):

                # If cell not empty or flagged
                if self.board[row][col].seen != ' ' and not self.board[row][col].flagged:
                    count += 1

        # Count comparison
        if count == self.width * self.height - self.num_mines:
            self.show_mines()
            self.game_over = True
        else:
            return False

    def show_mines(self):
        self.game_over = True
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row][col].real == -1:
                    self.reveal(row, col)

    def build_gui(self):
        window.columnconfigure([x for x in range(self.width)], minsize=25)
        window.rowconfigure([y for y in range(self.height)], minsize=25)

        for row in range(self.height):
            for col in range(self.width):
                self.board[row][col].canvas.grid(row=row, column=col)


def print_mines_layout():
    global mine_values
    global n

    print()
    print("\t\t\tMINESWEEPER\n")

    st = "   "
    for i in range(n):
        st = st + "     " + str(i + 1)
    print(st)

    for r in range(n):
        st = "     "
        if r == 0:
            for col in range(n):
                st = st + "______"
            print(st)

        st = "     "
        for col in range(n):
            st = st + "|     "
        print(st + "|")

        st = "  " + str(r + 1) + "  "
        for col in range(n):
            st = st + "|  " + str(mine_values[r][col]) + "  "
        print(st + "|")

        st = "     "
        for col in range(n):
            st = st + "|_____"
        print(st + '|')

    print()


# Referenced https://stackoverflow.com/questions/53861528/runtimeerror-too-early-to-create-image/53861790
imagelist = {
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
    ' ': ['images/facingDown.png', None],
}


def get(name):
    if name in imagelist:
        if imagelist[name][1] is None:
            imagelist[name][1] = tk.PhotoImage(file=imagelist[name][0])
        return imagelist[name][1]
    return None


if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] != 'Beginner' and sys.argv[1] != 'Intermediate' and sys.argv[1] != 'Expert':
            print("Invalid Input")
            sys.exit()
        diff = sys.argv[1]
    else:
        print("Invalid Input")
        sys.exit()

    window = tk.Tk()
    window.resizable(False, False)

    game = Game(diff)

    game.build_gui()

    window.mainloop()