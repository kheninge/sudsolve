from PySide6.QtWidgets import (
    QGridLayout,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
from gui.update_controller import UpdateController
from sudoku import Sudoku, Cell


class SudokuView(QWidget):
    def __init__(self, sudoku: Sudoku, updater: UpdateController) -> None:
        super().__init__()
        self.sudoku = sudoku
        self.ns = []  # Keep a list of nine-squares

        updater.add_update(self.update_sudoku)
        # Suduko Grid Layout
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                widget = NineSquareView(self)
                self.ns.append(widget)
                layout.addWidget(widget, i, j)
        self.setLayout(layout)

    def update_sudoku(self) -> None:
        for i, ns in enumerate(self.ns):
            for j, cell in enumerate(ns.cells):
                cell.update_cell(self.sudoku.ns[i].cells[j])


class NineSquareView(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                cell_widget = CellWidget(self)
                self.cells.append(cell_widget)
                layout.addWidget(cell_widget, i, j)
        self.setLayout(layout)


class CellWidget(QStackedWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        cell_dim = self.width()
        # Hints cells are kind of squished to the left so 1/2 just gives more room in the case of a 2 pixel remainder
        hint_dim = int(cell_dim * 0.40)
        self.setFixedHeight(cell_dim)
        normal_font = int(cell_dim * 0.6)
        update_font = int(cell_dim * 0.15)
        self.style_normal_background = (
            f" border: 1px solid black; font-size: {normal_font}px;"
        )
        self.style_yellow_background = f"background-color: yellow; border: 1px solid black; font-size: {normal_font}px;"
        self.style_hints_normal_no_border = (
            f"border: none; color: gray; font-size: {update_font}px;"
        )
        self.style_hints_yellow_no_border = f"background-color: yellow;border: none; color: gray; font-size: {update_font}px;"
        self.hint_wrapper = QWidget()
        self.hint_wrapper.setStyleSheet(self.style_normal_background)
        self.hint_view = HintsWidget(hint_dim)
        self.hint_view.setParent(self.hint_wrapper)
        self.hint_view.setStyleSheet(self.style_hints_normal_no_border)
        self.solved_view = QLabel()
        self.solved_view.setStyleSheet(self.style_normal_background)
        self.solved_view.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.addWidget(self.hint_wrapper)
        self.addWidget(self.solved_view)
        self.setCurrentIndex(1)

    def update_cell(self, cell_model: Cell):
        if cell_model.solved:
            val = str(cell_model.solution)  # Labels take strings not int
            self.solved_view.setText(val)
            if cell_model.new_solution:
                self.solved_view.setStyleSheet(self.style_yellow_background)
            else:
                self.solved_view.setStyleSheet(self.style_normal_background)
            self.setCurrentIndex(1)
        else:
            self.hint_wrapper.setStyleSheet(self.style_normal_background)
            self.hint_view.setStyleSheet(self.style_hints_normal_no_border)
            for i in range(1, 10):
                if i in cell_model.potentials:
                    self.hint_view.hint[i - 1].setText(str(i))
                else:
                    self.hint_view.hint[i - 1].setText("")
            for h in self.hint_view.hint:
                h.setStyleSheet(self.style_hints_normal_no_border)
            for e in cell_model.eliminated:
                self.hint_view.hint[e - 1].setStyleSheet(
                    self.style_hints_yellow_no_border
                )
            self.setCurrentIndex(0)


class HintsWidget(QWidget):
    style_hints_normal_no_border = "border: none; "
    style_hints_yellow_no_border = "background-color: yellow;border: none; "

    def __init__(self, dim: int) -> None:
        super().__init__()
        self.hint = []
        rows = []
        for _ in range(9):
            h = QLabel(self)
            h.setFixedWidth(dim)
            self.hint.append(h)
        for _ in range(3):
            rows.append(QHBoxLayout())
        for row_index, row in enumerate(rows):
            for i in range(3):
                row.addWidget(self.hint[row_index * 3 + i])
        hint_layout = QVBoxLayout()
        for i in range(3):
            hint_layout.addLayout(rows[i])
        self.setLayout(hint_layout)
        for h in self.hint:
            h.setStyleSheet(self.style_hints_normal_no_border)
            h.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            )
