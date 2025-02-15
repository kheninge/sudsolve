import logging

from sudoku.cell import Cell
from typing import cast
from sudoku.defines import (
    SUD_SPACE_SIZE,
)
from sudoku.generic_structure import GenericStructure

logger = logging.getLogger(__name__)


class SubLine(GenericStructure):
    """Represents the 3 cells which overlap between a line (row, col) and a ninesquare.
    The concept of a sub row or sub col is useful in solving the aligned potentials rule.
    A subline also builds a list of the non overlapping cells in both the ninesquare and the line.
    Given a base cell and a direction, the constructor will traverse the cell network and build a list of :
    subrow, non-matching squares, non-matching row/col


    """

    def __init__(self, base: Cell, direction: str) -> None:
        self.overlap = []
        self.square_non_over_lap = []
        self.line_non_over_lap = []

        next = base
        if direction == "row":
            sq_next = base
            # Build list of overlap by grabbing first 3 of the row
            for _ in range(3):
                self.overlap.append(next)
                # find tail of the first row
                sq_next = cast(Cell, next.network.traverse("square"))
                next = cast(Cell, next.network.traverse("row"))
            # Next 6 in the row are the non-overlap
            for _ in range(6):
                self.line_non_over_lap.append(next)
                next = cast(Cell, next.network.traverse("row"))
            # Next 6 of the circular NineSquare space is the non-overlap
            for _ in range(6):
                self.square_non_over_lap.append(sq_next)
                sq_next = cast(Cell, sq_next.network.traverse("square"))
        else:
            if direction != "col":
                raise ValueError
            # Column case
            for _ in range(3):
                self.overlap.append(next)
                next = cast(Cell, next.network.traverse("col"))
            # Next 6 in the col are the non-overlap
            for _ in range(6):
                self.line_non_over_lap.append(next)
                next = cast(Cell, next.network.traverse("col"))
            next = base
            for _ in range(SUD_SPACE_SIZE):
                if next not in self.overlap:
                    self.square_non_over_lap.append(next)
                next = cast(Cell, next.network.traverse("square"))
