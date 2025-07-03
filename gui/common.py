# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from dataclasses import dataclass
from typing import List, NewType, cast
from clingo import Model
import numpy as np

LineHint = NewType('LineHint', List[int])

# Line encoding function
def hint_from_line(line: np.ndarray) -> LineHint:
    hint = []
    current_block = 0
    for cell in line:
        if cell:
            current_block += 1
        else:
            if current_block > 0:
                hint.append(current_block)
                current_block = 0
    if current_block > 0:
        hint.append(current_block)
    
    # Use zero hints instead of empty hints
    if hint == []:
        hint = [0]
    
    return cast(LineHint, hint)


@dataclass
class Nonogram:
    width : int
    height: int
    row_hints: List[LineHint]
    col_hints: List[LineHint]
    #colors: int = 1 #number of colors besides the background color (white)

    def __init__(self):
        self.width = 0
        self.height = 0
        self.row_hints = []
        self.col_hints = []

    def init_from_grid(self, grid: np.ndarray):
        self.width = grid.shape[1]
        self.height = grid.shape[0]
        
        self.row_hints = []
        for row in grid:
            hint = hint_from_line(row)
            self.row_hints.append(cast(LineHint, hint))
        
        self.col_hints = []
        for i in range(grid.shape[1]):
            col = grid[:, i]
            hint = hint_from_line(col)
            self.col_hints.append(cast(LineHint, hint))


@dataclass
class NonogramSoln:
    # grid containing the solution: entry is 0 if background, 1 if black
    grid: np.ndarray
    def __init__(self, nonogram: Nonogram):
        self.grid = np.full((nonogram.height, nonogram.width), 0, dtype=np.bool)

    def fill_from_model(self, model: Model | None):
        if not model:
            return
        
        self.grid.fill(0)
        
        for symbol in model.symbols(atoms=True):
            if symbol.name == 'fill':
                self.grid[symbol.arguments[0].number - 1, symbol.arguments[1].number - 1] = 1

    def row_matches_hint(self, row_index: int, linehint: LineHint) -> bool:
        row = self.grid[row_index, :]
        generated_hint = hint_from_line(row)

        if linehint == [0] and generated_hint == [] \
            or generated_hint == [0] and linehint == []:
            return True
        
        return generated_hint == linehint
    
    def col_matches_hint(self, col_index: int, linehint: LineHint) -> bool:
        col = self.grid[:, col_index]
        generated_hint = hint_from_line(col)

        if linehint == [0] and generated_hint == [] \
            or generated_hint == [0] and linehint == []:
            return True
        
        return generated_hint == linehint
    
    def row_matches_hint_partial(self, row_index: int, linehint: LineHint) -> List[int]:
        row = self.grid[row_index, :]
        current_hint = hint_from_line(row)
        matched_indices = []

        if linehint == [0] and current_hint == [] \
            or current_hint == [0] and linehint == []:
            return [0]
        
        if linehint == current_hint:
           return [i for i in range(len(linehint))]
        
        for i in range(len(linehint)):
            if i < len(current_hint) and current_hint[i] == linehint[i]:
                matched_indices.append(i)
        return matched_indices

    def col_matches_hint_partial(self, col_index: int, linehint: LineHint) -> List[int]:
        col = self.grid[:, col_index]
        current_hint = hint_from_line(col)
        matched_indices = []
        
        if linehint == [0] and current_hint == [] \
            or current_hint == [0] and linehint == []:
            return [0]
        
        if linehint == current_hint:
           return [i for i in range(len(linehint))]
        
        for i in range(len(linehint)):
            if i < len(current_hint) and current_hint[i] == linehint[i]:
                matched_indices.append(i)
        return matched_indices

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
