from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from gui.fixed_size_control import FixedSizeControl
from gui.history_docker import RightDocker
from gui.sudoku_game_views import SudokuView
from sudoku import Sudoku, SudokuValType


# TODO:
# * Create a log with sudsovler.py
# * code remaining rules
# * scripting language to save order of button pushes (stretch)
# * puzzle editing mode instead of having to edit the yaml file directly (stretch)
# * Keep a list of button pushes. Have a back and foward button which will replay. Could save solutions off to file
# as well, like the scripting language item above?


class SSolveMain(QMainWindow):
    def __init__(
        self,
        app: QApplication,
        sizer: FixedSizeControl,
        sudoku: Sudoku,
        puzzles_dict: dict[str, SudokuValType],
    ) -> None:
        super().__init__()

        self.app = app
        self.sudoku = sudoku
        # Determine available screen size so we can make the sudoku app fit
        self.sizer = sizer

        # Primary Components of Main Window
        self.puzzle_widget = SudokuView(sudoku)
        self.right_docker = RightDocker(sudoku, sizer, self.update_gui)
        self.control_widget = ControlsView(
            sudoku, self, app, puzzles_dict, sizer, self.update_gui
        )

        self._define_layout()
        self._configure_mainwindow()
        self._define_shortcuts()

    def _define_layout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.puzzle_widget)
        main_layout.addWidget(self.control_widget)
        main_widget = QWidget()
        main_widget.setFixedWidth(self.sizer.app_width)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_docker)

    def _configure_mainwindow(self) -> None:
        self.setWindowTitle("Kurt's Suduko Logical Rule Solver")

    def _define_shortcuts(self) -> None:
        shortcut_quit = QShortcut(QKeySequence("q"), self)
        shortcut_quit.activated.connect(self.app.quit)
        shortcut_exit = QShortcut(QKeySequence("x"), self)
        shortcut_exit.activated.connect(self.app.quit)
        shortcut_restart = QShortcut(QKeySequence("r"), self)
        shortcut_restart.activated.connect(self.control_widget.initialize)
        shortcut_eto = QShortcut(QKeySequence("1"), self)
        shortcut_eto.activated.connect(
            lambda: self.control_widget.run_rule("elimination_to_one")
        )
        shortcut_spl = QShortcut(QKeySequence("2"), self)
        shortcut_spl.activated.connect(
            lambda: self.control_widget.run_rule("single_possible_location")
        )
        shortcut_spl = QShortcut(QKeySequence("4"), self)
        shortcut_spl.activated.connect(
            lambda: self.control_widget.run_rule("matched_pairs")
        )
        shortcut_hist_show = QShortcut(QKeySequence("d"), self)
        shortcut_hist_show.activated.connect(self.right_docker.toggle)

        shortcut_hist_forward = QShortcut(QKeySequence("l"), self)
        shortcut_hist_forward.activated.connect(
            self.right_docker.history_widget.forward
        )
        shortcut_hist_back = QShortcut(QKeySequence("h"), self)
        shortcut_hist_back.activated.connect(self.right_docker.history_widget.back)

    def update_gui(self) -> None:
        """The gui gets updated explicitly. This is the function that updates the entire gui. It should be called
        after anything that updates state such as a rule button press or loading a new puzzle"""
        self.puzzle_widget.update_sudoku()
        self.control_widget.update_controls()


class ControlsView(QWidget):
    # Below is original hard coded values.
    # control_height = 50
    # control_width = 130
    # rule_width = 200

    status_normal_style = "font-size: 16pt;"
    status_success_style = "color: green; font-size: 16pt;"

    def __init__(
        self,
        sudoku: Sudoku,
        mainwindow: SSolveMain,
        app: QApplication,
        puzzles_dict: dict[str, SudokuValType],
        sizer: FixedSizeControl,
        update_gui,
    ) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.main = mainwindow
        self.update_gui = update_gui
        self.app = app
        self.puzzles_dict = puzzles_dict
        self.control_height = sizer.app_width / 30
        self.control_width = sizer.app_width / 12
        self.rule_width = int(sizer.app_width / 7)

        # Create the Control and Rule Buttons
        self.controls = {
            "new_puzzle": QComboBox(),
            "start": QPushButton("Re-Start (r)"),
            "close": QPushButton("Exit (q)"),
            "history": QPushButton("History (d)"),
        }
        self.controls["new_puzzle"].setPlaceholderText("Choose a Puzzle")
        self.controls["new_puzzle"].addItems(puzzles_dict.keys())
        # Size the buttons
        for contr in self.controls:
            self.controls[contr].setFixedSize(self.control_width, self.control_height)
        self.rules = {
            "elimination": QPushButton("Eliminate Visible(0)"),
            "eto_rule": QPushButton("Elimination to One (1)"),
            "spl_rule": QPushButton("Single Possible Location (2)"),
            "aligned_rule": QPushButton("Aligned Potentials (3)"),
            "matched_pairs": QPushButton("Matched Pairs (4)"),
            "matched_triplets": QPushButton("Matched Triplets (5)"),
        }
        # Size the buttons
        for it in self.rules:
            self.rules[it].setFixedWidth(self.rule_width)

        # Header and Control Labels
        header_label = QLabel("Logic Solution Rules")
        header_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        control_label = QLabel("Controls")
        control_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        control_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_label = QLabel()
        self.status_label.setStyleSheet(self.status_normal_style)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Layout Formatting
        layout_rules = QHBoxLayout()
        for i, rl in enumerate(self.rules.values()):
            layout_rules.addWidget(rl, i)
        layout_controls = QHBoxLayout()
        for i, ct in enumerate(self.controls.values()):
            layout_controls.addWidget(ct, i)
        layout_controls.addWidget(self.status_label, len(self.controls.values()) + 1)
        layout = QVBoxLayout()
        layout.addWidget(HLine())
        layout.addWidget(header_label)
        layout.addLayout(layout_rules)
        layout.addWidget(HLine())
        # layout.addWidget(control_label)
        layout.addLayout(layout_controls)
        self.setLayout(layout)

        ## Connect Up Controls and Rules Buttons
        self.controls["close"].clicked.connect(self.app.quit)
        self.controls["start"].clicked.connect(self.initialize)
        self.controls["new_puzzle"].textActivated.connect(self.load_puzzle)
        self.controls["history"].clicked.connect(self.main.right_docker.toggle)
        self.rules["elimination"].clicked.connect(
            lambda: self.run_rule("eliminate_visible")
        )
        self.rules["eto_rule"].clicked.connect(
            lambda: self.run_rule("elimination_to_one")
        )
        self.rules["spl_rule"].clicked.connect(
            lambda: self.run_rule("single_possible_location")
        )
        self.rules["matched_pairs"].clicked.connect(
            lambda: self.run_rule("matched_pairs")
        )
        self.rules["aligned_rule"].clicked.connect(
            lambda: self.run_rule("aligned_potentials")
        )

    def update_controls(self) -> None:
        if self.sudoku.initial_state:
            status = "Initial"
        elif self.sudoku.solved:
            status = "Solved"
        elif self.sudoku.last_rule_progressed:
            status = "Progress"
        else:
            status = "No Progress"
        self.status_label.setText(status)
        # Make text green for Solved state
        if status == "Solved":
            self.status_label.setStyleSheet(self.status_success_style)
        else:
            self.status_label.setStyleSheet(self.status_normal_style)

    def initialize(self) -> None:
        self.sudoku.initialize()
        self.update_gui()

    def load_puzzle(self, t: str) -> None:
        self.sudoku.load(self.puzzles_dict[t])
        self.sudoku.initialize()
        self.update_gui()

    def run_rule(self, rule: str) -> None:
        self.sudoku.run_rule(rule)
        self.update_gui()


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
