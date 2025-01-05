class Cell:
    """Datastructure to represent the state of a single cell includes:
    * Initial state of the puzzle
    * Solved value
    * Possible values given the other solved states
    * Cell ID
    * Pointer to the next cell in the row, column and nineSquare
    Methods:
    init() - takes an integer 0-9 or None. Copies to the initial and solved state
    progress = elimination_loop() - loop through row, column and square loops and eliminate possibilities
                         if the possibility is limited to one then set the solved field.
                         returns true if new success is found or possibilities are improved
    *"""

    def __init__(self, initial=None) -> None:
        self._check_valid_values(initial)
        self._potentials = set(range(1, 10))
        self.init(initial)
        self._rnext = None
        self._cnext = None
        self._snext = None

    @property
    def rnext(self):
        return self._rnext

    @rnext.setter
    def rnext(self, pointer):
        self._rnext = pointer

    @property
    def cnext(self):
        return self._cnext

    @cnext.setter
    def cnext(self, pointer):
        self._cnext = pointer

    @property
    def snext(self):
        return self._snext

    @snext.setter
    def snext(self, pointer):
        self._snext = pointer

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
            self.clear_potentials()
        else:
            self._initial_value = None
            self._solved_value = None

    @property
    def solution(self):
        return self._solved_value

    @property
    def initial(self):
        return self._initial_value

    @property
    def potentials(self):
        return self._potentials

    def clear_potentials(self):
        self._potentials.clear()

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
                if item in self._potentials:
                    self._potentials.remove(item)
        else:
            if val in self._potentials:
                self._potentials.remove(val)

    def elimination_loop(self) -> bool:
        potential_starting_len = len(self.potentials)

        # Iterate over row
        cell = self.rnext
        while cell != self:  # stop when you get to the end of the loop
            if cell.solution:
                self.remove_potentials(cell.solution)
            cell = cell.rnext
        # Iterate over column
        cell = self.cnext
        while cell != self:  # stop when you get to the end of the loop
            if cell.solution:
                self.remove_potentials(cell.solution)
            cell = cell.cnext
        # Iterate over NineSquare
        cell = self.snext
        while cell != self:  # stop when you get to the end of the loop
            if cell.solution:
                self.remove_potentials(cell.solution)
            cell = cell.snext

        if len(self._potentials) == 1:
            self._solved_value = self._potentials.pop()
            self.clear_potentials()
        if len(self._potentials) < potential_starting_len:
            return True
        else:
            return False


class NineSquare:
    """Represents the 9 cells in a Sudoku square.
    Provides a building block for building out a full Sudoku Mesh
    Instantiate and connect 9 cells in a square
    Connect the 2 row pointer
    * initialize(vals) - takes a tuple of 9 values and assigns them to the nine cells
    * attach_row(self, some_nine_square) - connect the given nine square to self's pointers
    * attach_col(self, some_nine_square) - connect the given nine square to self's pointers
    * cell(row, col) - given a row, column returns the cell at that location
    * elimination_loop() - iterate through all cells and call their elimination_loop method
                        returns true if any of them made progress
    """

    def __init__(self) -> None:
        self.ns = []
        # Instantiate Cells
        for i in range(9):
            self.ns.append(Cell())
        # Connect up rows
        for i in range(0, 9, 3):
            self.ns[i].rnext = self.ns[i + 1]
            self.ns[i + 1].rnext = self.ns[i + 2]
        # Connect up columns
        for i in range(3):
            self.ns[i].cnext = self.ns[i + 3]
            self.ns[i + 3].cnext = self.ns[i + 6]
        # Connect up the NineSquare Loop
        for i in range(8):
            self.ns[i].snext = self.ns[i + 1]
        self.ns[8].snext = self.ns[0]

    def initialize(self, vals: tuple):
        for i in range(9):
            self.ns[i].init(vals[i])

    def cell(self, r: int, c: int):
        i = r * 3 + c
        return self.ns[i]

    def attach_row(self, other) -> None:
        self.ns[2].rnext = other.cell(0, 0)
        self.ns[5].rnext = other.cell(1, 0)
        self.ns[8].rnext = other.cell(2, 0)

    def attach_col(self, other) -> None:
        self.ns[6].cnext = other.cell(0, 0)
        self.ns[7].cnext = other.cell(0, 1)
        self.ns[8].cnext = other.cell(0, 2)

    def elimination_loop(self) -> bool:
        total_result = False
        for i in range(9):
            result = self.ns[i].elimination_loop()
            total_result = result or total_result
        return total_result


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
