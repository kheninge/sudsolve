import pytest
from sudoku.history import History
from sudoku.cell import Cell


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


def test_speculative_solution():
    history = History()
    my_cell = Cell(0, history)
    my_cell.set_speculative_solution(6, False)
    assert my_cell.speculative_solution
    assert my_cell.solution == 6


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


def test_cell_consistency_check():
    """sample 9 cell setup
    | 4 | 4 |
    | 1 | 2 |

    """
    r0c0 = Cell(id=0, initial=4)
    r0c1 = Cell(id=0, initial=4)
    r1c0 = Cell(id=0, initial=1)
    r1c1 = Cell(id=0, initial=2)
    # connections
    r0c0.connect("row", r0c1)
    r0c1.connect("row", r0c0)
    r1c0.connect("row", r1c1)
    r1c1.connect("row", r1c0)
    r0c0.connect("col", r1c0)
    r0c1.connect("col", r1c1)
    r1c0.connect("col", r0c0)
    r1c1.connect("col", r0c1)
    r0c0.connect("square", r0c1)
    r0c1.connect("square", r1c0)
    r1c0.connect("square", r1c1)
    r1c1.connect("square", r0c0)
    assert not r0c0.check_consistency()  # should fail


def test_cell_elimination_to_one_loop_solution_not_found():
    """sample 9 cell setup
    | 4 | 7 | _ |
    | 1 | ? | 2 |
    | _ | 6 | _ |
    potentials should be {3, 5, 8, 9}

    """
    r0c0 = Cell(initial=4)
    r0c1 = Cell(initial=7)
    r0c2 = Cell()
    r1c0 = Cell(initial=1)
    r1c1 = Cell()
    r1c2 = Cell(initial=2)
    r2c0 = Cell()
    r2c1 = Cell(initial=6)
    r2c2 = Cell()
    # row connection
    r0c0.connect("row", r0c1)
    r0c1.connect("row", r0c2)
    r0c2.connect("row", r0c0)
    r1c0.connect("row", r1c1)
    r1c1.connect("row", r1c2)
    r1c2.connect("row", r1c0)
    r2c0.connect("row", r2c1)
    r2c1.connect("row", r2c2)
    r2c2.connect("row", r2c0)
    # column connection
    r0c0.connect("col", r1c0)
    r1c0.connect("col", r2c0)
    r2c0.connect("col", r0c0)
    r0c1.connect("col", r1c1)
    r1c1.connect("col", r2c1)
    r2c1.connect("col", r0c1)
    r0c2.connect("col", r1c2)
    r1c2.connect("col", r2c2)
    r2c2.connect("col", r0c2)
    # square connection
    r0c0.connect("square", r0c1)
    r0c1.connect("square", r0c2)
    r0c2.connect("square", r1c0)
    r1c0.connect("square", r1c1)
    r1c1.connect("square", r1c2)
    r1c2.connect("square", r2c0)
    r2c0.connect("square", r2c1)
    r2c1.connect("square", r2c2)
    r2c2.connect("square", r0c0)

    progress = r1c1.run_rule("elimination_to_one")
    assert r1c1.check_consistency()  # should pass
    assert not progress
    assert r1c1.potentials == {3, 5, 8, 9}
    assert r1c1.solution is None
    assert r1c1.new_solution is False
    assert r1c1.initial is None
    progress = r1c1.run_rule("elimination_to_one")
    # second time through potentials should not change
    assert not progress

    ## Test count_multiples using exiting test setup TODO could set up a fixture
    singles = r1c1._gather_multiples(1, "square")
    assert len(singles) == 0
    quads = r1c1._gather_multiples(4, "square")
    assert quads == {3, 5, 8, 9}
    assert len(quads) == 4
    singles = r1c1._gather_multiples(1, "row")
    assert len(singles) == 4
    assert singles == {3, 5, 8, 9}


def test_cell_elimination_to_one_loop_solution_is_found():
    """sample 9 cell setup
    | 4 | 7 | 3 |
    | 1 | ? | 2 |
    | 5 | 6 | 8 |
    solution should be 9

    """
    r0c0 = Cell(initial=4)
    r0c1 = Cell(initial=7)
    r0c2 = Cell(initial=3)
    r1c0 = Cell(initial=1)
    r1c1 = Cell()
    r1c2 = Cell(initial=2)
    r2c0 = Cell(initial=5)
    r2c1 = Cell(initial=6)
    r2c2 = Cell(initial=8)
    # row connection
    r0c0.connect("row", r0c1)
    r0c1.connect("row", r0c2)
    r0c2.connect("row", r0c0)
    r1c0.connect("row", r1c1)
    r1c1.connect("row", r1c2)
    r1c2.connect("row", r1c0)
    r2c0.connect("row", r2c1)
    r2c1.connect("row", r2c2)
    r2c2.connect("row", r2c0)
    # column connection
    r0c0.connect("col", r1c0)
    r1c0.connect("col", r2c0)
    r2c0.connect("col", r0c0)
    r0c1.connect("col", r1c1)
    r1c1.connect("col", r2c1)
    r2c1.connect("col", r0c1)
    r0c2.connect("col", r1c2)
    r1c2.connect("col", r2c2)
    r2c2.connect("col", r0c2)
    # square connection
    r0c0.connect("square", r0c1)
    r0c1.connect("square", r0c2)
    r0c2.connect("square", r1c0)
    r1c0.connect("square", r1c1)
    r1c1.connect("square", r1c2)
    r1c2.connect("square", r2c0)
    r2c0.connect("square", r2c1)
    r2c1.connect("square", r2c2)
    r2c2.connect("square", r0c0)

    progress = r1c1.run_rule("elimination_to_one")
    assert progress
    assert not r1c1.potentials
    assert r1c1.solution == 9
    assert r1c1.new_solution
    assert r1c1.initial is None
    progress = r1c1.run_rule("elimination_to_one")
    assert not r1c1.new_solution


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
    my_cell.connect("row", row_partner)
    my_cell.connect("col", col_partner)
    my_cell.connect("square", square_partner)
    row_partner.connect("row", my_cell)
    col_partner.connect("col", my_cell)
    square_partner.connect("square", my_cell)

    result = my_cell.run_rule("single_possible_location")
    assert result
    assert my_cell.solution == 3
    assert my_cell.new_solution
