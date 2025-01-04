class Cell:
    """Datastructure to represent the state of a single cell includes:
    * Initial state of the puzzle
    * Solved value
    * Possible values given the other solved states
    * Cell ID
    * Pointer to the next cell in the row, column and nineSquare
    Methods:
    init() - takes an integer 0-9 or None. Copies to the initial and solved state
    *"""

    _potentials = set()

    def __init__(self, initial=None) -> None:
        self._check_valid_values(initial)
        self._initial_value = initial
        self._solved_value = initial

    def _check_valid_values(self, val):
        """cell can be initialized to a digit 1 - 9 or to None
        val is either a single int or a set of ints"""
        if val is not None:
            # Could be a set
            if isinstance(val, set):
                for item in val:
                    if type(item) is not int:
                        raise ValueError
                    if item < 1 or item > 9:
                        raise ValueError
            else:
                # Could be a scalar
                if type(val) is not int:
                    raise ValueError
                if val < 1 or val > 9:
                    raise ValueError

    def init(self, val) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        self._check_valid_values(val)
        if val is not None:
            self._initial_value = val
            self._solved_value = val
        else:
            self._initial_value = None
            self._solved_value = None

    def solved(self):
        return self._solved_value

    def initial(self):
        return self._initial_value

    def potentials(self):
        return self._potentials

    def add_potentials(self, val):
        self._check_valid_values(val)
        if isinstance(val, set):
            self._potentials.update(val)
        else:
            self._potentials.add(val)

    def remove_potentials(self, val):
        self._check_valid_values(val)
        if isinstance(val, set):
            for item in val:
                self._potentials.remove(item)
        else:
            self._potentials.remove(val)


class NineSquare:
    """Represents the 9 cells in a Sudoku square.
    Provides a building block for building out a full Sudoku Mesh"""

    pass


class Sudoku:
    """Represents the datastructure for a full Sudoku mesh and includes methods
    for solving the Sudoku. Includes:
    9 NineSquare Objects in an ordered list 0-8
        | 0 | 1 | 2 |
        | 3 | 4 | 5 |
        | 6 | 7 | 8 |

    puzzle_init() - Given a tuple of 81 values, initialize the cells
    puzzle_print() - print the current state of the puzzle in a text output
    Methods for solving the sudoku puzzle:
        * Elimination to one (possibility paring)
        * Aligned possibilities
        * Filled pairs
        * Filled triplets
        * Inferred line
    """

    def __init__(self) -> None:
        pass

    def elimination_to_one(self) -> bool:
        """Run the elimination to one algorithm for each non-solved
        cell. Returns true if a new solution is found or if a possibility is
        altered. Returns false if after trying all cells no new information
        is discovered"""
        return True
