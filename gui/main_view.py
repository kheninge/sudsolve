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

        self._define_layout()
        self._define_shortcuts()

    def _define_layout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.puzzle_widget)
        main_layout.addWidget(self.control_widget)
        main_widget = QWidget()
        main_widget.setFixedWidth(self.sizes.app_width)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_docker)

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
