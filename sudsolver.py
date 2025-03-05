#!/home/kheninge/virtual_envs/sudsolver/bin/python3

# The below lines are read by the nuitka tool used to compile this script
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/sudoku.yaml=sudoku.yaml
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --mode=onefile
#
# Linux Compile command: python3 -m nuitka sudsolver.py

import os
from PySide6.QtWidgets import QApplication
from gui.gui_top import GuiTop
from sudoku.sudoku import Sudoku
from sudoku.puzzleio import PuzzleList

PUZZLE_YAML_FILE = "sudoku.yaml"
HELP_FILE = "help.md"


def main():
    path = os.path.dirname(__file__)
    yaml_full_path = os.path.join(path, PUZZLE_YAML_FILE)
    help_full_path = os.path.join(path, HELP_FILE)
    puzzles = PuzzleList(yaml_full_path)

    # Model/Control
    solver = Sudoku()
    # Gui
    app = QApplication()
    gui = GuiTop(app, solver, puzzles, help_full_path)
    gui.start()


if __name__ == "__main__":
    main()
