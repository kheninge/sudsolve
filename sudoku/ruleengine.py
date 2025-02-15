import logging
from sudoku.subline import SubLine
from sudoku.cell import Cell
from sudoku.rules import SudokuRule

logger = logging.getLogger(__name__)


class RuleEngine:
    """Takes a rule and runs it on the correct structure, cell, subline, ninesquare etc.
    rule protocol."""

    def __init__(self, cells: list[Cell], sublines: list[SubLine]) -> None:
        self.cells = cells
        self.sublines = sublines

    def execute(self, rule: SudokuRule) -> bool:
        if rule.structure_type == "cell":
            target_list = self.cells
        elif rule.structure_type == "subline":
            target_list = self.sublines
        if rule.target == "all":
            total_result = False
            for structure in target_list:
                total_result |= rule.run(structure)
            return total_result
        else:
            return rule.run(target_list[rule.target])
