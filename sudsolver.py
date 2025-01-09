#!/home/kheninge/virtual_envs/sudsolver/bin/python3

from PySide6.QtWidgets import QApplication
from sudoku_gui import SSolveMain
import sudoku


def main():
    init1 = (
        (2, None, None, 5, 7, None, None, 1, None),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (None, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, None, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )

    app = QApplication()
    puzzle = sudoku.Sudoku()
    puzzle.initialize(init1)
    window = SSolveMain(app, puzzle)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
