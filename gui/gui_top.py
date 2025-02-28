from PySide6.QtWidgets import (
    QApplication,
)
from PySide6.QtGui import QShortcut, QKeySequence
from gui.fixed_size_control import FixedSizeControl
from gui.history_docker import RightDocker
from gui.controls_view import ControlsView
from gui.sudoku_game_views import SudokuView
from sudoku.sudoku import Sudoku
from sudoku.puzzleio import PuzzleList
import sudoku.rules
from gui.update_controller import UpdateController

from gui.main_view import SSolveMain

TITLE = "Sudoku Assistant"
WIDTH_RATIO = 0.45


class GuiTop:
    """Instantiates all of the gui objects. Configures the gui. Binding between gui and controller"""

    def __init__(
        self,
        app: QApplication,
        sudoku: Sudoku,
        puzzles_list: PuzzleList,
    ) -> None:
        super().__init__()
        self.sudoku = sudoku
        self.puzzles_list = puzzles_list
        self.app = app
        self.sizes = FixedSizeControl(self.app, WIDTH_RATIO)
        self.updater = UpdateController()
        # Instantiate GUI Pieces
        self.puzzle_widget = SudokuView(self.sudoku, self.updater, self.sizes)
        self.right_docker = RightDocker(self.sudoku)
        self.control_widget = ControlsView(
            self.sudoku,
            self.puzzles_list,
            self.sizes,
            self.right_docker,
        )
        self.main_widget = SSolveMain(
            self.puzzle_widget,
            self.right_docker,
            self.control_widget,
            self.sizes,
        )

        self._create_control_bindings()
        self._define_shortcuts()
        self._connect_updates()
        self.main_widget.setWindowTitle(TITLE)
        self.main_widget.show()

    def _define_shortcuts(self):
        # Define Shortcuts
        shortcuts = {
            "q": self.app.quit,
            "x": self.app.quit,
            "r": self.initialize,
            "h": self.toggle_history_dock,
            "j": self.forward,
            "k": self.back,
            "p": self.prune,
            "d": self.delete,
            "0": lambda: self.run_rule("eliminate_visible"),
            "1": lambda: self.run_rule("elimination_to_one"),
            "2": lambda: self.run_rule("single_possible_location"),
            "3": lambda: self.run_rule("aligned_potentials"),
            "4": lambda: self.run_rule("filled_cells"),
            "5": lambda: self.run_rule("filled_potentials"),
        }
        for k, func in shortcuts.items():
            QShortcut(QKeySequence(k), self.main_widget).activated.connect(func)

    def _create_control_bindings(self):
        # Control Buttons
        self.control_widget.controls["close"].clicked.connect(self.app.quit)
        self.control_widget.controls["start"].clicked.connect(self.initialize)
        self.control_widget.controls["new_puzzle"].textActivated.connect(
            self.load_puzzle
        )
        self.control_widget.controls["history"].clicked.connect(
            self.toggle_history_dock
        )
        # Rules Buttons
        self.control_widget.rules["elimination"].clicked.connect(
            lambda: self.run_rule("eliminate_visible")
        )
        self.control_widget.rules["eto_rule"].clicked.connect(
            lambda: self.run_rule("elimination_to_one")
        )
        self.control_widget.rules["spl_rule"].clicked.connect(
            lambda: self.run_rule("single_possible_location")
        )
        self.control_widget.rules["filled_cells"].clicked.connect(
            lambda: self.run_rule("filled_cells")
        )
        self.control_widget.rules["filled_potentials"].clicked.connect(
            lambda: self.run_rule("filled_potentials")
        )
        self.control_widget.rules["aligned_rule"].clicked.connect(
            lambda: self.run_rule("aligned_potentials")
        )
        # History Docker
        self.right_docker.history_widget.right_button.clicked.connect(self.forward)
        self.right_docker.history_widget.left_button.clicked.connect(self.back)
        self.right_docker.history_widget.prune.clicked.connect(self.prune)
        self.right_docker.history_widget.delete.clicked.connect(self.delete)

    def _connect_updates(self):
        self.updater.updated.connect(self.control_widget.update_controls)
        self.updater.updated.connect(self.puzzle_widget.update_sudoku)
        self.updater.updated.connect(self.right_docker.history_widget.update_history)

    def initialize(self) -> None:
        self.sudoku.initialize()
        self.updater.updated.emit()

    def load_puzzle(self, t: str) -> None:
        self.sudoku.load_sud(self.puzzles_list.puzzles[t])
        self.sudoku.initialize()
        self.updater.updated.emit()

    def run_rule(self, rule: str) -> None:
        match rule:
            case "eliminate_visible":
                sudoku_rule = sudoku.rules.EliminationRule("all")
            case "elimination_to_one":
                sudoku_rule = sudoku.rules.EliminationToOneRule("all")
            case "single_possible_location":
                sudoku_rule = sudoku.rules.SinglePossibleLocationRule("all")
            case "filled_cells":
                sudoku_rule = sudoku.rules.FilledCellsRule("all")
            case "filled_potentials":
                sudoku_rule = sudoku.rules.FilledPotentialsRule("all")
            case "aligned_potentials":
                sudoku_rule = sudoku.rules.AlignedPotentialsRule("all")
            case _:
                raise Exception("Invalid Rule")
        self.sudoku.run_rule(sudoku_rule)
        self.updater.updated.emit()

    def back(self):
        self.sudoku.replay_history("back")
        self.updater.updated.emit()

    def forward(self):
        self.sudoku.replay_history("forward")
        self.updater.updated.emit()

    def prune(self):
        self.sudoku.prune_history_to_end()
        self.updater.updated.emit()

    def delete(self):
        self.sudoku.delete_current_history_event()
        self.updater.updated.emit()

    def start(self):
        self.app.exec()

    def toggle_history_dock(self):
        self.right_docker.toggle()
        self.main_widget.adjustSize()
