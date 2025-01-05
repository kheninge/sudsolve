import pytest
from sudoku import NineSquare


def test_nine_square_init():
    foo = NineSquare()
    vals = (1, 2, None, None, None, 9, 8, 5, None)
    foo.initialize(vals)
    assert foo.cell(0, 0).initial == 1
    assert foo.cell(2, 1).initial == 5


def test_nine_square_init_connect_eliminate():
    """
    | _ | _ | 1 || _ | 2 | _ |
    | _ | _ | _ || 3 | _ | _ |
    | 4 | _ | _ || _ | _ | 7 |
    --------------------------
    | 2 | _ | _ || _ | 1 | _ |
    | _ | _ | _ || 5 | _ | _ |
    | _ | 6 | _ || _ | _ | 9 |
    """

    n00 = NineSquare()
    n01 = NineSquare()
    n10 = NineSquare()
    n11 = NineSquare()

    # Connect
    n00.attach_row(n01)
    n01.attach_row(n00)
    n10.attach_row(n11)
    n11.attach_row(n10)
    n00.attach_col(n10)
    n10.attach_col(n00)
    n01.attach_col(n11)
    n11.attach_col(n01)

    # Initialize
    n00.initialize((None, None, 1, None, None, None, 4, None, None))
    n01.initialize((None, 2, None, 3, None, None, None, None, 7))
    n10.initialize((2, None, None, None, None, None, None, 6, None))
    n11.initialize((None, 1, None, 5, None, None, None, None, 9))

    result1 = n00.elimination_loop()
    result2 = n01.elimination_loop()
    result3 = n10.elimination_loop()
    result4 = n11.elimination_loop()

    assert result1 and result2 and result3 and result4
    assert n00.cell(0, 0).potentials == {3, 5, 6, 7, 8, 9}
    assert not n11.cell(1, 0).potentials
    assert n11.cell(1, 0).solution == 5
    assert n11.cell(2, 1).potentials == {3, 4, 7, 8}
