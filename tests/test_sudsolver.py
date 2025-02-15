import pytest
import yaml
import sudsolver


@pytest.fixture()
def open_yaml():
    with open("../sudoku.yaml", "r") as file:
        stored_puzzles = yaml.safe_load(file)
    yield stored_puzzles


def test_convert_to_ns_format(open_yaml):
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
    converted_puzzles = sudsolver.convert_to_ns_format(open_yaml)
    assert converted_puzzles["puzzlepack01"] == init1
