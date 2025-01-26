#!/home/kheninge/virtual_envs/sudsolver/bin/python3

# The below lines are read by the nuitka tool used to compile this script
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/sudoku.yaml=sudoku.yaml
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --mode=onefile
#
# Linux Compile command: python3 -m nuitka sudsolver.py

from PySide6.QtWidgets import QApplication
from sudoku_gui import SSolveMain
import sudoku
import yaml
from pathlib import Path

PUZZLE_YAML_FILE = "sudoku.yaml"


def main():
    # Read the yaml file, convert the dictionary list to SudokuVal format
    p = Path(__file__).with_name(PUZZLE_YAML_FILE)
    with p.open("r") as file:
        stored_puzzles = yaml.safe_load(file)
    puzzles_ninesquare_fmt = convert_to_ns_format(stored_puzzles)

    # Model
    solver = sudoku.Sudoku()
    # Gui
    app = QApplication()
    window = SSolveMain(app, solver, puzzles_ninesquare_fmt)
    window.show()
    app.exec()


def convert_to_ns_format(puzzles: dict) -> dict[str, sudoku.SudokuValType]:
    converted_puzzle_d = {}
    for title, puzzle in puzzles.items():
        ns_list = []  # list of nine empty nineSquare lists
        for i in range(9):
            ns_list.append([])
        for i, val in enumerate(str(puzzle)):
            # 0 is a blank or a non solved cell
            solution = None if val == "0" else int(val)
            # Determine which nine-square to put the solution into
            ns_col = (i % 9) // 3
            ns_row = i // 27
            ns_list[ns_row * 3 + ns_col].append(solution)
        ns_tup = []
        # Convert the list of lists to a tuple of tuples and add it to a dictionary of puzzles
        for i in ns_list:
            ns_tup.append(tuple(i))
        converted_puzzle_d[title] = tuple(ns_tup)
    return converted_puzzle_d


if __name__ == "__main__":
    main()
