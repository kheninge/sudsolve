from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from gui.fixed_size_control import FixedSizeControl
from gui.history_docker import RightDocker
from gui.controls_view import ControlsView
from gui.sudoku_game_views import SudokuView


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
        puzzle_widget: SudokuView,
        right_docker: RightDocker,
        control_widget: ControlsView,
        sizes: FixedSizeControl,
    ) -> None:
        super().__init__()

        # Define Layout
        layout = QVBoxLayout()
        layout.addWidget(puzzle_widget)
        layout.addWidget(control_widget)
        widget = QWidget()
        widget.setFixedWidth(sizes.app_width)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_docker)
