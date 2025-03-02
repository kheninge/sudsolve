import logging
from sudoku.history import History
from sudoku.ninesquare import NineSquare
from sudoku.defines import PuzzleFormat, SUD_SPACE_SIZE
from sudoku.puzzleio import convert_to_ns_format
from sudoku.ruleengine import RuleEngine
from sudoku.rules import EliminationRule, SudokuRule

logger = logging.getLogger(__name__)


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
        self._initial_state = True
        self._last_rule_progressed = False
        self.history = History()
        self.ns: list[NineSquare] = [NineSquare(i) for i in range(SUD_SPACE_SIZE)]
        self.cells = []
        self.sublines = []
        self.puzzle = None
        for n in self.ns:
            for c in n.cells:
                self.cells.append(c)
        self._connect_ninesquare_network()
        for n in self.ns:
            for s in n.sublines:
                self.sublines.append(s)
        self.rule_engine: RuleEngine = RuleEngine(self.cells, self.sublines)

    def _connect_ninesquare_network(self):
        # Connect up the rows
        for row_start in (0, 3, 6):
            self.ns[row_start].attach_row(self.ns[row_start + 1])
            self.ns[row_start + 1].attach_row(self.ns[row_start + 2])
            self.ns[row_start + 2].attach_row(self.ns[row_start])  # circular
        # Connect up the columns
        for col_start in range(3):
            self.ns[col_start].attach_col(self.ns[col_start + 3])
            self.ns[col_start + 3].attach_col(self.ns[col_start + 6])
            self.ns[col_start + 6].attach_col(self.ns[col_start])  # circular
        # Signal completion of the network to the cells
        for c in self.cells:
            c.network.completed_connection()
        # Run a quick check of the completed sudoku network from the cell perspective
        # if it fails it will trigger an exception, so the answer isn't really needed.
        # TODO this is wrong. it only runs network from 1 cell perspective. Also it means Sudoku has to understand
        # cell methods??
        _ = self.ns[0].cell(0, 0).network.connection_ok
        for n in self.ns:
            n.create_sublines()

    def _update_all_potentials(self) -> bool:
        total_result = self.rule_engine.execute(EliminationRule("all"))
        return total_result

    ## Public API
    def load(self, puzzle: PuzzleFormat):
        """puzzle given in PuzzleFormat format."""
        self.puzzle = puzzle

    def load_sud(self, puzzle: str):
        """puzzle given in sudoku format i.e. like the yaml file."""
        self.load(convert_to_ns_format(puzzle))

    def initialize(self, history_mode=False) -> None:
        """Used to initialize state of the puzzle first time or to reset it for subsequent puzzles"""
        if not self.puzzle:
            logger.info("initialize called without an init being loaded. Do nothing")
        else:
            if not history_mode:
                self.history.clear()
            for i in range(SUD_SPACE_SIZE):
                self.ns[i].initialize(self.puzzle[i])
            logger.info("Sudoku Class finished initialization")
        self._initial_state = True

    def run_rule(self, rule: SudokuRule, history_mode=False) -> bool:
        """Wrapper to send the generic rule to each of the NineSquares"""
        logger.info("Sudoku Class starting rule %s", rule)
        self._initial_state = False
        # Need to clear this out here because want to capture the elimination from both the potential update
        # and the rule which gets run
        for c in self.cells:
            c.clear_eliminated()
            c.clear_new_solution()
        if not history_mode:
            self.history.push_rule(rule)
        _ = self._update_all_potentials()  # Do this for all cells before any rule runs
        total_result = self.rule_engine.execute(rule)
        self._last_rule_progressed = total_result
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

    # This is only used by the tests. The gui gets solutions directly from cell
    @property
    def _solutions(self) -> PuzzleFormat:
        sols = []
        for i in range(SUD_SPACE_SIZE):
            sols.append(self.ns[i].solutions)
        return tuple(sols)
