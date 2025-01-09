#!/home/kheninge/virtual_envs/sudsolver/bin/python3

from PySide6.QtWidgets import QApplication
from sudoku_gui import SSolveMain
import sudoku
import yaml


def main():
    ### Read the yaml file, convert the dictionary list to tuples in the format
    ### expected by Sudoku class
    with open("sudoku.yaml", "r") as file:
        stored_puzzles = yaml.safe_load(file)

    puzzles_ninesquare_fmt = convert_to_ns_format(stored_puzzles)

    app = QApplication()
    puzzle = sudoku.Sudoku()
    window = SSolveMain(app, puzzle, puzzles_ninesquare_fmt)
    window.show()
    app.exec()


def convert_to_ns_format(puzzles: dict) -> dict[str, sudoku.SudokuVal]:
    ret_val = {}
    for title, puzzle in puzzles.items():
        ns_list = []  # list of nine nineSquares
        for i in range(9):
            ns_list.append([])
        for i, val in enumerate(str(puzzle)):
            ns_col = (i % 9) // 3
            ns_row = i // 27
            if val == "0":
                intified_val = None
            else:
                intified_val = int(val)
            ns_list[ns_row * 3 + ns_col].append(intified_val)
        ns_tup = []
        for i in ns_list:
            ns_tup.append(tuple(i))
        ret_val[title] = tuple(ns_tup)
    return ret_val


if __name__ == "__main__":
    main()
