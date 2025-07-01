# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from dataclasses import dataclass
from typing import List
from clingo import Model

@dataclass
class Nonogram:
    width : int
    height: int
    row_hints: List[List[int]]
    col_hints: List[List[int]]
    #colors: int = 1 #number of colors besides the background color (white)


@dataclass
class NonogramSoln:
    fill: List[List[bool]]

    def __init__(self, nonogram: Nonogram):
        self.fill = [[False for _ in range(nonogram.width)] for _ in range(nonogram.height)]

    def fill_from_model(self, model: Model | None):
        if not model:
            return
        
        for row in self.fill:
            for cell in row:
                cell = False
        
        for symbol in model.symbols(atoms=True):
            if symbol.name == 'fill':
                self.fill[symbol.arguments[0].number - 1][symbol.arguments[1].number - 1] = True


def check_line(line: List[bool], hints: List[int]) -> bool:
    hint_index = 0
    i = 0
    n = len(line)

    while i < n and hint_index < len(hints):
        # Skip unfilled cells
        while i < n and not line[i]:
            i += 1

        # Check if there are enough cells left for the current hint
        if i + hints[hint_index] > n:
            return False

        # Check if the next cells are filled to match the hint
        for j in range(hints[hint_index]):
            if not line[i + j]:
                return False

        # Move past the current block
        i += hints[hint_index]

        # Check if the block is followed by at least one unfilled cell
        if i < n and line[i]:
            return False

        # Move to the next hint
        hint_index += 1

    # Ensure there are no remaining filled cells
    while i < n:
        if line[i]:
            return False
        i += 1

    # Ensure all hints have been processed
    return hint_index == len(hints)

def format_time(t: float) -> str:
    if t > 60.0*60.0:
        return f"{t/(60.0*60.0):.2f}h"
    if t > 60.0:
        return f"{t/60.0:.2f}min"
    if t > 1.0:
        return f"{t:.2f}s"
    if t > 0.001:
        return f"{t*1.0e3:.2f}ms"
    return f"{t*1.0e6:.2f}μs"
