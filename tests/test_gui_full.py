import pytest
from gui.gui_top import GuiTop
from sudoku.sudoku import Sudoku
from sudoku.puzzleio import PuzzleList
from PySide6 import QtCore


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


@pytest.fixture
def puzzle_list(yaml_file):
    p = PuzzleList(yaml_file)
    return p


@pytest.fixture
def gui_tester(qtbot, qapp, puzzle_list):
    # Model/Control
    solver = Sudoku()
    # Gui
    gui = GuiTop(qapp, solver, puzzle_list)
    qtbot.add_widget(gui.main_widget)
    return gui.main_widget


def test_gui_full(gui_tester, qtbot):
    new_puzzle = gui_tester.control_widget.controls["new_puzzle"]
    start = gui_tester.control_widget.controls["start"]
    eto_rule = gui_tester.control_widget.rules["eto_rule"]
    spl_rule = gui_tester.control_widget.rules["spl_rule"]
    qtbot.keyClicks(new_puzzle, "puzzlepack01")
    assert new_puzzle.currentIndex() == 0
    assert new_puzzle.currentText() == "puzzlepack01"
    qtbot.mouseClick(start, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Initial"
    qtbot.mouseClick(eto_rule, QtCore.Qt.MouseButton.LeftButton)
    # qtbot.keyPress(gui_tester, QtCore.Qt.Key.Key_1)
    # qtbot.keyPress(gui_tester, "1")
    assert gui_tester.control_widget.status_label.text() == "Progress"
    qtbot.mouseClick(eto_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Progress"
    qtbot.mouseClick(eto_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "No Progress"
    # Run SPL 4 times and should get solved
    qtbot.mouseClick(spl_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Progress"
    qtbot.mouseClick(spl_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Progress"
    qtbot.mouseClick(spl_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Progress"
    qtbot.mouseClick(spl_rule, QtCore.Qt.MouseButton.LeftButton)
    assert gui_tester.control_widget.status_label.text() == "Solved"
