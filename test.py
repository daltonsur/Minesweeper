import unittest
import minesweeper.minesweeper as ms


class TestBoardIcons(unittest.TestCase):
    def test_starts_uninitialized(self):
        for elem in ms.BoardIcons._image_list.values():
            self.assertIsNone(elem[1])


if __name__ == '__main__':
    unittest.main()
