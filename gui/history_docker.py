from PySide6.QtWidgets import (
    QDockWidget,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from gui.fixed_size_control import FixedSizeControl
from sudoku import Sudoku


class RightDocker(QDockWidget):
    def __init__(self, sudoku: Sudoku, sizer: FixedSizeControl, update_gui) -> None:
        super().__init__()

        self.sizer = sizer
        self.history_widget = HistoryWidget(sudoku, update_gui)
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
            self.width = self.sizer.app_width / 5


class HistoryWidget(QWidget):
    def __init__(self, sudoku: Sudoku, update_gui) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.update_gui = update_gui
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
        self.update_gui()

    def forward(self):
        self.sudoku.replay_history("forward")
        self.update_gui()
