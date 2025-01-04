import pytest
from sudoku import Sudoku, Cell, NineSquare


@pytest.fixture(scope="function")
def setup_cell():
    my_cell = Cell()
    my_cell.init(5)
    yield my_cell


def test_cell_valid_init_5(setup_cell):
    assert setup_cell.solved() == 5
    assert setup_cell.initial() == 5


def test_cell_valid_init_none():
    my_cell = Cell()
    my_cell.init(None)
    assert my_cell.solved() is None
    assert my_cell.initial() is None


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
    assert my_cell.solved() is None
    assert my_cell.initial() is None
    assert len(my_cell.potentials()) == 0


def test_cell_add_single_potentials(setup_cell):
    setup_cell.add_potentials(3)
    foo = setup_cell.potentials()
    assert 3 in foo


def test_invalid_potentials(setup_cell):
    with pytest.raises(ValueError):
        setup_cell.add_potentials(10)


def test_cell_add_mult_potentials(setup_cell):
    vals = {1, 2, 5}
    setup_cell.add_potentials(vals)
    foo = setup_cell.potentials()
    assert 1 in foo
    assert 2 in foo
    assert 5 in foo
    assert 7 not in foo


def test_remove_single_potentials(setup_cell):
    setup_cell.add_potentials({1, 2, 5})
    setup_cell.remove_potentials(2)
    foo = setup_cell.potentials()
    assert 1 in foo
    assert 2 not in foo
    assert 5 in foo
    assert 7 not in foo


def test_cell_remove_mult_potentials(setup_cell):
    setup_cell.add_potentials({1, 2, 5})
    setup_cell.remove_potentials({2, 5})
    foo = setup_cell.potentials()
    assert 1 in foo
    assert 2 not in foo
    assert 5 not in foo
    assert 7 not in foo
