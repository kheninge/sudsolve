from PySide6.QtWidgets import (
    QComboBox,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt
from gui.fixed_size_control import FixedSizeControl
from gui.history_docker import RightDocker
from sudoku.sudoku import Sudoku, SudokuValType


class ControlsView(QWidget):
    status_normal_style = "font-size: 16pt;"
    status_success_style = "color: green; font-size: 16pt;"

    def __init__(
        self,
        sudoku: Sudoku,
        puzzles_dict: dict[str, SudokuValType],
        sizer: FixedSizeControl,
        docker: RightDocker,
    ) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.right_docker = docker
        self.puzzles_dict = puzzles_dict
        self.control_height = sizer.app_width / 30
        self.control_width = sizer.app_width / 12
        self.rule_width = int(sizer.app_width / 7)

        # Create the Control and Rule Buttons
        self.controls = {
            "new_puzzle": QComboBox(),
            "start": QPushButton("Re-Start (r)"),
            "close": QPushButton("Exit (q)"),
            "history": QPushButton("History (h)"),
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


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
