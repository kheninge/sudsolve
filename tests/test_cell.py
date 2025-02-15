import pytest
from sudoku.cellnetwork import CellNetwork
from sudoku.ruleengine import RuleEngine
from sudoku.rules import (
    EliminationToOneRule,
    EliminationRule,
    SinglePossibleLocationRule,
)
from sudoku.cell import Cell


@pytest.fixture(scope="function")
def setup_cell():
    network = CellNetwork()
    my_cell = Cell(0, network)
    my_cell.initialize(5)
    yield my_cell


def test_cell_valid_init_5(setup_cell):
    assert setup_cell.solution == 5
    assert setup_cell.initial == 5
    assert setup_cell.solved


def test_cell_valid_init_none():
    network = CellNetwork()
    my_cell = Cell(0, network)
    my_cell.initialize(None)
    assert my_cell.solution is None
    assert my_cell.initial is None
    assert not my_cell.solved


def test_cell_invalid_init_10():
    network = CellNetwork()
    with pytest.raises(ValueError):
        my_cell = Cell(0, network)
        my_cell.initialize(10)


def test_cell_invalid_init_string():
    network = CellNetwork()
    with pytest.raises(ValueError):
        my_cell = Cell(0, network)
        my_cell.initialize("foo")  # type: ignore


def test_cell_invalid_init_0():
    network = CellNetwork()
    with pytest.raises(ValueError):
        my_cell = Cell(0, network)
        my_cell.initialize(0)


# TODO: This gets put into a ruletest not a cell test
# def test_speculative_solution():
#     history = History()
#     my_cell = Cell(0, history)
#     for dir in my_cell._next.keys():
#         my_cell._next[dir] = my_cell
#     my_cell.set_speculative_solution(6, False)
#     assert my_cell.speculative_solution
#     assert my_cell.solution == 6


def test_cell_before_init_call_empty():
    network = CellNetwork()
    my_cell = Cell(0, network)
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
    r0c0 = Cell(id=0, network=CellNetwork(), initial=4)
    r0c1 = Cell(id=0, network=CellNetwork(), initial=4)
    r1c0 = Cell(id=0, network=CellNetwork(), initial=1)
    r1c1 = Cell(id=0, network=CellNetwork(), initial=2)
    # connections
    r0c0.network.connect("row", r0c1)
    r0c1.network.connect("row", r0c0)
    r1c0.network.connect("row", r1c1)
    r1c1.network.connect("row", r1c0)
    r0c0.network.connect("col", r1c0)
    r0c1.network.connect("col", r1c1)
    r1c0.network.connect("col", r0c0)
    r1c1.network.connect("col", r0c1)
    r0c0.network.connect("square", r0c1)
    r0c1.network.connect("square", r1c0)
    r1c0.network.connect("square", r1c1)
    r1c1.network.connect("square", r0c0)
    # Cheat and poke inside
    r0c0.network._connection_complete = True
    r0c1.network._connection_complete = True
    r1c0.network._connection_complete = True
    r1c1.network._connection_complete = True
    assert not r0c0.check_consistency()  # should fail


def test_cell_elimination_to_one_loop_solution_not_found():
    """sample 9 cell setup
    | 4 | 7 | _ |
    | 1 | ? | 2 |
    | _ | 6 | _ |
    potentials should be {3, 5, 8, 9}

    """
    r0c0 = Cell(0, CellNetwork(), initial=4)
    r0c1 = Cell(1, CellNetwork(), initial=7)
    r0c2 = Cell(2, CellNetwork())
    r1c0 = Cell(3, CellNetwork(), initial=1)
    r1c1 = Cell(4, CellNetwork())
    r1c2 = Cell(5, CellNetwork(), initial=2)
    r2c0 = Cell(6, CellNetwork())
    r2c1 = Cell(7, CellNetwork(), initial=6)
    r2c2 = Cell(8, CellNetwork())
    # row connection
    r0c0.network.connect("row", r0c1)
    r0c1.network.connect("row", r0c2)
    r0c2.network.connect("row", r0c0)
    r1c0.network.connect("row", r1c1)
    r1c1.network.connect("row", r1c2)
    r1c2.network.connect("row", r1c0)
    r2c0.network.connect("row", r2c1)
    r2c1.network.connect("row", r2c2)
    r2c2.network.connect("row", r2c0)
    # column.network.connection
    r0c0.network.connect("col", r1c0)
    r1c0.network.connect("col", r2c0)
    r2c0.network.connect("col", r0c0)
    r0c1.network.connect("col", r1c1)
    r1c1.network.connect("col", r2c1)
    r2c1.network.connect("col", r0c1)
    r0c2.network.connect("col", r1c2)
    r1c2.network.connect("col", r2c2)
    r2c2.network.connect("col", r0c2)
    # square.network.connection
    r0c0.network.connect("square", r0c1)
    r0c1.network.connect("square", r0c2)
    r0c2.network.connect("square", r1c0)
    r1c0.network.connect("square", r1c1)
    r1c1.network.connect("square", r1c2)
    r1c2.network.connect("square", r2c0)
    r2c0.network.connect("square", r2c1)
    r2c1.network.connect("square", r2c2)
    r2c2.network.connect("square", r0c0)

    r0c0.network.completed_connection()
    r0c1.network.completed_connection()
    r0c2.network.completed_connection()
    r1c0.network.completed_connection()
    r1c1.network.completed_connection()
    r1c2.network.completed_connection()
    r2c0.network.completed_connection()
    r2c1.network.completed_connection()
    r2c2.network.completed_connection()

    cell_list = [r1c1]
    rule_engine = RuleEngine(cell_list, list())
    progress = rule_engine.execute(EliminationRule(0))
    assert r1c1.check_consistency()  # should pass
    assert progress
    assert r1c1.potentials == {3, 5, 8, 9}
    assert r1c1.solution is None
    assert r1c1.new_solution is False
    assert r1c1.initial is None
    progress = rule_engine.execute(EliminationRule(0))
    # second time through potentials should not change
    assert not progress

    ## Test count_multiples using exiting test setup TODO could set up a fixture
    mock_rule = EliminationToOneRule("all")
    singles = mock_rule._gather_multiples(r1c1, 1, "square")
    assert len(singles) == 0
    quads = mock_rule._gather_multiples(r1c1, 4, "square")
    assert quads == {3, 5, 8, 9}
    assert len(quads) == 4
    singles = mock_rule._gather_multiples(r1c1, 1, "row")
    assert len(singles) == 4
    assert singles == {3, 5, 8, 9}


def test_cell_elimination_to_one_loop_solution_is_found():
    """sample 9 cell setup
    | 4 | 7 | 3 |
    | 1 | ? | 2 |
    | 5 | 6 | 8 |
    solution should be 9

    """
    r0c0 = Cell(0, CellNetwork(), initial=4)
    r0c1 = Cell(1, CellNetwork(), initial=7)
    r0c2 = Cell(2, CellNetwork(), initial=3)
    r1c0 = Cell(3, CellNetwork(), initial=1)
    r1c1 = Cell(4, CellNetwork())
    r1c2 = Cell(5, CellNetwork(), initial=2)
    r2c0 = Cell(6, CellNetwork(), initial=5)
    r2c1 = Cell(7, CellNetwork(), initial=6)
    r2c2 = Cell(8, CellNetwork(), initial=8)
    # row connection
    r0c0.network.connect("row", r0c1)
    r0c1.network.connect("row", r0c2)
    r0c2.network.connect("row", r0c0)
    r1c0.network.connect("row", r1c1)
    r1c1.network.connect("row", r1c2)
    r1c2.network.connect("row", r1c0)
    r2c0.network.connect("row", r2c1)
    r2c1.network.connect("row", r2c2)
    r2c2.network.connect("row", r2c0)
    # column connection
    r0c0.network.connect("col", r1c0)
    r1c0.network.connect("col", r2c0)
    r2c0.network.connect("col", r0c0)
    r0c1.network.connect("col", r1c1)
    r1c1.network.connect("col", r2c1)
    r2c1.network.connect("col", r0c1)
    r0c2.network.connect("col", r1c2)
    r1c2.network.connect("col", r2c2)
    r2c2.network.connect("col", r0c2)
    # square connection
    r0c0.network.connect("square", r0c1)
    r0c1.network.connect("square", r0c2)
    r0c2.network.connect("square", r1c0)
    r1c0.network.connect("square", r1c1)
    r1c1.network.connect("square", r1c2)
    r1c2.network.connect("square", r2c0)
    r2c0.network.connect("square", r2c1)
    r2c1.network.connect("square", r2c2)
    r2c2.network.connect("square", r0c0)

    r0c0.network.completed_connection()
    r0c1.network.completed_connection()
    r0c2.network.completed_connection()
    r1c0.network.completed_connection()
    r1c1.network.completed_connection()
    r1c2.network.completed_connection()
    r2c0.network.completed_connection()
    r2c1.network.completed_connection()
    r2c2.network.completed_connection()

    cell_list = [r1c1]
    rule_engine = RuleEngine(cell_list, list())
    progress = rule_engine.execute(EliminationRule(0))
    progress = rule_engine.execute(EliminationToOneRule(0))
    assert progress
    assert not r1c1.potentials
    assert r1c1.solution == 9
    assert r1c1.new_solution
    assert r1c1.initial is None
    r1c1.clear_new_solution()
    progress = rule_engine.execute(EliminationToOneRule(0))
    assert not r1c1.new_solution


def test_cell_single_possible_location():
    my_cell = Cell(0, CellNetwork())
    my_cell.clear_potentials()
    my_cell.add_potential(3)

    ## This function requires a network of cells for row, col and square
    row_partner = Cell(1, CellNetwork())
    col_partner = Cell(2, CellNetwork())
    square_partner = Cell(3, CellNetwork())
    row_partner.clear_potentials()  # clear so that they aren't seen by function
    col_partner.clear_potentials()
    square_partner.clear_potentials()
    my_cell.network.connect("row", row_partner)
    my_cell.network.connect("col", col_partner)
    my_cell.network.connect("square", square_partner)
    row_partner.network.connect("row", my_cell)
    col_partner.network.connect("col", my_cell)
    square_partner.network.connect("square", my_cell)

    my_cell.network.completed_connection()
    row_partner.network.completed_connection()
    col_partner.network.completed_connection()
    square_partner.network.completed_connection()

    cell_list = [my_cell]
    rule_engine = RuleEngine(cell_list, list())
    result = rule_engine.execute(SinglePossibleLocationRule(0))
    assert result
    assert my_cell.solution == 3
    assert my_cell.new_solution
