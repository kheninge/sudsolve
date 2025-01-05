import pytest
from sudoku import Sudoku, Cell, NineSquare


@pytest.fixture(scope="function")
def setup_cell():
    my_cell = Cell()
    my_cell.init(5)
    yield my_cell


def test_cell_valid_init_5(setup_cell):
    assert setup_cell.solution == 5
    assert setup_cell.initial == 5


def test_cell_valid_init_none():
    my_cell = Cell()
    my_cell.init(None)
    assert my_cell.solution is None
    assert my_cell.initial is None


def test_cell_invalid_init_10():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.init(10)


def test_cell_invalid_init_string():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.init("foo")


def test_cell_invalid_init_0():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.init(0)


def test_cell_before_init_call_empty():
    my_cell = Cell()
    assert my_cell.solution is None
    assert my_cell.initial is None
    assert len(my_cell.potentials) == 9


def test_cell_add_single_potentials(setup_cell):
    setup_cell.add_potentials(3)
    foo = setup_cell.potentials
    assert 3 in foo


def test_invalid_potentials(setup_cell):
    with pytest.raises(ValueError):
        setup_cell.add_potentials(10)


def test_cell_add_mult_potentials(setup_cell):
    setup_cell.clear_potentials()
    vals = {1, 2, 5}
    setup_cell.add_potentials(vals)
    foo = setup_cell.potentials
    assert 1 in foo
    assert 2 in foo
    assert 5 in foo
    assert 7 not in foo


def test_remove_single_potentials(setup_cell):
    setup_cell.clear_potentials()
    setup_cell.add_potentials({1, 2, 5})
    setup_cell.remove_potentials(2)
    foo = setup_cell.potentials
    assert 1 in foo
    assert 2 not in foo
    assert 5 in foo
    assert 7 not in foo
    setup_cell.remove_potentials(2)  # do it twice to ensure no error


def test_cell_remove_mult_potentials(setup_cell):
    setup_cell.clear_potentials()
    setup_cell.add_potentials({1, 2, 5})
    setup_cell.remove_potentials({2, 5})
    foo = setup_cell.potentials
    assert 1 in foo
    assert 2 not in foo
    assert 5 not in foo
    assert 7 not in foo
    setup_cell.remove_potentials({2, 5})  #


def test_cell_elimination_loop_solution_not_found():
    """sample 9 cell setup
    | 4 | 7 | _ |
    | 1 | ? | 2 |
    | _ | 6 | _ |
    potentials should be {3, 5, 8, 9}

    """
    r0c0 = Cell(4)
    r0c1 = Cell(7)
    r0c2 = Cell()
    r1c0 = Cell(1)
    r1c1 = Cell()
    r1c2 = Cell(2)
    r2c0 = Cell()
    r2c1 = Cell(6)
    r2c2 = Cell()
    # row connection
    r0c0.rnext = r0c1
    r0c1.rnext = r0c2
    r0c2.rnext = r0c0
    r1c0.rnext = r1c1
    r1c1.rnext = r1c2
    r1c2.rnext = r1c0
    r2c0.rnext = r2c1
    r2c1.rnext = r2c2
    r2c2.rnext = r2c0
    # column connection
    r0c0.cnext = r1c0
    r1c0.cnext = r2c0
    r2c0.cnext = r0c0
    r0c1.cnext = r1c1
    r1c1.cnext = r2c1
    r2c1.cnext = r0c1
    r0c2.cnext = r1c2
    r1c2.cnext = r2c2
    r2c2.cnext = r0c2
    # square connection
    r0c0.snext = r0c1
    r0c1.snext = r0c2
    r0c2.snext = r1c0
    r1c0.snext = r1c1
    r1c1.snext = r1c2
    r1c2.snext = r2c0
    r2c0.snext = r2c1
    r2c1.snext = r2c2
    r2c2.snext = r0c0

    progress = r1c1.elimination_loop()
    assert progress
    assert r1c1.potentials == {3, 5, 8, 9}
    assert r1c1.solution is None
    assert r1c1.initial is None
    progress = r1c1.elimination_loop()
    # second time through potentials should not change
    assert not progress


def test_cell_elimination_loop_solution_is_found():
    """sample 9 cell setup
    | 4 | 7 | 3 |
    | 1 | ? | 2 |
    | 5 | 6 | 8 |
    solution should be 9

    """
    r0c0 = Cell(4)
    r0c1 = Cell(7)
    r0c2 = Cell(3)
    r1c0 = Cell(1)
    r1c1 = Cell()
    r1c2 = Cell(2)
    r2c0 = Cell(5)
    r2c1 = Cell(6)
    r2c2 = Cell(8)
    # row connection
    r0c0.rnext = r0c1
    r0c1.rnext = r0c2
    r0c2.rnext = r0c0
    r1c0.rnext = r1c1
    r1c1.rnext = r1c2
    r1c2.rnext = r1c0
    r2c0.rnext = r2c1
    r2c1.rnext = r2c2
    r2c2.rnext = r2c0
    # column connection
    r0c0.cnext = r1c0
    r1c0.cnext = r2c0
    r2c0.cnext = r0c0
    r0c1.cnext = r1c1
    r1c1.cnext = r2c1
    r2c1.cnext = r0c1
    r0c2.cnext = r1c2
    r1c2.cnext = r2c2
    r2c2.cnext = r0c2
    # square connection
    r0c0.snext = r0c1
    r0c1.snext = r0c2
    r0c2.snext = r1c0
    r1c0.snext = r1c1
    r1c1.snext = r1c2
    r1c2.snext = r2c0
    r2c0.snext = r2c1
    r2c1.snext = r2c2
    r2c2.snext = r0c0

    progress = r1c1.elimination_loop()
    assert progress
    assert not r1c1.potentials
    assert r1c1.solution == 9
    assert r1c1.initial is None
