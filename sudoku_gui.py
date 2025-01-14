from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
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
from sudoku import NineSquareValType, Sudoku, SudokuValType, Cell


# TODO:
# * Create a log with sudsovler.py
# * Swap out a label with hints in the appropriate spots (3x3)
# * hot keys for the Buttons
# * code remaining rules
# * scripting language to save order of button pushes (stretch)
# * puzzle editing mode instead of having to edit the yaml file directly (stretch)
# * Keep a list of button pushes. Have a back and foward button which will replay. Could save solutions off to file
# as well, like the scripting language item above?


class SSolveMain(QMainWindow):
    def __init__(
        self, app: QApplication, sudoku: Sudoku, puzzles_dict: dict[str, SudokuValType]
    ) -> None:
        super().__init__()

        self.app = app
        self.sudoku = sudoku
        self._status: str | None = None
        self.puzzle_widget = SudokuView(sudoku)
        self.control_widget = ControlsView(sudoku, self, puzzles_dict)

        self.setWindowTitle("Kurt's Suduko Logical Rule Solver")

        # Main Window Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.puzzle_widget)
        main_layout.addWidget(self.control_widget)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Shortcut Definitions
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

    def update_gui(self) -> None:
        """The gui gets updated explicitly. This is the function that updates the entire gui. It should be called
        after anything that updates state such as a rule button press or loading a new puzzle"""
        self.puzzle_widget.update_sudoku()
        self.control_widget.update_controls()


class SudokuView(QWidget):
    def __init__(self, sudoku: Sudoku) -> None:
        super().__init__()
        self.sudoku = sudoku
        self.ns = []  # Keep a list of nine-squares

        # Suduko Grid Layout
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                widget = NineSquareView()
                self.ns.append(widget)
                layout.addWidget(widget, i, j)
        self.setLayout(layout)

    def update_sudoku(self) -> None:
        for i, ns in enumerate(self.ns):
            for j, cell in enumerate(ns.cells):
                cell.update_cell(self.sudoku.sudoku[i].ns[j])


class NineSquareView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                cell_widget = CellWidget()
                self.cells.append(cell_widget)
                layout.addWidget(cell_widget, i, j)
        self.setLayout(layout)


class CellWidget(QLabel):
    style_normal_background = " border: 1px solid black; font-size: 18pt;"
    style_yellow_background = (
        "background-color: yellow; border: 1px solid black; font-size: 18pt;"
    )

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(self.style_normal_background)
        self.setFixedSize(75, 75)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def update_cell(self, cell_model: Cell):
        if cell_model.solved:
            val = str(cell_model.solution)  # Labels take strings not int
        else:
            val = ""
        self.setText(val)
        if cell_model.new_solution:
            self.setStyleSheet(self.style_yellow_background)
        else:
            self.setStyleSheet(self.style_normal_background)


class ControlsView(QWidget):
    control_height = 50
    control_width = 130
    rule_width = 200

    status_normal_style = "font-size: 16pt;"
    status_success_style = "color: green; font-size: 16pt;"

    def __init__(
        self,
        sudoku: Sudoku,
        mainwindow: SSolveMain,
        puzzles_dict: dict[str, SudokuValType],
    ) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.main = mainwindow
        self.puzzles_dict = puzzles_dict

        # Create the Control and Rule Buttons
        self.controls = {
            "new_puzzle": QComboBox(),
            "start": QPushButton("Re-Start (r)"),
            "close": QPushButton("Exit (q)"),
        }
        self.controls["new_puzzle"].setPlaceholderText("Choose a Puzzle")
        self.controls["new_puzzle"].addItems(puzzles_dict.keys())
        # Size the buttons
        for foo in self.controls:
            self.controls[foo].setFixedSize(self.control_width, self.control_height)
        self.rules = {
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
        header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        control_label = QLabel("Controls")
        control_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        control_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.status_label = QLabel()
        self.status_label.setStyleSheet(self.status_normal_style)
        self.status_label.setAlignment(Qt.AlignHCenter)

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
        self.controls["close"].clicked.connect(self.main.app.quit)
        self.controls["start"].clicked.connect(self.initialize)
        self.controls["new_puzzle"].textActivated.connect(self.load_puzzle)
        self.rules["eto_rule"].clicked.connect(
            lambda: self.run_rule("elimination_to_one")
        )
        self.rules["spl_rule"].clicked.connect(
            lambda: self.run_rule("single_possible_location")
        )
        self.rules["matched_pairs"].clicked.connect(
            lambda: self.run_rule("matched_pairs")
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
        self.main.update_gui()

    def load_puzzle(self, t: str) -> None:
        self.sudoku.load(self.puzzles_dict[t])
        self.sudoku.initialize()
        self.main.update_gui()

    def run_rule(self, rule: str) -> None:
        self.sudoku.run_rule(rule)
        self.main.update_gui()


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
