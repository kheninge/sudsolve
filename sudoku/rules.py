from abc import ABC, abstractmethod
from typing import cast
import logging
from sudoku.defines import (
    DirectionType,
    SUD_RANGE,
    CSPACES,
)
from sudoku.generic_structure import GenericStructure
from sudoku.subline import SubLine
import itertools
from sudoku.cell import Cell

logger = logging.getLogger(__name__)


class SudokuRule(ABC):
    """A protocol for rules to run on the sudoku cell network by a RuleEngine"""

    _name = "Undefined_SudokuRule"
    _structure_type = "undefined"

    def __init__(self, target: int | str):
        self._target = target

    @abstractmethod
    def run(self, structure: GenericStructure) -> bool:
        """Runs the rule on the specified structure i.e. cell or subline etc and returns progress as a bool"""

    @property
    def name(self) -> str:
        """Outputs the name of the rule used for history or other purposes"""
        return self._name

    @property
    def target(self) -> int | str:
        return self._target

    @property
    def structure_type(self) -> str:
        return self._structure_type

    # TODO this goes somewhere else
    def _gather_multiples(
        self, cell: Cell, mode: int, direction: DirectionType
    ) -> set[int]:
        """Traverse the space looking for mode number of occurences in potentials i.e. singles, pairs, triplets etc
        Returns a set of those potentials"""
        pot_count = dict.fromkeys(SUD_RANGE, 0)
        pot_list = set()
        cells = cell.network.clist[direction]
        for c in cells:
            for num in c.potentials:
                pot_count[num] += 1
        # Analyze potential_count statistics to see if there are any unique (just one) potential
        # If so then build a list of those numbers
        for num, count in pot_count.items():
            if count == mode:
                pot_list.add(num)
        return pot_list


class CellRule(SudokuRule):
    """A protocol for rules to run on the sudoku cell network by a RuleEngine"""

    _structure_type = "cell"


class SublineRule(SudokuRule):
    """A protocol for rules to run on the sudoku cell network by a RuleEngine"""

    _structure_type = "subline"


class EliminationToOneRule(CellRule):
    _name = "elimination_to_one"

    def run(self, structure: GenericStructure) -> bool:
        """Eliminate all solutions seen in constrained spaces and if a single potential is left designate it
        the solution"""
        cell = cast(Cell, structure)
        progress = False
        if len(cell.potentials) == 1:
            # Solved
            # TODO using internal _, should this just be made available or need a helper function?
            (mysolution,) = cell.potentials
            cell.set_solution(mysolution)
            cell.remove_potential_in_cspaces(mysolution)
            progress = True

        return progress


class SpeculativeSolution(CellRule):
    _name = "speculative_solution"

    def __init__(self, target: int | str, val: int):
        super().__init__(target)
        self._val = val
        self._name = self._name + f"({self._val})"

    def run(self, structure: GenericStructure) -> bool:
        cell = cast(Cell, structure)
        cell.speculative_solution = self._val
        return True


class EliminationRule(CellRule):
    _name = "elimination_visible"

    def run(self, structure: GenericStructure) -> bool:
        """Eliminate all solutions seen in constrained spaces. This step is run for every rule, but in this case
        just run the elimination step"""
        home_cell = cast(Cell, structure)
        if home_cell.solved:
            return False
        potential_starting_len = len(home_cell.potentials)
        for direction in CSPACES:
            node = cast(Cell, home_cell.network.traverse(direction))
            while node != home_cell:
                if node.solution:
                    _ = home_cell.remove_potential(node.solution)
                node = cast(Cell, node.network.traverse(direction))
            # If all potentials are gone something is wrong mark the cell in error
            if not home_cell.potentials:
                home_cell._error = True
        if len(home_cell._potentials) < potential_starting_len:
            logger.debug("Cell %d made progress on potentials", home_cell.id)
            return True
        else:
            return False


class SinglePossibleLocationRule(CellRule):
    _name = "single_possible_location"

    def run(self, structure: GenericStructure) -> bool:
        """Look through potentials determined by other rules. If a potential number is only present within this cell
        for a given constrained space, then that is the solution"""

        cell = cast(Cell, structure)
        # Iterate over row, col and square.
        for direction in CSPACES:
            singles_set = self._gather_multiples(cell, 1, direction)
            # Now see if any of our cell potentials is in the list, if so set it as the solution
            for num in cell.potentials:
                if num in singles_set:
                    cell.set_solution(num)
                    cell.remove_potential_in_cspaces(num)
                    return True  # short circuit if solution found
        return False


class FilledCellsRule(CellRule):
    _name = "filled_cells"

    def run(self, structure: GenericStructure) -> bool:
        """Any time you have 1 potential constrained to a single cell or 2 potentials constrained to 2 cells or n
        potentials constrained to n cells then there is no room for any other potential in those cells.
        This is a generalization of the single possible location rule. Note that this does not require that the
        potentials show up in all n cells. So a triple, a double and a single that are constrained to 3 cells would
        meet the criteria"""
        cell = cast(Cell, structure)
        total_return = False

        for direction in CSPACES:
            # Use the convenience list and add own cell for a complete network
            cells = cell.network.clist[direction]
            potentials_set = set()
            for cell in cells:
                potentials_set |= cell.potentials
            for n in range(1, len(potentials_set) + 1):
                for combo in itertools.combinations(potentials_set, n):
                    combo = set(combo)
                    matching_cells = []
                    for cell in cells:
                        if cell.potentials & combo:
                            matching_cells.append(cell)
                    if len(matching_cells) == n:
                        # We have found a set of matched pairs, now go through each cell and eliminate any potential
                        # that is not part of the matched pair combination
                        for cell in matching_cells:
                            to_remove = cell.potentials - combo
                            for p in to_remove:
                                _ = cell.remove_potential(p)
                                total_return |= True
        return total_return


class FilledPotentialsRule(CellRule):
    _name = "filled_potentials"

    def run(self, structure: GenericStructure) -> bool:
        """This rule relies on the same premise as filled_cells, that n values constrained to n cells is full and
        there is no more room. Filled potentials is the inferred opposite, if you find any n cells that only contain
        n potential values then you can assume those potential values will not be seen in the other cells. This is
        the general case of the eliminate to one rule as that rule is just the 1 value in 1 cell case.
        """
        cell = cast(Cell, structure)
        total_return = False

        for direction in CSPACES:
            cells = cell.network.clist[direction]
            # Build a list of unsolved cells
            unsolved_cells = []
            for c in cells:
                if not c.solved:
                    unsolved_cells.append(c)
            for n in range(1, len(unsolved_cells) + 1):
                for combo in itertools.combinations(unsolved_cells, n):
                    potentials_set = set()
                    for mycell in combo:
                        potentials_set |= mycell.potentials
                    if len(potentials_set) == len(combo):
                        # We have found a set of matched pairs, now go through each cell not in the combo and
                        # eliminate any potential from the combo
                        for mycell in unsolved_cells:
                            if mycell in combo:
                                continue
                            for p in potentials_set:
                                progress = mycell.remove_potential(p)
                                total_return |= progress
        return total_return


class AlignedPotentialsRule(SublineRule):
    _name = "aligned_potentials"

    def run(self, structure: GenericStructure) -> bool:
        """Utilizes the subline structures. Looks for occurences of a potential in ..."""
        subline = cast(SubLine, structure)
        progress = False
        # Gather up all of the possible potentials
        pot_count = dict.fromkeys(SUD_RANGE, 0)
        for cell in subline.overlap:
            if cell.solved:
                continue
            for num in cell.potentials:
                pot_count[num] += 1
        # See which have more than 1
        for p, cnt in pot_count.items():
            if cnt > 1:
                # Check if potential exists in non-overlap square
                found_in_non_ov_square = False
                for cell in subline.square_non_over_lap:
                    if p in cell.potentials:
                        found_in_non_ov_square = True
                if not found_in_non_ov_square:
                    # This is the aligned case
                    for cell in subline.line_non_over_lap:
                        progress = progress | cell.remove_potential(p)
                else:
                    found_in_non_ov_line = False
                    for cell in subline.line_non_over_lap:
                        if p in cell.potentials:
                            found_in_non_ov_line = True
                    if not found_in_non_ov_line:
                        for cell in subline.square_non_over_lap:
                            progress = progress | cell.remove_potential(p)
        return progress
