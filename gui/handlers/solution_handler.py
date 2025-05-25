from gui.common import *
from clingo import Control

class SolutionHandler:
    def __init__(self):
        pass

    def give_nonogram(self, nonogram: Nonogram):
        self.given_nonogram = nonogram
        self.working_solution = NonogramSoln(nonogram)