#!/usr/bin/bash
python3 -m cProfile -m pytest tests/test_sudoku.py &>profile.out
