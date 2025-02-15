import logging
from typing import cast
from sudoku.cellnetwork import CellNetwork
from sudoku.defines import (
    CellValType,
    SUD_RANGE,
    CSPACES,
    SUD_VAL_START,
    SUD_VAL_END,
)
from sudoku.generic_structure import GenericStructure

logger = logging.getLogger(__name__)


class Cell(GenericStructure):
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
        self, id: int, network: CellNetwork, initial: CellValType = None
    ) -> None:
        # TODO can't we just call intialize and get rid of all this stuff?
        self._check_cell_param_is_legal(initial)
        self.id: int = id
        self.network = network
        self.network.home_node(self)
        self._solved_value: CellValType = None
        self._new_solution: bool = False
        self._speculative_solution: bool = False
        self._error: bool = False
        self._potentials: set[int] = set(SUD_RANGE)
        self._eliminated = set()
        self.initialize(initial)

    def initialize(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None"""
        logger.debug("Init is called for Cell %d", self.id)
        self._check_cell_param_is_legal(val)
        self._speculative_solution = False
        self._error = False
        if val is not None:
            self._initial_value = val
            # Can't  just call set_solution here as network isn't guarenteed to be set up yet
            self._solved_value = val
            self.clear_potentials()
        else:
            self._initial_value = None
            self._solved_value = None
            self._potentials = set(SUD_RANGE)
        self.clear_eliminated()
        self.clear_new_solution()

    def _check_cell_param_is_legal(self, val: CellValType) -> None:
        """cell can be initialized to a digit 1 - 9 or to None
        val is either a single int or a set of ints"""
        if val is not None:
            if type(val) is not int:
                raise ValueError
            if val < SUD_VAL_START or val > SUD_VAL_END:
                logger.debug("Cell Value %d for cell id %d is illegal", val, self.id)
                raise ValueError

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

    @speculative_solution.setter
    def speculative_solution(self, val):
        self._speculative_solution = True
        self.set_solution(val)

    def clear_new_solution(self) -> None:
        self._new_solution = False

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

        all_is_good = True
        for direction in CSPACES:
            solution_set = dict.fromkeys(SUD_RANGE, None)
            cell = self
            while True:
                if cell is None:
                    raise Exception("Cell network is not set up correctly")
                if cell.solution:
                    if solution_set[cell.solution]:
                        cell._error = True
                        solution_set[cell.solution]._error = True
                        logger.error(
                            "Found more than one solution for solution %d in in direction %s cell %d",
                            cell.solution,
                            direction,
                            self.id,
                        )
                        all_is_good = False
                    else:
                        solution_set[cell.solution] = cell
                cell = cast(Cell, cell.network.traverse(direction))
                if cell == self:
                    break
        return all_is_good

    def set_solution(self, val: int) -> None:
        """Set the solution field. Clear the potentials field. Go through all visible c-spaces and remove solved value from their potentials"""
        self._check_cell_param_is_legal(val)
        self._solved_value = val
        self._new_solution = True
        self.clear_potentials()
        self.check_consistency()  # TODO if this is done here, can I remove other calls?
        logger.info("Cell %d: Solution found: %d", self.id, self._solved_value)

    def remove_potential_in_cspaces(self, val: int) -> None:
        for direction in CSPACES:
            for cell in self.network.clist[direction]:
                if not cell.solved:
                    _ = cell.remove_potential(val)
                    # If all potentials are gone something is wrong mark the cell in error
                    if not cell.potentials:
                        cell._error = True
