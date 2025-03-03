#!/home/kheninge/virtual_envs/sudsolver/bin/python3

# The below lines are read by the nuitka tool used to compile this script
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/sudoku.yaml=sudoku.yaml
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --mode=onefile
#
# Linux Compile command: python3 -m nuitka sudsolver.py

from PySide6.QtWidgets import QApplication
from gui.gui_top import GuiTop
from sudoku.sudoku import Sudoku
from sudoku.puzzleio import PuzzleList

PUZZLE_YAML_FILE = "sudoku.yaml"
HELP_FILE = "help.md"


def main():
    puzzles = PuzzleList(PUZZLE_YAML_FILE)

    # Model/Control
    solver = Sudoku()
    # Gui
    app = QApplication()
    gui = GuiTop(app, solver, puzzles, HELP_FILE)
    gui.start()


if __name__ == "__main__":
    main()
