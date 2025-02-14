from PySide6.QtWidgets import (
    QGridLayout,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMenu,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QContextMenuEvent
from gui.update_controller import UpdateController
from sudoku.sudoku import Sudoku
from sudoku.ninesquare import NineSquare
from sudoku.cell import Cell

COLOR_YELLOW = "#f4f8b2"
COLOR_RED = "red"


class SudokuView(QWidget):
    def __init__(self, sudoku: Sudoku, updater: UpdateController) -> None:
        super().__init__()
        self.sudoku = sudoku
        self.ns = []  # Keep a list of nine-squares

        # Suduko Grid Layout
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                widget = NineSquareView(self, sudoku.ns[i * 3 + j], updater)
                self.ns.append(widget)
                layout.addWidget(widget, i, j)
        self.setLayout(layout)

    def update_sudoku(self) -> None:
        for ns in self.ns:
            ns.update_ninesquare()


class NineSquareView(QWidget):
    def __init__(
        self, parent, ninesquare: NineSquare, updater: UpdateController
    ) -> None:
        super().__init__(parent)

        self.ninesquare = ninesquare
        # Create layout of 9 widgets to represent cells in a nine-square
        self.cells = []  # track the widgets in this list
        layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                cell_widget = CellWidget(
                    self, self.ninesquare.cells[i * 3 + j], updater
                )
                self.cells.append(cell_widget)
                layout.addWidget(cell_widget, i, j)
        self.setLayout(layout)

    def update_ninesquare(self) -> None:
        for cell in self.cells:
            cell.update_cell()


# TODO style sheets are a mess


class CellWidget(QStackedWidget):
    def __init__(self, parent, cell, updater: UpdateController) -> None:
        super().__init__(parent)
        self.cell = cell
        cell_dim = self.width()
        # Hints cells are kind of squished to the left so 1/2 just gives more room in the case of a 2 pixel remainder
        hint_dim = int(cell_dim * 0.40)
        self.setFixedHeight(cell_dim)
        self.normal_font = int(cell_dim * 0.6)
        hint_font = int(cell_dim * 0.15)
        self.style_normal_background = (
            f" border: 1px solid black;  font-size: {self.normal_font}px;"
        )
        self.style_hints_normal_no_border = (
            f"border: none;  color: gray; font-size: {hint_font}px;"
        )
        self.style_hints_yellow_no_border = f"background-color: {COLOR_YELLOW};border: none; color: gray; font-size: {hint_font}px;"
        self.hint_wrapper = QWidget()
        self.hint_wrapper.setStyleSheet(self.style_normal_background)
        self.hint_view = HintsWidget(hint_dim, self.cell, updater)
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

    def _compose_style(self, cell: Cell) -> str:
        solution_font = "black"  # default
        background = ""
        if cell.in_error:
            background = f"background-color: {COLOR_RED};"
        elif cell.solved:
            if cell.new_solution:
                background = f"background-color: {COLOR_YELLOW};"
            if cell.speculative_solution:
                solution_font = "blue"
        return f"border: 1px solid black; {background}font-size: {self.normal_font}px; color: {solution_font}"

    def update_cell(self):
        if self.cell.in_error or self.cell.solved:
            style = self._compose_style(self.cell)
            self.solved_view.setStyleSheet(style)
            if self.cell.solved:
                val = str(self.cell.solution)  # Labels take strings not int
                self.solved_view.setText(val)
            else:
                self.solved_view.setText(" ")
            self.setCurrentIndex(1)
        else:
            self.hint_wrapper.setStyleSheet(self.style_normal_background)
            self.hint_view.setStyleSheet(self.style_hints_normal_no_border)
            for i in range(1, 10):
                if i in self.cell.potentials:
                    self.hint_view.hint[i - 1].setText(str(i))
                else:
                    self.hint_view.hint[i - 1].setText("")
            for h in self.hint_view.hint:
                h.setStyleSheet(self.style_hints_normal_no_border)
            for e in self.cell.eliminated:
                self.hint_view.hint[e - 1].setStyleSheet(
                    self.style_hints_yellow_no_border
                )
            self.setCurrentIndex(0)


class HintsWidget(QWidget):
    style_hints_normal_no_border = "border: none; "
    style_hints_yellow_no_border = f"background-color: {COLOR_YELLOW};border: none; "

    def __init__(self, dim: int, cell: Cell, updater: UpdateController) -> None:
        super().__init__()
        self.cell = cell
        self.updater = updater
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

    def contextMenuEvent(self, event: QContextMenuEvent):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("color: black")
        context_menu.addAction("Choose a Solution").setEnabled(False)

        actions = {}
        for i in range(1, 10):
            actions[context_menu.addAction(str(i))] = i

        action = context_menu.exec(event.globalPos())
        if action in actions:
            self.cell.set_speculative_solution(actions[action], history_mode=False)
            self.updater.updated.emit()
