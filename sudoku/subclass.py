import logging

from sudoku.cell import Cell
from sudoku.defines import (
    SUD_RANGE,
    SUD_SPACE_SIZE,
)

logger = logging.getLogger(__name__)


class SubLine:
    """Represents the 3 squares overlapping between a square's row or column and the full row or column
    The concept of a sub row or sub col is useful in solving the aligned potentials rule.
    A subline also has a list of the non overlapping cells in both the square and the line.
    Given a base cell and a direction, the constructor will traverse the cell network and build a list of :
    subrow, non-matching squares, non-matching row/col


    """

    def __init__(self, base: Cell, direction: str) -> None:
        self.overlap = []
        self.sq_non_over_lap = []
        self.ln_non_over_lap = []

        next = base
        if direction == "row":
            sq_next = base
            # Build list of overlap by grabbing first 3 of the row
            for _ in range(3):
                self.overlap.append(next)
                sq_next = next.traverse("square")  # find tail of the first row
                next = next.traverse("row")
            # Next 6 in the row are the non-overlap
            for _ in range(6):
                self.ln_non_over_lap.append(next)
                next = next.traverse("row")
            # Next 6 of the circular NineSquare space is the non-overlap
            for _ in range(6):
                self.sq_non_over_lap.append(sq_next)
                sq_next = sq_next.traverse("square")
        else:
            if direction != "col":
                raise ValueError
            # Column case
            for _ in range(3):
                self.overlap.append(next)
                next = next.traverse("col")
            # Next 6 in the col are the non-overlap
            for _ in range(6):
                self.ln_non_over_lap.append(next)
                next = next.traverse("col")
            next = base
            for _ in range(SUD_SPACE_SIZE):
                if next not in self.overlap:
                    self.sq_non_over_lap.append(next)
                next = next.traverse("square")

    def aligned_potentials(self) -> bool:
        progress = False
        # Gather up all of the possible potentials
        pot_count = dict.fromkeys(SUD_RANGE, 0)
        for cell in self.overlap:
            if cell.solved:
                continue
            for num in cell.potentials:
                pot_count[num] += 1
        # See which have more than 1
        for p, cnt in pot_count.items():
            if cnt > 1:
                # Check if potential exists in non-overlap square
                found_in_non_ov_square = False
                for cell in self.sq_non_over_lap:
                    if p in cell.potentials:
                        found_in_non_ov_square = True
                if not found_in_non_ov_square:
                    # This is the aligned case
                    for cell in self.ln_non_over_lap:
                        progress = progress | cell.remove_potential(p)
                else:
                    found_in_non_ov_line = False
                    for cell in self.ln_non_over_lap:
                        if p in cell.potentials:
                            found_in_non_ov_line = True
                    if not found_in_non_ov_line:
                        for cell in self.sq_non_over_lap:
                            progress = progress | cell.remove_potential(p)
        return progress
