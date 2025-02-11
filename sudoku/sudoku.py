import logging
from sudoku.history import History
from sudoku.ninesquare import NineSquare
from sudoku.defines import SudokuValType, SUD_SPACE_SIZE

logger = logging.getLogger(__name__)

# TODO:
# *  Publish as an executable to windows
# *  Publish to linux and mac?


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
            self.ns.append(NineSquare(i, self.history))
        self._connect_ninesquare_network()

    def _connect_ninesquare_network(self):
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
            n.create_sublines()

    # TODO The following functions all do the same thing. Traverse the ninesquares calling this same function at that
    # level. There has to be a way to collapse into one. The problem being run_rule needs to call update_potentials
    # and consistency_check as a part of that algorithm. Needs some thought
    def check_consistency(self) -> bool:
        return True
        total_result = True
        for i in range(SUD_SPACE_SIZE):
            total_result &= self.ns[i].check_consistency()
        return total_result

    def _update_all_potentials(self) -> bool:
        total_result = False
        for square in self.ns:
            total_result |= square.run_rule("update_potentials")
        logger.info(
            "Sudoku Class finishing elimination_to_one result is %d", total_result
        )
        if not self.check_consistency():
            raise Exception("update_all_potentials failed check_consistency")
        return total_result

    ## Public API
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
        _ = self._update_all_potentials()  # Do this for all cells before any rule runs
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
            self.history.back()
        elif direction == "forward":
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

    def prune_history_to_end(self) -> None:
        self.history.prune()

    def delete_current_history_event(self) -> bool:
        self.history.delete_current()
        return self.replay_history("back")

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

