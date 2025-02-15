import logging
from sudoku.cell import Cell
from sudoku.cellnetwork import CellNetwork
from sudoku.subline import SubLine
from sudoku.defines import NineSquareValType, SUD_SPACE_SIZE

logger = logging.getLogger(__name__)


class NineSquare:
    """Represents the 9 cells in a Sudoku square.
    Provides a building block for building out a full Sudoku Mesh
    Instantiate and connect 9 cells in a square
    Connect the 2 row pointer
    * initialize(vals) - takes a tuple of 9 values and assigns them to the nine cells
    * attach_row(self, some_nine_square) - connect the given nine square to self's pointers
    * attach_col(self, some_nine_square) - connect the given nine square to self's pointers
    * connect_sublines(self) - creates the subline structures needed for the aligned_potentials rule
    * cell(row, col) - given a row, column returns the cell at that location
    * elimination_to_one_loop() - iterate through all cells and call their elimination_to_one_loop method
                        returns true if any of them made progress
    """

    def __init__(
        self,
        id: int,
    ) -> None:
        self.id: int = id
        self.rules = {
            "aligned_potentials": self._rule_aligned_potentials,
        }
        self.cells: list[Cell] = []  # A list of cells to represent a NineSquare
        # Instantiate Cells
        for i in range(SUD_SPACE_SIZE):
            self.cells.append(Cell(self.id * SUD_SPACE_SIZE + i, CellNetwork()))
        self._connect_cell_network()

    def _connect_cell_network(self):
        # Connect up rows of the NineSquare
        for i in (0, 3, 6):
            self.cells[i].network.connect("row", self.cells[i + 1])
            self.cells[i + 1].network.connect("row", self.cells[i + 2])
        # Connect up columns of the NineSquare
        for i in range(3):
            self.cells[i].network.connect("col", self.cells[i + 3])
            self.cells[i + 3].network.connect("col", self.cells[i + 6])
        # Connect up the NineSquare Loop
        for i in range(8):
            self.cells[i].network.connect("square", self.cells[i + 1])
        self.cells[8].network.connect("square", self.cells[0])

    def create_sublines(self):
        # This function has to run after the full cell network has been connected up since SubLine init will connect
        # up a subline network which relies on the full cell network
        self.sublines = [
            SubLine(self.cells[0], "col"),
            SubLine(self.cells[1], "col"),
            SubLine(self.cells[2], "col"),
            SubLine(self.cells[0], "row"),
            SubLine(self.cells[3], "row"),
            SubLine(self.cells[6], "row"),
        ]

    def initialize(self, vals: NineSquareValType) -> None:
        for i in range(SUD_SPACE_SIZE):
            self.cells[i].initialize(vals[i])

    @property
    def solved(self) -> bool:
        all_solved = True
        for cell in self.cells:
            all_solved &= cell.solved
        return all_solved

    @property
    def solutions(self) -> NineSquareValType:
        sols = []
        for i in range(SUD_SPACE_SIZE):
            sols.append(self.cells[i].solution)
        return tuple(sols)

    def cell(self, row: int, col: int) -> Cell:
        """returns a cell pases on row and column coordinates"""
        i = row * 3 + col
        return self.cells[i]

    def attach_row(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another to the right"""
        self.cells[2].network.connect("row", other.cell(0, 0))
        self.cells[5].network.connect("row", other.cell(1, 0))
        self.cells[8].network.connect("row", other.cell(2, 0))

    def attach_col(self, other: "NineSquare") -> None:
        """Connect this NineSquare to another below"""
        self.cells[6].network.connect("col", other.cell(0, 0))
        self.cells[7].network.connect("col", other.cell(0, 1))
        self.cells[8].network.connect("col", other.cell(0, 2))

    def _rule_aligned_potentials(self):
        progress = False
        for subline in self.sublines:
            progress = progress | subline.aligned_potentials()
        return progress
