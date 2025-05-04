# Random Nonogram generator
# Author: Fabian Kraus

# Run from project root with:
"""
python3 nonograms/generate-random.py & clingo nonograms/random.lp solvers/brute-force.lp
# or
python3 nonograms/generate-random.py & clinguin client-server --domain-files nonograms/random.lp solvers/brute-force.lp --ui-files solvers/nonogram-ui.lp
"""

# tweak parameters here:
SIZE = 20
BW_RATIO = 0.5 # (smaller value -> less black pixels)
FILE = "nonograms/random.lp"

import random

def generate_nonogram(n, ratio, output_filename):
    # generate pixel grid
    grid = [] 
    for _ in range(n): 
        row = [1 if random.random() < ratio else 0 for _ in range(n)] 
        grid.append(row)

    def get_hints(line):
        hints = []
        current = 0
        for cell in line:
            if cell == 1:
                current += 1
            else:
                if current > 0:
                    hints.append(current)
                    current = 0
        if current > 0:
            hints.append(current)
        return hints

    # Compute row hints
    row_hints = []
    for i in range(n):
        hints = get_hints(grid[i])
        row_hints.append( (i+1, hints) )  # rows are 1-based

    # Compute column hints
    col_hints = []
    for j in range(n):
        column = [grid[i][j] for i in range(n)]
        hints = get_hints(column)
        col_hints.append( (j+1, hints) )  # columns are 1-based

    # Write to file
    with open(output_filename, 'w') as f:
        f.write(f"%%% Generated Nonogram {n}x{n}\n")
        f.write(f"#const n = {n}.  % Size of the Nonogram (n x n bw image)\n\n")
        f.write("% Hints for rows\n")
        f.write("% Format: row_hint(Row, HintIndex, BlockLength)\n")
        for row_num, hints in row_hints:
            for idx, length in enumerate(hints, start=1):
                f.write(f"row_hint({row_num}, {idx}, {length}).\n")
        f.write("\n% Hints for columns\n")
        f.write("% Format: col_hint(Column, HintIndex, BlockLength)\n")
        for col_num, hints in col_hints:
            for idx, length in enumerate(hints, start=1):
                f.write(f"col_hint({col_num}, {idx}, {length}).\n") 

generate_nonogram(SIZE, BW_RATIO, FILE)
