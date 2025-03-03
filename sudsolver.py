#!/home/kheninge/virtual_envs/sudsolver/bin/python3

# The below lines are read by the nuitka tool used to compile this script
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/sudoku.yaml=sudoku.yaml
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --mode=onefile
#
# Linux Compile command: python3 -m nuitka sudsolver.py

from PySide6.QtWidgets import QApplication
from gui.gui_top import GuiTop
from sudoku.sudoku import Sudoku, PuzzleFormat
from sudoku.puzzleio import PuzzleList
import yaml
from pathlib import Path

PUZZLE_YAML_FILE = "sudoku.yaml"
HELP_FILE = "help.md"


def main():
    puzzles = PuzzleList(PUZZLE_YAML_FILE)
    # # Read the yaml file, convert the dictionary list to SudokuVal format
    # p = Path(__file__).with_name(PUZZLE_YAML_FILE)
    # with p.open("r") as file:
    #     stored_puzzles = yaml.safe_load(file)
    # puzzles_ninesquare_fmt = convert_to_ns_format(stored_puzzles)

    # Model/Control
    solver = Sudoku()
    # Gui
    app = QApplication()
    gui = GuiTop(app, solver, puzzles, HELP_FILE)
    gui.start()


if __name__ == "__main__":
    main()
