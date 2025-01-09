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
from sudoku import NineSquareVal, Sudoku, SudokuVal


# TODO
# * choose a puzzle from a list
# * Give the name of the current puzzle
# * Color squares with changes
# * Swap out a label with hints in the appropriate spots (3x3)
# * Indicate when the puzzle is solved, somehow
# * hot keys for the Buttons
# * scripting language to save order of button pushes
# * puzzle editing mode instead of having to edit the yaml file directly (stretch)
# * code remaining rules


class SSolveMain(QMainWindow):
    def __init__(
        self, app: QApplication, sudoku: Sudoku, puzzle_dict: dict[str, SudokuVal]
    ) -> None:
        super().__init__()

        self.app = app
        self.sudoku = sudoku
        self.puzzle_dict = puzzle_dict

        self.setWindowTitle("Suduko Logical Rule Solver")

        # Suduko Grip Layout
        layout = QGridLayout()
        self.ns = []  # Keep a list of nine-squares
        for i in range(3):
            for j in range(3):
                widget = NineSquareView()
                self.ns.append(widget)
                layout.addWidget(widget, i, j)
        puzzle_widget = QWidget()
        puzzle_widget.setLayout(layout)

        # Control Widget Added to Bottom
        control_widget = ControlButtons(puzzle_dict)
        main_layout = QVBoxLayout()
        main_layout.addWidget(puzzle_widget)
        main_layout.addWidget(control_widget)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Controls Buttons Connect Up
        control_widget.controls["close"].clicked.connect(self.app.quit)
        control_widget.controls["start"].clicked.connect(self.sudoku.initialize)
        control_widget.controls["start"].clicked.connect(self.update_ninesquares)
        control_widget.controls["new_puzzle"].textActivated.connect(self.load_puzzle)
        # Rules Buttons Connect Up
        control_widget.rules["eto_rule"].clicked.connect(self.sudoku.elimination_to_one)
        control_widget.rules["spl_rule"].clicked.connect(
            self.sudoku.single_possible_location
        )
        # Update cells on every button press
        for it in control_widget.rules.values():
            it.clicked.connect(self.update_ninesquares)

    def update_ninesquares(self):
        data = self.sudoku.solutions
        for i, it in enumerate(self.ns):
            it.update_cells(data[i])

    def load_puzzle(self, t: str) -> None:
        self.sudoku.load(self.puzzle_dict[t])
        self.sudoku.initialize()
        self.update_ninesquares()


class NineSquareView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                value_widget = QLabel()
                value_widget.setStyleSheet("border: 1px solid black; font-size: 18pt;")
                value_widget.setFixedSize(75, 75)
                value_widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.cells.append(value_widget)
                layout.addWidget(value_widget, i, j)
        self.setLayout(layout)

    def update_cells(self, data: NineSquareVal):
        for i, cell in enumerate(self.cells):
            val = ""
            if data[i]:
                val = str(data[i])
            cell.setText(val)


class ControlButtons(QWidget):
    control_height = 50
    control_width = 130
    rule_width = 200

    def __init__(self, puzzle_dict: dict[str, SudokuVal]) -> None:
        super().__init__()

        # Control Buttons
        self.controls = {
            "new_puzzle": QComboBox(),
            "start": QPushButton("Re-Start"),
            "close": QPushButton("Exit"),
        }
        self.controls["new_puzzle"].setPlaceholderText("Choose a Puzzle")
        self.controls["new_puzzle"].addItems(puzzle_dict.keys())
        for foo in self.controls:  # Set size
            self.controls[foo].setFixedSize(self.control_width, self.control_height)

        # Rule Buttons
        self.rules = {
            "eto_rule": QPushButton("Elimination to One"),
            "spl_rule": QPushButton("Single Possible Location"),
            "aligned_rule": QPushButton("Aligned Potentials"),
            "matched_pairs": QPushButton("Matched Pairs"),
            "matched_triplets": QPushButton("Matched Triplets"),
        }
        for it in self.rules:  # Set size
            self.rules[it].setFixedWidth(self.rule_width)

        header_label = QLabel("Sudoku Logic Rules - Click Button to Apply")

        # Layout Formatting
        layout_rules = QHBoxLayout()
        for i, rl in enumerate(self.rules.values()):
            layout_rules.addWidget(rl, i)
        layout_controls = QHBoxLayout()
        for i, ct in enumerate(self.controls.values()):
            layout_controls.addWidget(ct, i)
        layout = QVBoxLayout()
        layout.addWidget(header_label)
        layout.addWidget(HLine())
        layout.addLayout(layout_rules)
        layout.addWidget(HLine())
        layout.addLayout(layout_controls)
        self.setLayout(layout)

        # Controls Buttons Connect Up
        # self.controls["close"].clicked.connect(self.app.quit)


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
