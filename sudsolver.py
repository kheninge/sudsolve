#!/home/kheninge/virtual_envs/sudsolver/bin/python3

from PySide6.QtWidgets import QApplication
from sudoku_gui import SSolveMain


def main():
    app = QApplication()
    window = SSolveMain()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
