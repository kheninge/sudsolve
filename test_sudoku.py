import pytest
from sudoku import Sudoku


def test_sudoku_initialize_and_solutions_match():
    init1 = (
        (1, 2, 3, 4, 5, 6, 7, 8, 9),
        (3, 5, 4, 8, 2, 6, 7, 9, 1),
        (3, 2, 4, 8, 2, 5, 7, 9, 1),
        (3, 5, 4, 8, 2, None, 7, None, 1),
        (3, 5, 4, 8, 2, 6, 7, 9, 1),
        (3, 2, 4, 8, 2, 5, 7, 9, 1),
        (3, 5, 4, 8, 2, None, 7, None, 1),
        (9, 8, 7, 6, 5, 4, 3, 2, 1),
        (3, 5, 4, 8, 2, None, 7, None, 1),
    )

    puzzle = Sudoku()
    puzzle.load(init1)
    puzzle.initialize()
    sols = puzzle.solutions
    assert sols == init1


def test_sudoku_elimination_to_one():
    """Create an initialization map and calculate the answers by hand
    Puzzle 1 from March 2023 Sudoku puzzles
    | 2 _ _ | _ 7 _ | _ 8 6 |
    | 5 7 _ | _ _ 4 | _ _ _ |
    | _ 1 _ | _ _ 6 | _ 4 3 |
    -------------------------
    | _ _ _ | _ 6 9 | _ _ 7 |
    | _ _ 1 | _ _ _ | 3 _ _ |
    | 8 _ _ | 1 3 _ | _ _ _ |
    -------------------------
    | 3 9 _ | 7 _ _ | _ 1 _ |
    | _ _ _ | 4 _ _ | _ 7 9 |
    | 1 8 _ | _ 9 _ | _ _ 4 |
    """
    puzzle = Sudoku()
    init1 = (
        (2, None, None, 5, 7, None, None, 1, None),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (None, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, None, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )

    sols1 = (
        (2, None, None, 5, 7, None, 9, 1, 8),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (4, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, 6, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = puzzle.run_rule("elimination_to_one")
    assert progress
    assert puzzle.sudoku[0].ns[1].eliminated == {1, 2, 5, 6, 7, 8, 9}
    sols = puzzle.solutions
    # print("KHH")
    # print(sols)
    assert sols == sols1


def test_sudoku_single_possible_location():
    """Using the same map as above. Run elimination to one twice. Then single possible location"""
    puzzle = Sudoku()
    assert not puzzle.last_rule_progressed
    init1 = (
        (2, None, None, 5, 7, None, None, 1, None),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (None, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, None, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = puzzle.run_rule("elimination_to_one")
    assert progress
    assert puzzle.last_rule_progressed
    progress = puzzle.run_rule("single_possible_location")
    assert progress
    assert puzzle.last_rule_progressed
    sols = puzzle.solutions
    assert sols[0] == (2, 4, None, 5, 7, 6, 9, 1, 8)


def test_sudoku_simple_solved_after_multiple_calls():
    """Using the same map as above. Run elimination to one twice. Then single possible location"""
    puzzle = Sudoku()
    init1 = (
        (2, None, None, 5, 7, None, None, 1, None),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (None, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, None, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = True
    assert not puzzle.solved
    while progress:
        progress = puzzle.run_rule("elimination_to_one")
    progress = True
    assert not puzzle.solved
    while progress:
        progress = puzzle.run_rule("single_possible_location")
    assert puzzle.solved
    sols = puzzle.solutions
    assert sols == (
        (2, 4, 3, 5, 7, 6, 9, 1, 8),
        (9, 7, 1, 3, 8, 4, 2, 5, 6),
        (5, 8, 6, 9, 2, 1, 7, 4, 3),
        (4, 3, 2, 7, 6, 1, 8, 5, 9),
        (8, 6, 9, 5, 4, 2, 1, 3, 7),
        (1, 5, 7, 3, 9, 8, 4, 6, 2),
        (3, 9, 4, 6, 2, 5, 1, 8, 7),
        (7, 2, 8, 4, 1, 3, 6, 9, 5),
        (6, 1, 5, 8, 7, 9, 2, 3, 4),
    )


def test_sudoku_simple_solved_replay():
    """Using the same map as above. Run elimination to one twice. Then single possible location"""
    puzzle = Sudoku()
    init1 = (
        (2, None, None, 5, 7, None, None, 1, None),
        (None, 7, None, None, None, 4, None, None, 6),
        (None, 8, 6, None, None, None, None, 4, 3),
        (None, None, None, None, None, 1, 8, None, None),
        (None, 6, 9, None, None, None, 1, 3, None),
        (None, None, 7, 3, None, None, None, None, None),
        (3, 9, None, None, None, None, 1, 8, None),
        (7, None, None, 4, None, None, None, 9, None),
        (None, 1, None, None, 7, 9, None, None, 4),
    )
    puzzle.load(init1)
    assert not puzzle.solved
    puzzle.initialize()
    progress = puzzle.run_rule("elimination_to_one")
    assert progress
    chkpnt1 = puzzle.solutions
    progress = puzzle.run_rule("elimination_to_one")
    chkpnt2 = puzzle.solutions
    progress = puzzle.run_rule("single_possible_location")
    chkpnt3 = puzzle.solutions
    progress = puzzle.replay_history("back")
    assert puzzle.solutions == chkpnt2
    progress = puzzle.replay_history("back")
    assert puzzle.solutions == chkpnt1
    progress = puzzle.replay_history("back")
    assert puzzle.solutions == init1
    progress = puzzle.replay_history("forward")
    assert puzzle.solutions == chkpnt1
    progress = puzzle.replay_history("forward")
    assert puzzle.solutions == chkpnt2
    progress = puzzle.replay_history("forward")
    assert puzzle.solutions == chkpnt3


def test_sudoku_with_Daniel():
    """Using the same map as above. Run elimination to one twice. Then single possible location"""
    puzzle = Sudoku()
    init1 = (
        (None, None, None, 2, 1, 8, 4, 9, None),
        (2, None, None, None, 3, 9, 8, 6, 7),
        (None, 3, 8, None, 4, 7, 2, 5, 1),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, 9, 5, 4, None, 6),
        (8, None, None, None, None, 4, None, None, None),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = True
    while progress:
        progress = puzzle.run_rule("elimination_to_one")
    print("After step 1")
    print(puzzle.solutions)
    progress = True
    while progress:
        progress = puzzle.run_rule("single_possible_location")
    print("After step 2")
    print(puzzle.solutions)


def test_sudoku_matched_pairs_single_pair():
    """Sinlge matched pair. The other potentials should be eliminated"""
    puzzle = Sudoku()
    init1 = (
        (None, None, None, 4, None, 5, None, 7, 8),
        (1, 2, None, 6, 7, 8, None, None, None),
        (None, None, None, 9, None, None, None, None, None),
        (3, None, None, 5, None, None, 6, None, None),
        (7, None, None, 8, None, None, 9, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = puzzle.run_rule("matched_pairs")
    assert progress
    pots = puzzle.sudoku[0].cell(1, 1).potentials
    assert pots == {1, 2}


def test_sudoku_matched_pairs_four_pairs():
    """4 matched pairs"""
    puzzle = Sudoku()
    init1 = (
        (None, None, 9, 6, 3, None, None, None, 4),
        (7, 2, None, 5, None, None, 1, None, None),
        (None, None, None, None, None, None, 5, None, None),
        (7, 1, 5, 8, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, 8, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = puzzle.run_rule("matched_pairs")
    assert progress
    pots = puzzle.sudoku[0].cell(1, 2).potentials
    assert pots == {1, 7}
    pots = puzzle.sudoku[0].cell(2, 0).potentials
    assert pots == {2}


def test_sudoku_matched_pairs_four_pairs_only_two_matched():
    """4 pairs but only 2 are matched"""
    puzzle = Sudoku()
    init1 = (
        (None, None, None, None, None, None, None, None, 4),
        (2, 8, None, 1, 5, None, None, None, None),
        (None, None, None, 8, None, None, 1, 5, None),
        (7, None, 1, None, None, 5, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, 7, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None),
    )
    puzzle.load(init1)
    puzzle.initialize()
    progress = puzzle.run_rule("matched_pairs")
    assert progress
    pots = puzzle.sudoku[0].cell(0, 0).potentials
    assert pots == {1, 5}
    pots = puzzle.sudoku[0].cell(0, 1).potentials
    assert pots == {1, 5}
