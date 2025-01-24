from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDockWidget,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import QPropertyAnimation, Qt, QRect
from PySide6.QtGui import QShortcut, QKeySequence
from sudoku import Sudoku, SudokuValType, Cell


# TODO:
# * Create a log with sudsovler.py
# * Swap out a label with hints in the appropriate spots (3x3)
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
        # Determine available screen size so we can make the sudoku app fit
        screens = self.app.screens()
        geometry = screens[0].availableGeometry()
        self.full_width = geometry.width()
        self.full_height = geometry.height()
        self.main_width = int(self.full_width * 0.40)
        self.puzzle_widget = SudokuView(sudoku, self)
        self.right_docker = RightDocker(sudoku, self)
        self.control_widget = ControlsView(sudoku, self, puzzles_dict)

        self._define_layout()
        self._configure_mainwindow()
        self._define_shortcuts()

    def _define_layout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.puzzle_widget)
        main_layout.addWidget(self.control_widget)
        main_widget = QWidget()
        main_widget.setFixedWidth(self.main_width)
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


class SudokuView(QWidget):
    def __init__(self, sudoku: Sudoku, main) -> None:
        super().__init__()
        self.sudoku = sudoku
        self.ns = []  # Keep a list of nine-squares

        # Suduko Grid Layout
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                widget = NineSquareView(main, self)
                self.ns.append(widget)
                layout.addWidget(widget, i, j)
        self.setLayout(layout)

    def update_sudoku(self) -> None:
        for i, ns in enumerate(self.ns):
            for j, cell in enumerate(ns.cells):
                cell.update_cell(self.sudoku.sudoku[i].ns[j])


class NineSquareView(QWidget):
    def __init__(self, main, parent) -> None:
        super().__init__(parent)

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                cell_widget = CellWidget(main, self)
                self.cells.append(cell_widget)
                layout.addWidget(cell_widget, i, j)
        self.setLayout(layout)


class CellWidget(QStackedWidget):
    def __init__(self, main, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        cell_dim = self.width()
        # Hints cells are kind of squished to the left so 1/2 just gives more room in the case of a 2 pixel remainder
        hint_dim = int(cell_dim * 0.40)
        self.setFixedHeight(cell_dim)
        normal_font = int(cell_dim * 0.6)
        update_font = int(cell_dim * 0.15)
        self.style_normal_background = (
            f" border: 1px solid black; font-size: {normal_font}px;"
        )
        self.style_yellow_background = f"background-color: yellow; border: 1px solid black; font-size: {normal_font}px;"
        self.style_hints_normal_no_border = (
            f"border: none; color: gray; font-size: {update_font}px;"
        )
        self.style_hints_yellow_no_border = f"background-color: yellow;border: none; color: gray; font-size: {update_font}px;"
        self.hint_wrapper = QWidget()
        self.hint_wrapper.setStyleSheet(self.style_normal_background)
        self.hint_view = HintsWidget(main, hint_dim)
        self.hint_view.setParent(self.hint_wrapper)
        self.hint_view.setStyleSheet(self.style_hints_normal_no_border)
        self.solved_view = QLabel()
        self.solved_view.setStyleSheet(self.style_normal_background)
        self.solved_view.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.addWidget(self.hint_wrapper)
        self.addWidget(self.solved_view)
        self.setCurrentIndex(1)

    def update_cell(self, cell_model: Cell):
        if cell_model.solved:
            val = str(cell_model.solution)  # Labels take strings not int
            self.solved_view.setText(val)
            if cell_model.new_solution:
                self.solved_view.setStyleSheet(self.style_yellow_background)
            else:
                self.solved_view.setStyleSheet(self.style_normal_background)
            self.setCurrentIndex(1)
        else:
            self.hint_wrapper.setStyleSheet(self.style_normal_background)
            self.hint_view.setStyleSheet(self.style_hints_normal_no_border)
            for i in range(1, 10):
                if i in cell_model.potentials:
                    self.hint_view.hint[i - 1].setText(str(i))
                else:
                    self.hint_view.hint[i - 1].setText("")
            for h in self.hint_view.hint:
                h.setStyleSheet(self.style_hints_normal_no_border)
            for e in cell_model.eliminated:
                self.hint_view.hint[e - 1].setStyleSheet(
                    self.style_hints_yellow_no_border
                )
            self.setCurrentIndex(0)


class HintsWidget(QWidget):
    style_hints_normal_no_border = "border: none; "
    style_hints_yellow_no_border = "background-color: yellow;border: none; "

    def __init__(self, main: SSolveMain, dim: int) -> None:
        super().__init__()
        self.main = main
        self.hint = []
        rows = []
        for _ in range(9):
            h = QLabel(self)
            h.setFixedWidth(dim)
            self.hint.append(h)
        for _ in range(3):
            rows.append(QHBoxLayout())
        for row_index, row in enumerate(rows):
            for i in range(3):
                row.addWidget(self.hint[row_index * 3 + i])
        hint_layout = QVBoxLayout()
        for i in range(3):
            hint_layout.addLayout(rows[i])
        self.setLayout(hint_layout)
        for h in self.hint:
            h.setStyleSheet(self.style_hints_normal_no_border)
            h.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            )


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
        puzzles_dict: dict[str, SudokuValType],
    ) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.main = mainwindow
        self.puzzles_dict = puzzles_dict
        self.control_height = self.main.main_width / 30
        self.control_width = self.main.main_width / 12
        self.rule_width = int(self.main.main_width / 7)

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
        self.controls["close"].clicked.connect(self.main.app.quit)
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


class RightDocker(QDockWidget):
    def __init__(self, sudoku: Sudoku, main: SSolveMain) -> None:
        super().__init__()

        self.main = main
        self.history_widget = HistoryWidget(sudoku, main)
        self.setWidget(self.history_widget)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.hide()
        self.hidden = True

    def toggle(self):
        if self.hidden:
            self.show()
            self.hidden = False
            self.width = 0
        else:
            self.hide()
            self.hidden = True
            self.width = self.main.full_width / 5


class HistoryWidget(QWidget):
    def __init__(self, sudoku: Sudoku, main: SSolveMain) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.main = main
        self.right_button = QPushButton("Forward (l)")
        self.left_button = QPushButton("Back (h)")
        self.history_log = QWidget()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.right_button)
        layout = QVBoxLayout()
        layout.addWidget(self.history_log)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.right_button.clicked.connect(self.forward)
        self.left_button.clicked.connect(self.back)

    def back(self):
        self.sudoku.replay_history("back")
        self.main.update_gui()

    def forward(self):
        self.sudoku.replay_history("forward")
        self.main.update_gui()


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
