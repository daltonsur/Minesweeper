import unittest
from minesweeper.minesweeper import *


class TestBoardIcons(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tk.Tk()

    def test_returns_image_for_all_possible_inputs(self):
        for value in CellValue:
            self.assertIsInstance(BoardIcons.get(value), tk.PhotoImage)

    def test_returns_same_image_for_same_input(self):
        self.assertEquals(BoardIcons.get(CellValue.ZERO),
                          BoardIcons.get(CellValue.ZERO))


if __name__ == '__main__':
    unittest.main()
