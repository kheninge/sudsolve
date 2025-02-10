import logging
from sudoku.defines import (
    CellValType,
    DirectionType,
    SUD_RANGE,
    CSPACES,
    SUD_VAL_START,
    SUD_VAL_END,
    SUD_SPACE_SIZE,
)
from sudoku.history import History
import itertools
import re

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
    run_rule(rule) - Takes these
    *"""

    def __init__(
        self, id: int = 0, history: History = None, initial: CellValType = None
    ) -> None:
        self.id: int = id
        self.history = history
        self._check_cell_param_is_legal(initial)
        self._solved_value: CellValType = None
        self._new_solution: bool = False
        self._speculative_solution: bool = False
        self._error: bool = False
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
    def in_error(self) -> bool:
        return self._error

    @property
    def new_solution(self) -> bool:
        return self._new_solution

    @property
    def speculative_solution(self) -> bool:
        return self._speculative_solution

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

    def set_speculative_solution(self, val: int, history_mode: bool) -> None:
        self._speculative_solution = True
        self._set_solution(val)
        if not history_mode:
            self.history.push_rule(f"speculative_solution:{self.id}:{val}")

    def _set_solution(self, val: int) -> None:
        """Set the solution field. Clear the potentials field. Go through all visible c-spaces and remove solved value from their potentials"""
        self._solved_value = val
        self._new_solution = True
        self.clear_potentials()
        logger.info("Cell %d: Solution found: %d", self.id, self._solved_value)

    def _remove_potential_in_cspaces(self, val: int) -> None:
        for direction in CSPACES:
            cell = self.traverse(direction)
            while cell != self:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if not cell.solved:
                    _ = cell.remove_potential(val)
                    # If all potentials are gone something is wrong mark the cell in error
                    if not cell.potentials:
                        cell._error = True
                cell = cell.traverse(direction)

    def initialize(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        logger.debug("Init is called for Cell %d", self.id)
        self._check_cell_param_is_legal(val)
        self._speculative_solution = False
        self._error = False
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
            # If all potentials are gone something is wrong mark the cell in error
            if not self.potentials:
                self._error = True
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
        # Special case - speculative_solution, not really a rule
        if "speculative_solution" in rule:
            return self._replay_speculative_solution(rule)
        self.clear_new_solution()
        if rule not in self.rules.keys():
            logger.error("In run_rule, %s rule is called but not defined", rule)
            raise Exception("Undefine rule called")

        if self.solution:
            # Already solved
            return False

        # TODO is this needed other than the first time? Since the rules themselves update potentials whenever a
        # solution is found?
        _ = self._update_potentials()
        return self.rules[rule]()

    def _replay_speculative_solution(self, rule) -> bool:
        match = re.search(r"speculative_solution:(\d+):(\d+)", rule)
        if match:
            id = int(match.group(1))
            val = int(match.group(2))
        else:
            raise Exception("specultive solution replay error")
        if self.id == id:
            self.set_speculative_solution(val, history_mode=True)
            return True
        else:
            return False

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
            self._remove_potential_in_cspaces(mysolution)
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
                    self._remove_potential_in_cspaces(num)
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
