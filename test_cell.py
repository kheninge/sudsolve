import pytest
from sudoku import Cell


@pytest.fixture(scope="function")
def setup_cell():
    my_cell = Cell()
    my_cell.initialize(5)
    yield my_cell


def test_cell_valid_init_5(setup_cell):
    assert setup_cell.solution == 5
    assert setup_cell.initial == 5
    assert setup_cell.solved


def test_cell_valid_init_none():
    my_cell = Cell()
    my_cell.initialize(None)
    assert my_cell.solution is None
    assert my_cell.initial is None
    assert not my_cell.solved


def test_cell_invalid_init_10():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.initialize(10)


def test_cell_invalid_init_string():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.initialize("foo")  # type: ignore


def test_cell_invalid_init_0():
    with pytest.raises(ValueError):
        my_cell = Cell()
        my_cell.initialize(0)


def test_cell_before_init_call_empty():
    my_cell = Cell()
    assert my_cell.solution is None
    assert my_cell.initial is None
    assert len(my_cell.potentials) == 9


def test_cell_add_single_potentials(setup_cell):
    setup_cell.add_potential(3)
    foo = setup_cell.potentials
    assert 3 in foo


def test_invalid_potentials(setup_cell):
    with pytest.raises(ValueError):
        setup_cell.add_potential(10)


def test_remove_single_potentials(setup_cell):
    setup_cell.clear_potentials()
    for i in (1, 2, 5):
        setup_cell.add_potential(i)
    setup_cell.remove_potential(2)
    foo = setup_cell.potentials
    assert 1 in foo
    assert 2 not in foo
    assert 5 in foo
    assert 7 not in foo
    setup_cell.remove_potential(2)  # do it twice to ensure no error


def test_cell_elimination_to_one_loop_solution_not_found():
    """sample 9 cell setup
    | 4 | 7 | _ |
    | 1 | ? | 2 |
    | _ | 6 | _ |
    potentials should be {3, 5, 8, 9}

    """
    r0c0 = Cell(0, 4)
    r0c1 = Cell(0, 7)
    r0c2 = Cell()
    r1c0 = Cell(0, 1)
    r1c1 = Cell()
    r1c2 = Cell(0, 2)
    r2c0 = Cell()
    r2c1 = Cell(0, 6)
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

    progress = r1c1.elimination_to_one_loop()
    assert progress
    assert r1c1.potentials == {3, 5, 8, 9}
    assert r1c1.solution is None
    assert r1c1.initial is None
    progress = r1c1.elimination_to_one_loop()
    # second time through potentials should not change
    assert not progress


def test_cell_elimination_to_one_loop_solution_is_found():
    """sample 9 cell setup
    | 4 | 7 | 3 |
    | 1 | ? | 2 |
    | 5 | 6 | 8 |
    solution should be 9

    """
    r0c0 = Cell(0, 4)
    r0c1 = Cell(0, 7)
    r0c2 = Cell(0, 3)
    r1c0 = Cell(0, 1)
    r1c1 = Cell()
    r1c2 = Cell(0, 2)
    r2c0 = Cell(0, 5)
    r2c1 = Cell(0, 6)
    r2c2 = Cell(0, 8)
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

    progress = r1c1.elimination_to_one_loop()
    assert progress
    assert not r1c1.potentials
    assert r1c1.solution == 9
    assert r1c1.initial is None


def test_cell_single_possible_location():
    my_cell = Cell()
    my_cell.clear_potentials()
    my_cell.add_potential(3)

    ## This function requires a network of cells for row, col and square
    row_partner = Cell()
    col_partner = Cell()
    square_partner = Cell()
    row_partner.clear_potentials()  # clear so that they aren't seen by function
    col_partner.clear_potentials()
    square_partner.clear_potentials()
    my_cell.rnext = row_partner
    my_cell.cnext = col_partner
    my_cell.snext = square_partner
    row_partner.rnext = my_cell
    col_partner.cnext = my_cell
    square_partner.snext = my_cell

    result = my_cell.single_possible_location()
    assert result
    assert my_cell.solution == 3
