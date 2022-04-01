import unittest
from minesweeper.minesweeper import *


class TestCellValues(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tk.Tk()

    def test_all_values_have_image(self):
        for value in CellValue:
            self.assertIsInstance(value.image, tk.PhotoImage)

    def test_returns_same_image_for_same_value(self):
        self.assertEqual(CellValue.ZERO.image, CellValue.ZERO.image)


if __name__ == '__main__':
    unittest.main()
