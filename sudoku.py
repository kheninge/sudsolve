import logging

logger = logging.getLogger(__name__)


class Cell:
    """Datastructure to represent the state of a single cell includes:
    * Initial state of the puzzle
    * Solved value
    * Possible values given the other solved states
    * Cell ID
    * Pointer to the next cell in the row, column and nineSquare
    Methods:
    init() - takes an integer 0-9 or None. Copies to the initial and solved state
    progress = elimination_to_one_loop() - loop through row, column and square loops and eliminate possibilities
                         if the possibility is limited to one then set the solved field.
                         returns true if new success is found or possibilities are improved
    *"""

    def __init__(self, id: int = 0, initial: int | None = None) -> None:
        self.id: int = id
        self._check_input_values(initial)
        self._solved_value: int | None = None
        self._potentials: set[int] = set(range(1, 10))
        self._next: dict[str, "None | Cell"] = {
            "row": None,
            "col": None,
            "square": None,
        }
        self.init(initial)

    def _check_input_values(self, val: int | None) -> None:
        """cell can be initialized to a digit 1 - 9 or to None
        val is either a single int or a set of ints"""
        if val is not None:
            if type(val) is not int:
                raise ValueError
            if val < 1 or val > 9:
                raise ValueError

    @property
    def rnext(self) -> "Cell | None":
        return self._next["row"]

    @rnext.setter
    def rnext(self, pointer: "Cell | None") -> None:
        self._next["row"] = pointer

    @property
    def cnext(self) -> "Cell | None":
        return self._next["col"]

    @cnext.setter
    def cnext(self, pointer: "Cell | None"):
        self._next["col"] = pointer

    @property
    def snext(self) -> "Cell | None":
        return self._next["square"]

    @snext.setter
    def snext(self, pointer: "Cell | None"):
        self._next["square"] = pointer

    @property
    def solution(self) -> int | None:
        return self._solved_value

    @property
    def initial(self) -> int | None:
        return self._initial_value

    @property
    def potentials(self) -> set[int]:
        return self._potentials

    def clear_potentials(self) -> None:
        self._potentials.clear()

    def add_potential(self, val: int) -> None:
        self._check_input_values(val)
        self._potentials.add(val)

    def remove_potential(self, val: int) -> None:
        self._check_input_values(val)
        if val in self._potentials:
            self._potentials.remove(val)

    def _set_solution(self, val: int) -> None:
        """Set the solution field. Clear the potentials field. Go through all visible c-spaces and remove solved value from their potentials"""
        self._solved_value = val
        self.clear_potentials()
        logger.info("Cell %d: Solution found: %d", self.id, self._solved_value)
        # For all visibile c spaces, remove solved value from potentials
        for direction in self._next:
            cell = self._next[direction]
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                cell.remove_potential(val)
                cell = cell._next[direction]

    def init(self, val: int | None) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        logger.debug("Init is called for Cell %d", self.id)
        self._check_input_values(val)
        if val is not None:
            # TODO should I just call _set_solution here?
            self._initial_value = val
            self._solved_value = val
            self.clear_potentials()
        else:
            self._initial_value = None
            self._solved_value = None

    def elimination_to_one_loop(self) -> bool:
        """Eliminate all solutions seen in constrained spaces and if a single potential is left designate it
        the solution"""
        potential_starting_len = len(self.potentials)
        if self.solution:
            # Already solved
            return False

        # Iterate over row, col and square. Remove potentials for any solution
        for direction in self._next:
            cell = self._next[direction]
            count = 1
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if cell.solution:
                    self.remove_potential(cell.solution)
                cell = cell._next[direction]
                count += 1
                ## Error condition, should never be more than 9 cells in a loop
                if count > 9:
                    logger.error(
                        "Cell %d is looping more than 9 times for %s direction",
                        self.id,
                        direction,
                    )
                    raise Exception("Elimination_to_one has an infinite loop")

        if len(self._potentials) == 1:
            # Solved
            mysolution = self._potentials.pop()
            self._set_solution(mysolution)
        if len(self._potentials) < potential_starting_len:
            logger.debug(
                "Cell %d Elimination_to_one made progress on potentials", self.id
            )
            return True
        else:
            logger.debug(
                "Cell %d Elimination_to_one didn't make progress on potentials", self.id
            )
            return False

    def single_possible_location(self) -> bool:
        """Look through potentials determined by other rules. If a potential number is only present within this cell
        for a given constrained space, then that is the solution"""

        if self.solution:
            # Already solved
            return False

        # Iterate over row, col and square.
        for direction in self._next:
            # First pass, gather statistics on potential counts in pot_count
            pot_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
            pot_list = set()
            # First examine yourself
            for num in self.potentials:
                pot_count[num] += 1
            # Then look at others in the network
            cell = self._next[direction]
            while cell != self:  # stop when you get to the end of the loop
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                for num in cell.potentials:
                    pot_count[num] += 1
                cell = cell._next[direction]
            # Analyze potential_count statistics to see if there are any unique (just one) potential
            # If so then build a list of those numbers
            for num, count in pot_count.items():
                if count == 1:
                    pot_list.add(num)
            # Now see if any of our cell potentials is in the list, if so set it as the solution
            for num in self.potentials:
                if num in pot_list:
                    self._set_solution(num)
                    return True
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
    * elimination_to_one_loop() - iterate through all cells and call their elimination_to_one_loop method
                        returns true if any of them made progress
    """

    def __init__(self, id: int = 0) -> None:
        self.id = id
        self.ns = []  # A list of cells to represent a NineSquare
        # Instantiate Cells
        for i in range(9):
            # TODO - 9 is hard code everywhere. Should it be a macro?
            self.ns.append(Cell(self.id * 9 + i))
        # Connect up rows of the NineSquare
        for i in (0, 3, 6):
            self.ns[i].rnext = self.ns[i + 1]
            self.ns[i + 1].rnext = self.ns[i + 2]
            self.ns[i + 2].rnext = self.ns[i]
        # Connect up columns of the NineSquare
        for i in range(3):
            self.ns[i].cnext = self.ns[i + 3]
            self.ns[i + 3].cnext = self.ns[i + 6]
            self.ns[i + 6].cnext = self.ns[i]
        # Connect up the NineSquare Loop
        for i in range(8):
            self.ns[i].snext = self.ns[i + 1]
        self.ns[8].snext = self.ns[0]

    def initialize(self, vals: tuple[int | None]) -> None:
        for i in range(9):
            self.ns[i].init(vals[i])

    @property
    def solutions(self) -> tuple[int]:
        sols = []
        for i in range(9):
            sols.append(self.ns[i].solution)
        return tuple(sols)

    def cell(self, row: int, col: int) -> Cell:
        """returns a cell pases on row and column coordinates"""
        i = row * 3 + col
        return self.ns[i]

    def attach_row(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another to the right"""
        self.ns[2].rnext = other.cell(0, 0)
        self.ns[5].rnext = other.cell(1, 0)
        self.ns[8].rnext = other.cell(2, 0)

    def attach_col(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another below"""
        self.ns[6].cnext = other.cell(0, 0)
        self.ns[7].cnext = other.cell(0, 1)
        self.ns[8].cnext = other.cell(0, 2)

    def elimination_to_one_loop(self) -> bool:
        logger.debug("NineSquare %d starting elimination_to_one_loop", self.id)
        total_result = False
        for i in range(9):
            total_result |= self.ns[i].elimination_to_one_loop()
        logger.debug(
            "NineSquare %d completing elimination_to_one_loop, result is ",
            self.id,
            total_result,
        )
        return total_result

    def single_possible_location(self) -> bool:
        logger.debug("NineSquare %d starting single_possible_location", self.id)
        total_result = False
        for i in range(9):
            total_result |= self.ns[i].single_possible_location()
        logger.debug(
            "NineSquare %d completing single_possible_location, result is ",
            self.id,
            total_result,
        )
        return total_result


class Sudoku:
    """Represents the datastructure for a full Sudoku mesh and includes methods
    for solving the Sudoku. Includes:
    9 NineSquare Objects in an ordered list 0-8
        | 0 | 1 | 2 |
        | 3 | 4 | 5 |
        | 6 | 7 | 8 |

    initialize() - Given a tuple of 81 values. Actually a tuple of nine tuples in NineSquare order
      (0  1  2 9 10 11 18 19 20) ( 3 4 5 ... ) (6 7 8 ... )

    solutions() - output a tuple of 81 values with the current state of solutions. Same format as initialize tuple
    puzzle_print() - print the current state of the puzzle in a text output
    Methods for solving the sudoku puzzle:
        * Elimination to one (possibility paring)
        * Aligned possibilities
        * Filled pairs
        * Filled triplets
        * Inferred line
    """

    def __init__(self) -> None:
        self.sudoku = []
        for i in range(9):
            self.sudoku.append(NineSquare(i))
        # Connect up the rows
        for i in (0, 3, 6):
            self.sudoku[i].attach_row(self.sudoku[i + 1])
            self.sudoku[i + 1].attach_row(self.sudoku[i + 2])
            self.sudoku[i + 2].attach_row(self.sudoku[i])
        # Connect up the columns
        for i in range(3):
            self.sudoku[i].attach_col(self.sudoku[i + 3])
            self.sudoku[i + 3].attach_col(self.sudoku[i + 6])
            self.sudoku[i + 6].attach_col(self.sudoku[i])

    def initialize(self, init_val: tuple[tuple[int | None]]) -> None:
        for i in range(9):
            self.sudoku[i].initialize(init_val[i])
        logger.info("Sudoku Class finished initialization")

    @property
    def solutions(self) -> tuple[tuple[int]]:
        sols = []
        for i in range(9):
            sols.append(self.sudoku[i].solutions)
        return tuple(sols)

    def elimination_to_one(self) -> bool:
        """Run the elimination to one algorithm for each non-solved
        cell. Returns true if a new solution is found or if a possibility is
        altered. Returns false if after trying all cells no new information
        is discovered"""
        logger.info("Sudoku Class starting elimination_to_one")
        total_result = False
        for square in self.sudoku:
            total_result |= square.elimination_to_one_loop()
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        return total_result

    def single_possible_location(self) -> bool:
        """Run the single possible location algorithm for each non-solved
        cell. Returns true if a new solution is found"""

        logger.info("Sudoku Class starting single_possible_location")
        total_result = False
        for square in self.sudoku:
            total_result |= square.single_possible_location()
        logger.info(
            "Sudoku Class finishing single_possible_location result is %d", total_result
        )
        return total_result
