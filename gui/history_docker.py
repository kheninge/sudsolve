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
        self.delete = QPushButton("Delete (d)")
        self.prune = QPushButton("Prune (p)")
        self.history_log = QLabel()

        button_layout1 = QHBoxLayout()
        button_layout1.addWidget(self.left_button)
        button_layout1.addWidget(self.right_button)
        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(self.delete)
        button_layout2.addWidget(self.prune)
        layout = QVBoxLayout()
        layout.addWidget(self.history_log)
        layout.addLayout(button_layout2)
        layout.addLayout(button_layout1)
        self.setLayout(layout)

    def update_history(self) -> None:
        text = "\n".join(self.sudoku.history.print_out())
        self.history_log.setText(text)
