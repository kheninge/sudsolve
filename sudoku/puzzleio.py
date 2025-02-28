from ruamel.yaml import YAML
from sudoku.defines import PuzzleFormat


class PuzzleList:
    def __init__(self, puzzle_file):
        self.yaml = YAML()
        self.puzzles = {}
        with open(puzzle_file, "r") as file:
            self.puzzles = self.yaml.load(file)

    def delete(self, puzzle: str):
        del self.puzzles[puzzle]

    def add(self, puzzle: str, puzzle_str: str):
        # Ignore an attempt to add a new puzzle with the same name
        if puzzle in self.puzzles:
            return
        self.puzzles[puzzle] = puzzle_str

    def write(self, puzzle_file: str):
        with open(puzzle_file, "w") as file:
            self.yaml.dump(self.puzzles, file)


def convert_to_ns_format(puzzle: str) -> PuzzleFormat:
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
    return tuple(ns_tup)
