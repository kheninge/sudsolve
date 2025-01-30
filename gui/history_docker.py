from PySide6.QtWidgets import (
    QDockWidget,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)
from gui.fixed_size_control import FixedSizeControl
from sudoku import Sudoku


class RightDocker(QDockWidget):
    def __init__(self, sudoku: Sudoku) -> None:
        super().__init__()

        self.history_widget = HistoryWidget(sudoku)
        self.setWidget(self.history_widget)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setVisible(False)

    def toggle(self):
        self.setVisible(not self.isVisible())


class HistoryWidget(QWidget):
    def __init__(self, sudoku: Sudoku) -> None:
        super().__init__()

        self.sudoku = sudoku
        self.right_button = QPushButton("Forward (l)")
        self.left_button = QPushButton("Back (h)")
        self.history_log = QLabel()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.right_button)
        layout = QVBoxLayout()
        layout.addWidget(self.history_log)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_history(self) -> None:
        text = "\n".join(self.sudoku.history.print_out())
        self.history_log.setText(text)
