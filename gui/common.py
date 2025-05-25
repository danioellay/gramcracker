
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