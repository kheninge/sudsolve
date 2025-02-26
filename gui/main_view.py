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
        self.control_widget = control_widget
        layout = QVBoxLayout()
        layout.addWidget(puzzle_widget)
        layout.addWidget(control_widget)
        widget = QWidget()
        widget.setFixedWidth(sizes.app_width)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_docker)
