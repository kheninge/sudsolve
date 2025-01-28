from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from gui.fixed_size_control import FixedSizeControl
from gui.history_docker import RightDocker
from gui.controls_view import ControlsView
from gui.sudoku_game_views import SudokuView
from gui.update_controller import UpdateController
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
        sizes: FixedSizeControl,
        sudoku: Sudoku,
        puzzles_dict: dict[str, SudokuValType],
    ) -> None:
        super().__init__()

        self.app = app
        self.sizes = sizes

        updater = UpdateController()
        # Instantiate Primary Components of Main Window
        self.puzzle_widget = SudokuView(sudoku, updater)
        self.right_docker = RightDocker(sudoku, sizes, updater)
        self.control_widget = ControlsView(
            sudoku, app, puzzles_dict, sizes, updater, self.right_docker
        )

        # Define Layout
        layout = QVBoxLayout()
        layout.addWidget(self.puzzle_widget)
        layout.addWidget(self.control_widget)
        widget = QWidget()
        widget.setFixedWidth(self.sizes.app_width)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_docker)

        # Define Shortcuts
        shortcuts = {
            "q": self.app.quit,
            "x": self.app.quit,
            "r": self.control_widget.initialize,
            "d": self.right_docker.toggle,
            "l": self.right_docker.history_widget.forward,
            "h": self.right_docker.history_widget.back,
            "0": lambda: self.control_widget.run_rule("update_potentials"),
            "1": lambda: self.control_widget.run_rule("elimination_to_one"),
            "2": lambda: self.control_widget.run_rule("single_possible_location"),
            "3": lambda: self.control_widget.run_rule("aligned_potentials"),
            "4": lambda: self.control_widget.run_rule("matched_pairs"),
        }
        for k, func in shortcuts.items():
            QShortcut(QKeySequence(k), self).activated.connect(func)
