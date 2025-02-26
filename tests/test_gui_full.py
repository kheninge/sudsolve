import pytest
from gui.gui_top import GuiTop
from sudoku.sudoku import Sudoku
from PySide6 import QtCore


@pytest.fixture
def puzzle_list():
    puzzles = {
        "One": (
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
    }
    return puzzles


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
    qtbot.keyClicks(new_puzzle, "One")
    assert new_puzzle.currentIndex() == 0
    assert new_puzzle.currentText() == "One"
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
