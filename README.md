# Sudoku Assistant (sudsolve)

The Sudoku Assistant isn't a Sudoku solver per se. Rather it is a tool that could help you solve Sudoku puzzles. It was written as an exercise for the author in writing Qt GUI programs and as a way to explore Sudoku solutions through the use of logical inferences. The author has not studied any Sudoku solutions or theory and so the nomenclature used below is unique to this program and will not match up with terminology used in the Sudoku community. Also the following list of inference rules is very likely not a complete list of all possible rules, it is just the ones that he was able to come up with on his own.

The code is open source and provided for use without any license. 

## Release

A windows binary is available under releases.

********************************************************************************

## The Rules

### 0. Elimination

This isn't really a full rule, but rather the definition of Sudoku, which is applied before any rule is run or after a solution is found. The rule is applied by walking through each unsolved cell and *eliminating* any values from the list of potential values that can be seen in the row, column or square that cell belongs to.

### 1. Elimination to One

After eliminating all visible solutions from the list of potential values (rule zero above), if there is one one potential value left then that is deemed to be the solution for that cell.

### 2. Single Possible Location

After eliminating all visible solutions from the list of potential values (rule zero above), if any value is present in only one cell then that is deemed to be the solution for that cell.

### 3. Aligned Potentials

Every row or column overlaps with a square. If there is a value in one or more of the cells in the overlap between line and square, that does not exist in the rest of that line or square (the aligned case), then we can assume that the solution will be present somewhere in the overlap and we can safely eliminate it from the non-overlapping portion of the line or square. This rule does not find solutions, it only eliminates potential values.

### 4. Filled Cells

Any time you have 1 potential value constrained to a 1 cell or 2 potential value  constrained to 2 cells or more generally n potential values constrained to n cells then there is no room for any other potential in those cells. This is a generalization of the single possible location rule. Note that this does not require that all the potential values show up in all n cells. So a triple, a double and a single that are constrained to 3 cells would meet the criteria. Once it is determined that n values are constrained to n cells then those cells are considered *filled* and all other potential values are removed.

### 5. Filled Potentials

This rule relies on the same premise as the above Filled Cells rule. Filled potentials is the opposite inference, if you find any n cells that only contain n potential values then you can assume those cells will be filled by those n values and they can be removed from the list of potential values the other cells. This is the general case of the eliminate to one rule as that rule is just the 1 value in 1 cell case.

********************************************************************************

## Features

### Highlighted Cells

Potential values which have just been eliminated or new solutions will be highlighted in yellow until the next
command is given.

### History

There is a history feature that allows the user to step back and forth through the rules and commands that have been applies. The history can be pruned i.e. all of the commands below the cursor deleted, or a single command can be deleted. Also history can be changed by moving to that point and injecting new rules.

### Speculative Solutions

The user can test an hypothesis by adding a speculative solution. This is done by right clicking on a cell and then choosing a value. The cell will be colored blue and the speculative solution added to the history. If the solution is incorrect then applying subsequent rules may lead to an error which will be noted with a red colored cell. The user can then step back through the history and try a different solution.

### Add or Delete Puzzles

Clicking the Add Puzzle button will allow you to add, delete and load new puzzles.

