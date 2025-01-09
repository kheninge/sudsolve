from PySide6.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from _pytest.outcomes import Exit


class SSolveMain(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Suduko Logical Rule Solver")

        # Suduko Grip Layout
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                layout.addWidget(NineSquareView(), i, j)
        puzzle_widget = QWidget()
        puzzle_widget.setLayout(layout)

        # Control Widget Added to Bottom
        control_widget = ControlButtons()
        main_layout = QVBoxLayout()
        main_layout.addWidget(puzzle_widget)
        main_layout.addWidget(control_widget)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


class NineSquareView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                value_widget = QLabel()
                value_widget.setStyleSheet("border: 1px solid black;")
                value_widget.setFixedSize(75, 75)
                self.cells.append(value_widget)
                layout.addWidget(value_widget, i, j)
        self.setLayout(layout)


class ControlButtons(QWidget):
    control_height = 50
    control_width = 120
    rule_width = 200

    def __init__(self) -> None:
        super().__init__()

        # Control Buttons
        controls = {
            "new_puzzle": QPushButton("New Puzzle"),
            "start": QPushButton("Start"),
            "close": QPushButton("Exit"),
        }
        for foo in controls:
            controls[foo].setFixedSize(self.control_width, self.control_height)

        # Rule Buttons
        rules = {
            "eto_rule": QPushButton("Elimination to One"),
            "spl_rule": QPushButton("Single Possible Location"),
            "aligned_rule": QPushButton("Aligned Potentials"),
            "matched_pairs": QPushButton("Matched Pairs"),
            "matched_triplets": QPushButton("Matched Triplets"),
        }
        for rule in rules:
            rules[rule].setFixedWidth(self.rule_width)

        header_label = QLabel("Sudoku Logic Rules - Click Button to Apply")

        layout = QVBoxLayout()
        layout.addWidget(header_label)
        layout.addWidget(HLine())
        layout_rules = QHBoxLayout()
        for i, (_, it) in enumerate(rules.items()):
            layout_rules.addWidget(it, i)
        layout_controls = QHBoxLayout()
        for i, (_, it) in enumerate(controls.items()):
            layout_controls.addWidget(it, i)
        layout.addLayout(layout_rules)
        layout.addWidget(HLine())
        layout.addLayout(layout_controls)

        self.setLayout(layout)


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
