from clingo import Control
from dataclasses import dataclass

@dataclass
class Nonogram:
    width: int
    height: int
    row_hints: list[list[int]]
    col_hints: list[list[int]]
    #colors: int = 1 #number of colors besides the background color (white)

@dataclass
class NonogramSoln:
    fill: list[list[bool]]

class NonogramHandler:
    def load_file(self, filename: str) -> None:
        self.loaded_nonogram_filename = filename
        with open(filename, 'r') as file:
            lines = file.readlines()

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
        self.solutions = [NonogramSoln([[False]*height]*width)]
        self.current_solution_idx = 0

    def save_file(self):
        pass
        #TODO

    def get_nonogram(self):
        return self.loaded_nonogram

    def solve(self):
        pass
        #TODO