import logging
import itertools
from typing import TypeAlias

logger = logging.getLogger(__name__)

## Define some types
CellValType: TypeAlias = int | None
NineSquareValType: TypeAlias = tuple[CellValType, ...]
SudokuValType: TypeAlias = tuple[NineSquareValType, ...]


# TODO:
# *  Publish as an executable to windows
# *  Publish to linux and mac?


class Cell:
    """Datastructure to represent the state of a single cell includes:
    * Initial state of the puzzle
    * Solved value
    * Possible values given the other solved states
    * Cell ID
    * Pointer to the next cell in the row, column and nineSquare
    Methods:
    init() - takes an integer 0-9 or None. Copies to the initial and solved state
    run_rule(rule) - Takes these
    *"""

    def __init__(self, id: int = 0, initial: CellValType = None) -> None:
        self.id: int = id
        self._check_cell_is_legal(initial)
        self._solved_value: CellValType = None
        self._new_solution: bool = False
        self._potentials: set[int] = set(range(1, 10))
        self._next: dict[str, "None | Cell"] = {
            "row": None,
            "col": None,
            "square": None,
        }
        self.rules = {
            "update_potentials": self._update_potentials,
            "elimination_to_one": self._rule_elimination_to_one,
            "single_possible_location": self._rule_single_possible_location,
            "matched_pairs": self._rule_matched_pairs,
        }
        self.initialize(initial)

    def _check_cell_is_legal(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None
        val is either a single int or a set of ints"""
        if val is not None:
            if type(val) is not int:
                raise ValueError
            if val < 1 or val > 9:
                raise ValueError
        logger.debug("Cell Value for cell id %d is legal", self.id)

    def _check_network_connection(self) -> bool:
        """Check to make sure everything is connected properly for this cell; make sure no endless loops
        on network traversals."""
        # Iterate over row, col and square.
        for direction in self._next:
            cell = self
            count = 0
            while True:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
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
                if cell == self:
                    break
        return True

    @property
    def connection_ok(self) -> bool:
        return self._check_network_connection()

    @property
    def solved(self) -> bool:
        return self.solution is not None

    @property
    def new_solution(self) -> bool:
        return self._new_solution

    def clear_new_solution(self) -> None:
        self._new_solution = False

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
    def solution(self) -> CellValType:
        return self._solved_value

    @property
    def initial(self) -> CellValType:
        return self._initial_value

    @property
    def potentials(self) -> set[int]:
        return self._potentials

    def clear_potentials(self) -> None:
        self._potentials.clear()

    def add_potential(self, val: int) -> None:
        self._check_cell_is_legal(val)
        self._potentials.add(val)

    def remove_potential(self, val: int) -> None:
        self._check_cell_is_legal(val)
        if val in self._potentials:
            self._potentials.remove(val)

    def check_consistency(self) -> bool:
        """Check that current solution state is legal. Used to catch any logic problems early, shouldn't find them
        if there are no errors"""

        for direction in self._next:
            solution_count = dict.fromkeys(range(1, 10), 0)
            cell = self
            while True:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if cell.solution:
                    solution_count[cell.solution] += 1
                cell = cell._next[direction]
                if cell == self:
                    break
            for i in solution_count:
                if solution_count[i] > 1:
                    logger.error("Found solution inconsistency for solution %d", i)
                    return False
        return True

    def _set_solution(self, val: int) -> None:
        """Set the solution field. Clear the potentials field. Go through all visible c-spaces and remove solved value from their potentials"""
        self._solved_value = val
        self._new_solution = True
        self.clear_potentials()
        logger.info("Cell %d: Solution found: %d", self.id, self._solved_value)
        # For all visibile c spaces, remove solved value from potentials
        self._remove_potential_in_cspaces(val)

    def _remove_potential_in_cspaces(self, val: int) -> None:
        for direction in self._next:
            cell = self._next[direction]
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                cell.remove_potential(val)
                cell = cell._next[direction]

    def initialize(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        logger.debug("Init is called for Cell %d", self.id)
        self._check_cell_is_legal(val)
        if val is not None:
            self._initial_value = val
            # Can't  just call _set_solution here as network isn't guarenteed to be set up yet
            self._solved_value = val
            self.clear_potentials()
        else:
            self._initial_value = None
            self._solved_value = None
            self._potentials = set(range(1, 10))

    def _update_potentials(self) -> bool:
        """Loop through all cstates and remove potentials from the list for any present
        This is the first step before any rule, so making this a seperate function so it can be called by each
        rule"""

        potential_starting_len = len(self.potentials)
        for direction in self._next:
            cell = self._next[direction]
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if cell.solution:
                    self.remove_potential(cell.solution)
                cell = cell._next[direction]

            if not self.potentials:
                logger.error(
                    "Something wrong with puzzle, potentials for cell %d is empty",
                    self.id,
                )
        if len(self._potentials) < potential_starting_len:
            logger.debug("Cell %d made progress on potentials", self.id)
            return True
        else:
            return False

    def _gather_multiples(self, mode: int, direction: str) -> set[int]:
        """Traverse the space looking for mode number of occurences in potentials i.e. singles, pairs, triplets etc
        Returns a set of those potentials"""
        pot_count = dict.fromkeys(range(1, 10), 0)
        pot_list = set()
        cell = self
        while True:
            if cell is None:
                raise Exception("Cell network is not set up correctly")
            for num in cell.potentials:
                pot_count[num] += 1
            cell = cell._next[direction]
            if cell == self:
                break
        # Analyze potential_count statistics to see if there are any unique (just one) potential
        # If so then build a list of those numbers
        for num, count in pot_count.items():
            if count == mode:
                pot_list.add(num)
        return pot_list

    def run_rule(self, rule: str) -> bool:
        """Wrapper for running rules listed in rule"""
        self.clear_new_solution()
        if rule not in self.rules.keys():
            logger.error("In run_rule, %s rule is called but not defined", rule)
            raise Exception("Undefine rule called")

        if self.solution:
            # Already solved
            return False

        _ = self._update_potentials()
        return self.rules[rule]()

    def _rule_elimination_to_one(self) -> bool:
        """Eliminate all solutions seen in constrained spaces and if a single potential is left designate it
        the solution"""
        progress = False
        if len(self._potentials) == 1:
            # Solved
            mysolution = self._potentials.pop()
            self._set_solution(mysolution)
            progress = True

        return progress

    def _rule_single_possible_location(self) -> bool:
        """Look through potentials determined by other rules. If a potential number is only present within this cell
        for a given constrained space, then that is the solution"""

        # Iterate over row, col and square.
        for direction in self._next:
            singles_set = self._gather_multiples(1, direction)
            # Now see if any of our cell potentials is in the list, if so set it as the solution
            for num in self.potentials:
                if num in singles_set:
                    self._set_solution(num)
                    return True  # short circuit if solution found
        return False

    def _rule_matched_pairs(self) -> bool:
        total_return = False

        for direction in self._next:
            logger.debug("In rule_matched_pairs, direction is %s", direction)
            pairs_set = self._gather_multiples(2, direction)
            total_num_pairs = len(pairs_set)
            # 2 is the minimum that can match
            if total_num_pairs < 2:
                continue
            # Check to see if subset number of pairs only shows up in that number of  cells. If so then they are "matched"
            # e.g. 2 pairs that only potentially exist in 2 cells or 3 pairs that only potentially exist in 3 cells
            for subset_num_pairs in range(2, total_num_pairs + 1):
                # For every number of pairs from 2 to number of pairs found pick a combination of N choose n
                combinations = itertools.combinations(pairs_set, subset_num_pairs)
                for combo in combinations:
                    matching_cells = []
                    # TODO this traversal of the c space has to be generalized into a function of some sort
                    cell = self
                    while True:
                        if cell is None:
                            raise Exception("Cell network is not set up correctly")
                        if cell.potentials.intersection(combo):
                            matching_cells.append(cell)
                        cell = cell._next[direction]
                        if cell == self:
                            break
                    if len(matching_cells) == subset_num_pairs:
                        # We have found a set of matched pairs, now go through each cell and eliminate any potential
                        # that is not part of the matched pair combination
                        for c in matching_cells:
                            current_pots = c.potentials.copy()
                            for p in current_pots:
                                if p not in combo:
                                    c.remove_potential(p)
                                    # success! we actually removed a potential
                                    total_return |= True
        return total_return


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
        self.id: int = id
        self.ns: list[Cell] = []  # A list of cells to represent a NineSquare
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

    def initialize(self, vals: NineSquareValType) -> None:
        for i in range(9):
            self.ns[i].initialize(vals[i])

    @property
    def solved(self) -> bool:
        all_solved = True
        for cell in self.ns:
            all_solved &= cell.solved
        return all_solved

    @property
    def solutions(self) -> NineSquareValType:
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

    def check_consistency(self) -> bool:
        total_result = True
        for i in range(9):
            total_result &= self.ns[i].check_consistency()
        return total_result

    def run_rule(self, rule: str) -> bool:
        """Wrapper to send the generic rule to each of the cells"""
        logger.info("NineSquare %d starting rule %s", self.id, rule)
        total_result = False
        for i in range(9):
            total_result |= self.ns[i].run_rule(rule)
        logger.debug(
            "NineSquare %d completing %s, result is %d",
            self.id,
            rule,
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

    initialize(tuple) -  if tuple is given, loads that tuple, otherwise re-initializes the last one loaded set/reset the state of the puzzle to initial state specified by load function
    Given a tuple of 81 values. Actually a tuple of nine tuples in NineSquare order
      (0  1  2 9 10 11 18 19 20) ( 3 4 5 ... ) (6 7 8 ... )

    solutions() - output a tuple of 81 values with the current state of solutions. Same format as initialize tuple
    Methods for solving the sudoku puzzle:
        * Elimination to one (possibility paring)
        * Single Possible Location
        * Aligned possibilities
        * Filled pairs
        * Filled triplets
        * Inferred line
    """

    def __init__(self) -> None:
        self.init_val = None
        self._initial_state = True
        self._last_rule_progressed = False
        self.sudoku: list[NineSquare] = []
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
        # Run a quick check of the completed sudoku network from the cell perspective
        # if it fails it will trigger an exception, so the answer isn't really needed.
        # TODO this is wrong. it only runs network from 1 cell perspective. Also it means Sudoku has to understand
        # cell methods??
        _ = self.sudoku[0].cell(0, 0).connection_ok

    def load(self, init_val: SudokuValType):
        self.init_val = init_val

    def initialize(self) -> None:
        """Used to initialize state of the puzzle first time or to reset it for subsequent puzzles"""
        if not self.init_val:
            logger.warning("initialize called without an init being loaded. Do nothing")
        else:
            for i in range(9):
                self.sudoku[i].initialize(self.init_val[i])
            logger.info("Sudoku Class finished initialization")
        self._initial_state = True

    @property
    def solved(self) -> bool:
        all_solved = True
        for ns in self.sudoku:
            all_solved &= ns.solved
        return all_solved

    @property
    def last_rule_progressed(self) -> bool:
        return self._last_rule_progressed

    @property
    def initial_state(self) -> bool:
        """True if puzzle is still in the initial state and no rules run"""
        return self._initial_state

    @property
    def solutions(self) -> SudokuValType:
        sols = []
        for i in range(9):
            sols.append(self.sudoku[i].solutions)
        return tuple(sols)

    # TODO The following functions all do the same thing. Traverse the ninesquares calling this same function at that
    # level. There has to be a way to collapse into one. The problem being run_rule needs to call update_potentials
    # and consistency_check as a part of that algorithm. Needs some thought
    def check_consistency(self) -> bool:
        total_result = True
        for i in range(9):
            total_result &= self.sudoku[i].check_consistency()
        return total_result

    def update_all_potentials(self) -> bool:
        total_result = False
        for square in self.sudoku:
            total_result |= square.run_rule("update_potentials")
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        if not self.check_consistency():
            raise Exception("update_all_potentials failed check_consistency")
        return total_result

    def run_rule(self, rule: str) -> bool:
        """Wrapper to send the generic rule to each of the NineSquares"""
        logger.info("Sudoku Class starting rule %s", rule)
        self._initial_state = False
        total_result = False
        _ = self.update_all_potentials()  # Do this for all cells before any rule runs
        for square in self.sudoku:
            total_result |= square.run_rule(rule)
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        self._last_rule_progressed = total_result
        if not self.check_consistency():
            raise Exception("%s failed check_consistency", rule)
        return total_result
