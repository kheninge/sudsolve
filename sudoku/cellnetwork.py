import logging
from typing import Any
from sudoku.generic_structure import GenericStructure
from sudoku.defines import (
    DirectionType,
    CSPACES,
)

logger = logging.getLogger(__name__)


class CellNetwork:
    """A CellNetwork from the perspective of a single cell within that network. That is the network contains a
    cell for a single cell but also the means to traverse the row, column and square for that particular cell
    Built by a network builder class, the cell network gets cell state for an entire sudoku network and provides
    methods for the network to be traversed"""

    def __init__(self):
        self._next: dict[DirectionType, GenericStructure | None] = dict.fromkeys(
            CSPACES
        )
        self._connection_complete = False

    def home_node(self, cell: GenericStructure):
        self.my_cell = cell

    def connect(self, direction: DirectionType, cell: GenericStructure) -> None:
        self._next[direction] = cell

    def traverse(self, direction: DirectionType) -> GenericStructure:
        return self._next[direction]  # type: ignore

    def completed_connection(self) -> None:
        self._connection_complete = True
        self._generate_convenience_lists()

    def _generate_convenience_lists(self):
        self.clist: dict[DirectionType, list[Any]] = {}
        self.olist: dict[DirectionType, list[Any]] = {}
        for direction in CSPACES:
            self.clist[direction] = []
            self.clist[direction].append(self.my_cell)
        for direction in CSPACES:
            self.olist[direction] = []
            count = 0
            cell = self.traverse(direction)
            while cell != self.my_cell and cell is not None:
                self.clist[direction].append(cell)
                self.olist[direction].append(cell)
                cell = cell.network.traverse(direction)
                count += 1
                if count > 100:
                    raise Exception("Cell network is not set up correctly")
            self._node_count = count

    @property
    def connection_ok(self) -> bool:
        return self._check_network_connectivity()

    def _check_network_connectivity(self) -> bool:
        """Check to make sure everything is connected properly for this cell; make sure no endless loops
        on network traversals."""
        # Iterate over row, col and square.
        total_result = self._connection_complete
        for direction in CSPACES:
            ok = len(self.clist[direction]) == (self._node_count - 1)
            total_result = total_result and ok
        return total_result
