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


# TODO:
# * Color squares with changes
# * Write a consistency checker - ensure that sudoku state doesn't violate any sudoku rules - Flag any errors in the
#       status field
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
        self._status: str | None = None

        self.setWindowTitle("Kurt's Suduko Logical Rule Solver")

        # Suduko Grid Layout
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
        self.control_widget = ControlButtons(puzzle_dict)
        main_layout = QVBoxLayout()
        main_layout.addWidget(puzzle_widget)
        main_layout.addWidget(self.control_widget)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Controls Buttons Connect Up
        self.control_widget.controls["close"].clicked.connect(self.app.quit)
        self.control_widget.controls["start"].clicked.connect(self.sudoku.initialize)
        self.control_widget.controls["start"].clicked.connect(self.update_gui)
        self.control_widget.controls["new_puzzle"].textActivated.connect(
            self.load_puzzle
        )
        # Rules Buttons Connect Up
        self.control_widget.rules["eto_rule"].clicked.connect(
            self.sudoku.elimination_to_one
        )
        self.control_widget.rules["spl_rule"].clicked.connect(
            self.sudoku.single_possible_location
        )
        # Update cells on every button press
        for it in self.control_widget.rules.values():
            it.clicked.connect(self.update_gui)

    def update_gui(self) -> None:
        data = self.sudoku.solutions
        for i, it in enumerate(self.ns):
            it.update_cells(data[i])
        self.update_status()

    def update_status(self) -> None:
        if self.sudoku.initial_state:
            status = "Initial"
        elif self.sudoku.solved:
            status = "Solved"
        elif self.sudoku.last_rule_progressed:
            status = "Progress"
        else:
            status = "No Progress"
        self.control_widget.update_status(status)

    def load_puzzle(self, t: str) -> None:
        self.sudoku.load(self.puzzle_dict[t])
        self.sudoku.initialize()
        self.update_gui()


class NineSquareView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                cell_widget = QLabel()
                cell_widget.setStyleSheet("border: 1px solid black; font-size: 18pt;")
                cell_widget.setFixedSize(75, 75)
                cell_widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.cells.append(cell_widget)
                layout.addWidget(cell_widget, i, j)
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

    status_normal_style = "font-size: 16pt;"
    status_success_style = "color: green; font-size: 16pt;"

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

        header_label = QLabel("Logic Solutions")
        header_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        control_label = QLabel("Controls")
        control_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        control_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.status_label = QLabel()
        self.status_label.setStyleSheet(self.status_normal_style)
        self.status_label.setAlignment(Qt.AlignRight)

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
        layout.addWidget(control_label)
        layout.addLayout(layout_controls)
        self.setLayout(layout)

    def update_status(self, status: str) -> None:
        self.status_label.setText(status)
        if status == "Solved":
            self.status_label.setStyleSheet(self.status_success_style)
        else:
            self.status_label.setStyleSheet(self.status_normal_style)


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
