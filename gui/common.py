
from dataclasses import dataclass
from typing import List

@dataclass
class Nonogram:
    width: int
    height: int
    row_hints: List[List[int]]
    col_hints: List[List[int]]
    #colors: int = 1 #number of colors besides the background color (white)


@dataclass
class NonogramSoln:
    fill: List[List[bool]]

    def __init__(self, nonogram: Nonogram):
        self.fill = [[False for _ in range(nonogram.width)] for _ in range(nonogram.height)]