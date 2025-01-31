import logging
import itertools
from typing import TypeAlias, Literal

logger = logging.getLogger(__name__)

## Define some types
CellValType: TypeAlias = int | None
NineSquareValType: TypeAlias = tuple[CellValType, ...]
SudokuValType: TypeAlias = tuple[NineSquareValType, ...]
DirectionType: TypeAlias = Literal["row", "col", "square"]


# TODO:
# *  Publish as an executable to windows
# *  Publish to linux and mac?

## Constant Defines
CSPACES = ("row", "col", "square")
SUD_SPACE_SIZE = 9
SUD_VAL_START = 1
SUD_VAL_END = SUD_SPACE_SIZE
SUD_RANGE = range(SUD_VAL_START, SUD_SPACE_SIZE + SUD_VAL_START)


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
        self._check_cell_param_is_legal(initial)
        self._solved_value: CellValType = None
        self._new_solution: bool = False
        self._potentials: set[int] = set(SUD_RANGE)
        self._eliminated = set()
        self._next: dict[DirectionType, Cell | None] = dict.fromkeys(CSPACES)
        self.rules = {
            "update_potentials": self._update_potentials,
            "eliminate_visible": self._rule_elimination,
            "elimination_to_one": self._rule_elimination_to_one,
            "single_possible_location": self._rule_single_possible_location,
            "matched_pairs": self._rule_matched_pairs,
        }
        self.initialize(initial)

    def _check_cell_param_is_legal(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None
        val is either a single int or a set of ints"""
        if val is not None:
            if type(val) is not int:
                raise ValueError
            if val < SUD_VAL_START or val > SUD_VAL_END:
                raise ValueError
        logger.debug("Cell Value for cell id %d is legal", self.id)

    def _check_network_connectivity(self) -> bool:
        """Check to make sure everything is connected properly for this cell; make sure no endless loops
        on network traversals."""
        # Iterate over row, col and square.
        for direction in CSPACES:
            cell = self
            count = 0
            while True:
                cell = cell.traverse(direction)
                count += 1
                ## Error condition, should never be more than 9 cells in a loop
                if count > SUD_SPACE_SIZE:
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
        return self._check_network_connectivity()

    @property
    def solved(self) -> bool:
        return self.solution is not None

    @property
    def new_solution(self) -> bool:
        return self._new_solution

    def clear_new_solution(self) -> None:
        self._new_solution = False

    def connect(self, direction: DirectionType, cell: "Cell") -> None:
        self._next[direction] = cell

    def traverse(self, direction: DirectionType) -> "Cell":
        if self._next[direction] is None:
            raise Exception("Cell network is not set up correctly")
        return self._next[direction]  # type: ignore

    @property
    def solution(self) -> CellValType:
        return self._solved_value

    @property
    def initial(self) -> CellValType:
        return self._initial_value

    @property
    def potentials(self) -> set[int]:
        return self._potentials

    @property
    def eliminated(self) -> set[int]:
        return self._eliminated

    def clear_potentials(self) -> None:
        self._potentials.clear()

    def clear_eliminated(self) -> None:
        self._eliminated.clear()

    def add_potential(self, val: int) -> None:
        self._check_cell_param_is_legal(val)
        self._potentials.add(val)

    def remove_potential(self, val: int) -> bool:
        self._check_cell_param_is_legal(val)
        if val in self._potentials:
            self._potentials.remove(val)
            self._eliminated.add(val)
            return True
        else:
            return False

    def check_consistency(self) -> bool:
        """Check that current solution state is legal. Used to catch any logic problems early, shouldn't find them
        if there are no errors"""

        for direction in CSPACES:
            solution_count = dict.fromkeys(SUD_RANGE, 0)
            cell = self
            while True:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if cell.solution:
                    solution_count[cell.solution] += 1
                cell = cell.traverse(direction)
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
        for direction in CSPACES:
            cell = self.traverse(direction)
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                _ = cell.remove_potential(val)
                cell = cell.traverse(direction)

    def initialize(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        logger.debug("Init is called for Cell %d", self.id)
        self._check_cell_param_is_legal(val)
        if val is not None:
            self._initial_value = val
            # Can't  just call _set_solution here as network isn't guarenteed to be set up yet
            self._solved_value = val
            self.clear_potentials()
        else:
            self._initial_value = None
            self._solved_value = None
            self._potentials = set(SUD_RANGE)
        self.clear_eliminated()
        self.clear_new_solution()

    def _update_potentials(self) -> bool:
        """Loop through all cstates and remove potentials from the list for any present
        This is the first step before any rule, so making this a seperate function so it can be called by each
        rule"""

        potential_starting_len = len(self.potentials)
        for direction in CSPACES:
            cell = self.traverse(direction)
            while cell != self:
                if cell.solution:
                    _ = self.remove_potential(cell.solution)
                cell = cell.traverse(direction)

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

    def _gather_multiples(self, mode: int, direction: DirectionType) -> set[int]:
        """Traverse the space looking for mode number of occurences in potentials i.e. singles, pairs, triplets etc
        Returns a set of those potentials"""
        pot_count = dict.fromkeys(SUD_RANGE, 0)
        pot_list = set()
        cell = self
        while True:
            for num in cell.potentials:
                pot_count[num] += 1
            cell = cell.traverse(direction)
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

    def _rule_elimination(self) -> bool:
        """Eliminate all solutions seen in constrained spaces. This step is run for every rule, but in this case
        just run the elimination step"""
        progress = False
        return progress

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
        for direction in CSPACES:
            singles_set = self._gather_multiples(1, direction)
            # Now see if any of our cell potentials is in the list, if so set it as the solution
            for num in self.potentials:
                if num in singles_set:
                    self._set_solution(num)
                    return True  # short circuit if solution found
        return False

    def _rule_matched_pairs(self) -> bool:
        total_return = False

        for direction in CSPACES:
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
                        cell = cell.traverse(direction)
                        if cell == self:
                            break
                    if len(matching_cells) == subset_num_pairs:
                        # We have found a set of matched pairs, now go through each cell and eliminate any potential
                        # that is not part of the matched pair combination
                        for c in matching_cells:
                            current_pots = c.potentials.copy()
                            for p in current_pots:
                                if p not in combo:
                                    _ = c.remove_potential(p)
                                    # success! we actually removed a potential
                                    total_return |= True
        return total_return


class SubLine:
    """Represents the 3 squares overlapping between a square's row or column and the full row or column
    The concept of a sub row or sub col is useful in solving the aligned potentials rule.
    A subline also has a list of the non overlapping cells in both the square and the line.
    Given a base cell and a direction, the constructor will traverse the cell network and build a list of :
    subrow, non-matching squares, non-matching row/col


    """

    def __init__(self, base: Cell, direction: str) -> None:
        self.overlap = []
        self.sq_non_over_lap = []
        self.ln_non_over_lap = []

        next = base
        if direction == "row":
            sq_next = base
            # Build list of overlap by grabbing first 3 of the row
            for _ in range(3):
                self.overlap.append(next)
                sq_next = next.traverse("square")  # find tail of the first row
                next = next.traverse("row")
            # Next 6 in the row are the non-overlap
            for _ in range(6):
                self.ln_non_over_lap.append(next)
                next = next.traverse("row")
            # Next 6 of the circular NineSquare space is the non-overlap
            for _ in range(6):
                self.sq_non_over_lap.append(sq_next)
                sq_next = sq_next.traverse("square")
        else:
            if direction != "col":
                raise ValueError
            # Column case
            for _ in range(3):
                self.overlap.append(next)
                next = next.traverse("col")
            # Next 6 in the col are the non-overlap
            for _ in range(6):
                self.ln_non_over_lap.append(next)
                next = next.traverse("col")
            next = base
            for _ in range(SUD_SPACE_SIZE):
                if next not in self.overlap:
                    self.sq_non_over_lap.append(next)
                next = next.traverse("square")

    def aligned_potentials(self) -> bool:
        progress = False
        # Gather up all of the possible potentials
        pot_count = dict.fromkeys(SUD_RANGE, 0)
        for cell in self.overlap:
            if cell.solved:
                continue
            for num in cell.potentials:
                pot_count[num] += 1
        # See which have more than 1
        for p, cnt in pot_count.items():
            if cnt > 1:
                # Check if potential exists in non-overlap square
                found_in_non_ov_square = False
                for cell in self.sq_non_over_lap:
                    if p in cell.potentials:
                        found_in_non_ov_square = True
                if not found_in_non_ov_square:
                    # This is the aligned case
                    for cell in self.ln_non_over_lap:
                        progress = progress | cell.remove_potential(p)
                else:
                    found_in_non_ov_line = False
                    for cell in self.ln_non_over_lap:
                        if p in cell.potentials:
                            found_in_non_ov_line = True
                    if not found_in_non_ov_line:
                        for cell in self.sq_non_over_lap:
                            progress = progress | cell.remove_potential(p)
        return progress


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
        self.rules = {
            "aligned_potentials": self._rule_aligned_potentials,
        }
        self.cells: list[Cell] = []  # A list of cells to represent a NineSquare
        # Instantiate Cells
        for i in range(SUD_SPACE_SIZE):
            self.cells.append(Cell(self.id * SUD_SPACE_SIZE + i))
        # Connect up rows of the NineSquare
        for i in (0, 3, 6):
            self.cells[i].connect("row", self.cells[i + 1])
            self.cells[i + 1].connect("row", self.cells[i + 2])
        # Connect up columns of the NineSquare
        for i in range(3):
            self.cells[i].connect("col", self.cells[i + 3])
            self.cells[i + 3].connect("col", self.cells[i + 6])
        # Connect up the NineSquare Loop
        for i in range(8):
            self.cells[i].connect("square", self.cells[i + 1])
        self.cells[8].connect("square", self.cells[0])

    def connect_sublines(self):
        self.sublines = []
        for i, cell in enumerate(self.cells):
            if i == 0:
                self.sublines.append(SubLine(cell, "row"))
                self.sublines.append(SubLine(cell, "col"))
            if i == 1:
                self.sublines.append(SubLine(cell, "col"))
            if i == 2:
                self.sublines.append(SubLine(cell, "col"))
            if i == 3:
                self.sublines.append(SubLine(cell, "row"))
            if i == 6:
                self.sublines.append(SubLine(cell, "row"))

    def initialize(self, vals: NineSquareValType) -> None:
        for i in range(SUD_SPACE_SIZE):
            self.cells[i].initialize(vals[i])

    @property
    def solved(self) -> bool:
        all_solved = True
        for cell in self.cells:
            all_solved &= cell.solved
        return all_solved

    @property
    def solutions(self) -> NineSquareValType:
        sols = []
        for i in range(SUD_SPACE_SIZE):
            sols.append(self.cells[i].solution)
        return tuple(sols)

    def cell(self, row: int, col: int) -> Cell:
        """returns a cell pases on row and column coordinates"""
        i = row * 3 + col
        return self.cells[i]

    def attach_row(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another to the right"""
        self.cells[2].connect("row", other.cell(0, 0))
        self.cells[5].connect("row", other.cell(1, 0))
        self.cells[8].connect("row", other.cell(2, 0))

    def attach_col(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another below"""
        self.cells[6].connect("col", other.cell(0, 0))
        self.cells[7].connect("col", other.cell(0, 1))
        self.cells[8].connect("col", other.cell(0, 2))

    def check_consistency(self) -> bool:
        total_result = True
        for i in range(SUD_SPACE_SIZE):
            total_result &= self.cells[i].check_consistency()
        return total_result

    def run_rule(self, rule: str) -> bool:
        """Wrapper to send the generic rule to each of the cells"""
        logger.info("NineSquare %d starting rule %s", self.id, rule)
        total_result = False
        if rule in self.rules.keys():
            # NineSquare level rule
            total_result = self.rules[rule]()
        else:
            # Cell level rule
            for i in range(SUD_SPACE_SIZE):
                total_result |= self.cells[i].run_rule(rule)
        logger.debug(
            "NineSquare %d completing %s, result is %d",
            self.id,
            rule,
            total_result,
        )
        return total_result

    def _rule_aligned_potentials(self):
        progress = False
        for subline in self.sublines:
            progress = progress | subline.aligned_potentials()
        return progress


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
        self.history = History()
        self.ns: list[NineSquare] = []
        for i in range(SUD_SPACE_SIZE):
            self.ns.append(NineSquare(i))
        # Connect up the rows
        for i in (0, 3, 6):
            self.ns[i].attach_row(self.ns[i + 1])
            self.ns[i + 1].attach_row(self.ns[i + 2])
            self.ns[i + 2].attach_row(self.ns[i])
        # Connect up the columns
        for i in range(3):
            self.ns[i].attach_col(self.ns[i + 3])
            self.ns[i + 3].attach_col(self.ns[i + 6])
            self.ns[i + 6].attach_col(self.ns[i])
        # Run a quick check of the completed sudoku network from the cell perspective
        # if it fails it will trigger an exception, so the answer isn't really needed.
        # TODO this is wrong. it only runs network from 1 cell perspective. Also it means Sudoku has to understand
        # cell methods??
        _ = self.ns[0].cell(0, 0).connection_ok
        for n in self.ns:
            n.connect_sublines()

    def load(self, init_val: SudokuValType):
        self.init_val = init_val

    def initialize(self, history_mode=False) -> None:
        """Used to initialize state of the puzzle first time or to reset it for subsequent puzzles"""
        if not self.init_val:
            logger.warning("initialize called without an init being loaded. Do nothing")
        else:
            if not history_mode:
                self.history.clear()
            for i in range(SUD_SPACE_SIZE):
                self.ns[i].initialize(self.init_val[i])
            logger.info("Sudoku Class finished initialization")
        self._initial_state = True

    @property
    def solved(self) -> bool:
        all_solved = True
        for ns in self.ns:
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
        for i in range(SUD_SPACE_SIZE):
            sols.append(self.ns[i].solutions)
        return tuple(sols)

    # TODO The following functions all do the same thing. Traverse the ninesquares calling this same function at that
    # level. There has to be a way to collapse into one. The problem being run_rule needs to call update_potentials
    # and consistency_check as a part of that algorithm. Needs some thought
    def check_consistency(self) -> bool:
        total_result = True
        for i in range(SUD_SPACE_SIZE):
            total_result &= self.ns[i].check_consistency()
        return total_result

    def update_all_potentials(self) -> bool:
        total_result = False
        for square in self.ns:
            total_result |= square.run_rule("update_potentials")
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        if not self.check_consistency():
            raise Exception("update_all_potentials failed check_consistency")
        return total_result

    def run_rule(self, rule: str, history_mode=False) -> bool:
        """Wrapper to send the generic rule to each of the NineSquares"""
        logger.info("Sudoku Class starting rule %s", rule)
        self._initial_state = False
        total_result = False
        # Need to clear this out here because want to capture the elimination from both the potential update
        # and the rule which gets run
        for s in self.ns:
            for c in s.cells:
                c.clear_eliminated()
        if not history_mode:
            self.history.push_rule(rule)
        _ = self.update_all_potentials()  # Do this for all cells before any rule runs
        for square in self.ns:
            total_result |= square.run_rule(rule)
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        self._last_rule_progressed = total_result
        if not self.check_consistency():
            raise Exception("%s failed check_consistency", rule)
        return total_result

    def replay_history(self, direction: str) -> bool:
        if direction == "back":
            if self.history.at_beginning:
                # Already at earliest point, do nothing
                pass
            else:
                self.history.back()
        elif direction == "forward":
            if self.history.at_end:
                # Already at latest point, do nothing
                pass
            else:
                self.history.forward()
        else:
            raise Exception("Invalid Argument")
        self.initialize(history_mode=True)
        progress = False
        i = 0
        while i <= self.history.curr_ptr:
            progress = self.run_rule(self.history.rule_queue[i], history_mode=True)
            i += 1
        return progress

    def delete_current_history_event(self) -> bool:
        if self.history.at_beginning:
            # Already at earliest point, do nothing
            pass
        self.history.delete_current()
        return self.replay_history("back")


class History:
    def __init__(self) -> None:
        self.rule_queue = []
        self.tail_ptr = -1
        self.curr_ptr = -1

    def push_rule(self, rule: str) -> None:
        self.rule_queue.insert(self.curr_ptr + 1, rule)
        self.tail_ptr += 1
        self.curr_ptr += 1

    def clear(self) -> None:
        self.rule_queue = []
        self.tail_ptr = self.curr_ptr = -1

    def back(self) -> None:
        self.curr_ptr -= 1

    def forward(self) -> None:
        self.curr_ptr += 1

    def delete_current(self) -> None:
        self.rule_queue.pop(self.curr_ptr)
        self.tail_ptr -= 1

    def print_out(self) -> list[str]:
        out = []
        for i, rule in enumerate(self.rule_queue):
            curr_prefix = "c-> " if self.curr_ptr == i else "    "
            out.insert(i, curr_prefix + rule)
        return out

    @property
    def at_end(self) -> bool:
        return self.tail_ptr == self.curr_ptr

    @property
    def at_beginning(self) -> bool:
        return self.curr_ptr == -1

    @property
    def init_val(self) -> SudokuValType:
        return self._init

    @init_val.setter
    def init_val(self, val: SudokuValType) -> None:
        self._init = val
