import pytest
from sudoku.puzzleio import PuzzleList, convert_to_ns_format


@pytest.fixture
def yaml_example():
    example_yaml = """
# An example yaml file, this comment should be preserved
# As well as this one
puzzlepack01: "200070086570004000010006043000069007001000300800130000390700010000400079180090004" #end of line comment
puzzlepack02: "000020800060080902012570004470010009008000500600050087500091230703060090009030000"
# comment between 02 and 07
puzzlepack07: "408007065300028000000400083000060070060702090070050000810006000000590008630800907"
    """
    return example_yaml


@pytest.fixture()
def yaml_file(tmp_path, yaml_example):
    config_path = tmp_path / "test_example.yaml"
    # Open a file for writing
    with open(config_path, "w") as file:
        file.write(yaml_example)
    return config_path


def test_puzzleio_read(yaml_file):
    # Read the yaml file, convert the dictionary list to SudokuVal format
    p = PuzzleList(yaml_file)
    assert len(p.puzzles) == 3
    assert (
        p.puzzles["puzzlepack01"]
        == "200070086570004000010006043000069007001000300800130000390700010000400079180090004"
    )
    assert convert_to_ns_format(p.puzzles["puzzlepack07"])[0][0] == 4
    assert convert_to_ns_format(p.puzzles["puzzlepack07"])[0][1] is None
    assert convert_to_ns_format(p.puzzles["puzzlepack07"])[2][2] == 5


def test_puzzlieio_delete(yaml_file):
    p = PuzzleList(yaml_file)
    assert len(p.puzzles) == 3
    p.delete("puzzlepack01")
    assert len(p.puzzles) == 2


def test_puzzleio_add(yaml_file, tmp_path):
    tmp_test_out = tmp_path / "test_add_write.yaml"
    p = PuzzleList(yaml_file)
    p.add(
        "test_puzzle01",
        "040000100000004609050130800007306290000040000083201400004098070805400000002000080",
    )
    p.write(tmp_test_out)
    with open(tmp_test_out) as file:
        contents = file.read()
        assert "test_puzzle01" in contents
    p2 = PuzzleList(tmp_test_out)
    assert (
        p2.puzzles["test_puzzle01"]
        == "040000100000004609050130800007306290000040000083201400004098070805400000002000080"
    )


def test_puzzleio_add_same_is_ignored(yaml_file):
    p = PuzzleList(yaml_file)
    p.add(
        "puzzlepack01",
        "999999999999999999999999999999999999999999999999999999999999999999999999999999999",
    )
    assert (
        p.puzzles["puzzlepack01"]
        == "200070086570004000010006043000069007001000300800130000390700010000400079180090004"
    )


def test_puzzleio_write_preserves_comments(yaml_file, tmp_path):
    tmp_test_out = tmp_path / "test_preserve_write.yaml"
    p = PuzzleList(yaml_file)
    p.write(tmp_test_out)
    with open(tmp_test_out) as file:
        contents = file.read()
        assert "# comment between 02 and 07" in contents
        assert "#end of line comment" in contents


def test_overwrite_same_file_ok(yaml_file):
    p = PuzzleList(yaml_file)
    p.add(
        "Foo",
        "999999999999999999999999999999999999999999999999999999999999999999999999999999999",
    )
    p.write(yaml_file)
    with open(yaml_file) as file:
        contents = file.read()
        assert "# comment between 02 and 07" in contents
        assert "Foo" in contents


def test_convert_to_ns_format():
    puzzle1 = "200070086570004000010006043000069007001000300800130000390700010000400079180090004"
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
    converted_puzzles = convert_to_ns_format(puzzle1)
    assert converted_puzzles == init1
