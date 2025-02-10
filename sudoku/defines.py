from typing import TypeAlias, Literal

## Define some types
CellValType: TypeAlias = int | None
NineSquareValType: TypeAlias = tuple[CellValType, ...]
SudokuValType: TypeAlias = tuple[NineSquareValType, ...]
DirectionType: TypeAlias = Literal["row", "col", "square"]

## Constant Defines
CSPACES = ("row", "col", "square")
SUD_SPACE_SIZE = 9
SUD_VAL_START = 1
SUD_VAL_END = SUD_SPACE_SIZE
SUD_RANGE = range(SUD_VAL_START, SUD_SPACE_SIZE + SUD_VAL_START)
