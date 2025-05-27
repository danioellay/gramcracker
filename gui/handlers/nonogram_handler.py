# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *

class NonogramHandler:
    def __init__(self):
        self.loaded_nonogram = Nonogram(4,4, [], [])
    def load_file(self, filename: str) -> None:
        self.loaded_nonogram_filename = filename
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        #TODO: check which file ending the filename has and switch between parsers

        width, height = 0, 0
        row_hints = [[] for _ in range(height)]
        col_hints = [[] for _ in range(width)]

        for line in lines:
            line = line.strip()
            if line.startswith('#const w ='):
                width = int(line.split('=')[1].strip().split('.', 1)[0])
                row_hints = [[] for _ in range(height if height else width)]
            elif line.startswith('#const h ='):
                height = int(line.split('=')[1].strip().split('.', 1)[0])
                row_hints = [[] for _ in range(height)]
                col_hints = [[] for _ in range(width)]
            elif line.startswith('row_hint('):
                parts = line.split('(')[1].split(')')[0].split(',')
                row, hint_index, block_length = map(int, parts)
                while len(row_hints) <= row - 1:
                    row_hints.append([])
                while len(row_hints[row - 1]) <= hint_index - 1:
                    row_hints[row - 1].append(0)
                row_hints[row - 1][hint_index - 1] = block_length
            elif line.startswith('col_hint('):
                parts = line.split('(')[1].split(')')[0].split(',')
                col, hint_index, block_length = map(int, parts)
                while len(col_hints) <= col - 1:
                    col_hints.append([])
                while len(col_hints[col - 1]) <= hint_index - 1:
                    col_hints[col - 1].append(0)
                col_hints[col - 1][hint_index - 1] = block_length

        self.loaded_nonogram = Nonogram(width, height, row_hints, col_hints)

    def hints_from_grid(self, grid: List[List[bool]]):
        
        def get_hints(line):
            hints = []
            current = 0
            for cell in line:
                if cell:
                    current += 1
                else:
                    if current > 0:
                        hints.append(current)
                        current = 0
            if current > 0:
                hints.append(current)

            return hints if hints else [0]
        
        # Compute row hints
        self.loaded_nonogram.row_hints = []
        for i in range(self.loaded_nonogram.height):
            hints = get_hints(grid[i])
            self.loaded_nonogram.row_hints.append(hints)
            
        # Compute column hints
        self.loaded_nonogram.col_hints = []
        for j in range(self.loaded_nonogram.width):
            column = [grid[i][j] for i in range(self.loaded_nonogram.height)]
            hints = get_hints(column)
            self.loaded_nonogram.col_hints.append(hints)

    def clear_hints(self):
        self.loaded_nonogram.col_hints = [[0] for _ in range(self.loaded_nonogram.width)]
        self.loaded_nonogram.row_hints = [[0] for _ in range(self.loaded_nonogram.height)]

    def resize(self, width: int, height: int):
        self.loaded_nonogram.width = width
        self.loaded_nonogram.height = height

    def save_file(self, path: str = ""):
        if path == "":
            path = self.loaded_nonogram_filename
        nonogram = self.get_nonogram()
        with open(path, 'w') as f:
            f.write(f"%%% ASP Nonogram solver\n")
            f.write(f"%%% Problem Instance encoding\n")
            f.write(f"%%% {nonogram.width}x{nonogram.height} Nonogram\n")
            f.write(f"#const w = {nonogram.width}.  % Size of the Nonogram (w x h bw image)\n")
            f.write(f"#const h = {nonogram.height}.\n\n")
            f.write(f"% Hints for rows\n")
            f.write(f"% Format: row_hint(Row, HintIndex, BlockLength)\n")
            for row_num, hints in enumerate(nonogram.row_hints, start=1):
                for idx, length in enumerate(hints, start=1):
                    f.write(f"row_hint({row_num}, {idx}, {length}).\n")
            f.write("\n% Hints for columns\n")
            f.write("% Format: col_hint(Column, HintIndex, BlockLength)\n")
            for col_num, hints in enumerate(nonogram.col_hints, start=1):
                for idx, length in enumerate(hints, start=1):
                    f.write(f"col_hint({col_num}, {idx}, {length}).\n")

    def get_nonogram(self) -> Nonogram:
        return self.loaded_nonogram

    def solve(self):
        pass
        #TODO