# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import subprocess, os
import time
from copy import deepcopy

class SolutionHandler:
    def __init__(self):
        self.given_nonogram: Nonogram
        self.solutions: List[NonogramSoln] = []
        self.curr_soln_idx: int = -1 # == -1 if in working solution
        self.working_soln: NonogramSoln

    def give_nonogram(self, nonogram: Nonogram):
        """Give a reference to a nonogram that will be solved when run_solver is called"""
        self.given_nonogram = nonogram
        self.curr_soln_idx = -1
        self.solutions = []
        self.working_soln = NonogramSoln(nonogram)

    def get_curr_soln(self) -> NonogramSoln:
        if self.curr_soln_idx < 0:
            return self.working_soln
        return self.solutions[self.curr_soln_idx]
    
    def use_working_soln(self):
        self.working_soln = deepcopy(self.get_curr_soln())
        self.curr_soln_idx = -1

    def run_nonogrid_solver(self, check_unique: bool = True, all_models: bool = False) -> str:
        with open("nono.temp", 'w') as f:
            nonogram = self.given_nonogram
            for hints in nonogram.row_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
            f.write("\n")
            for hints in nonogram.col_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")

        args = []
        if check_unique and not all_models:
            args = ["-m", "2"]
        elif not check_unique:
            args = ["-m", "1"]

        start_time = time.time()
        result = subprocess.run(["./nonogrid/target/release/nonogrid",  "nono.temp"] + args, stdout=subprocess.PIPE)
        end_time = time.time()

        os.remove("nono.temp")
        result = result.stdout.decode('utf-8')

        self.solutions = []
        if "Backtracking found" in result:
            # Multiple solutions case
            lines = result.split('\n')
            i = 0
            n = len(lines)
            while i < n:
                if lines[i].endswith("solution:"):
                    i += 1  # move to the first grid line
                    grid_lines = []
                    while i < n and lines[i].strip() and all(c in {'■', '.'} for c in lines[i].strip()):
                        grid_lines.append(lines[i].strip())
                        i += 1
                    if grid_lines:
                        height = len(grid_lines)
                        width = len(grid_lines[0]) if height > 0 else 0
                        soln = NonogramSoln(self.given_nonogram)
                        for y in range(height):
                            for x in range(width):
                                c = grid_lines[y][x]
                                soln.grid[y, x] = (c == '■')
                        self.solutions.append(soln)
                else:
                    i += 1
        else:
            # Unique solution case
            lines = result.split('\n')
            grid_lines = []
            for line in lines:
                if line.startswith('#'):
                    continue
                line = line.strip()
                if not line:
                    continue
                tokens = line.split()
                if not tokens:
                    continue
                tokens = [token[-1] for token in tokens]
                # Find the first non-digit token
                hint_end = 0
                for i, token in enumerate(tokens):
                    if not token.isdigit():
                        hint_end = i
                        break
                if hint_end == 0 and all(token.isdigit() for token in tokens):
                    continue  # skip lines that are only hints (no grid cells)
                grid_cells = tokens[hint_end:]
                if grid_cells:
                    grid_lines.append(grid_cells)
            if grid_lines:
                height = len(grid_lines)
                width = max(len(cells) for cells in grid_lines) if height > 0 else 0
                soln = NonogramSoln(self.given_nonogram)
                for y in range(height):
                    row_cells = grid_lines[y]
                    for x in range(width):
                        if x < len(row_cells):
                            c = row_cells[x]
                            soln.grid[y, x] = (c == '■')
                        else:
                            soln.grid[y, x] = False  # treat missing cells as empty
                self.solutions.append(soln)
        if self.solutions:
            self.curr_soln_idx = 0
        
        res = f"Solver 'nonogrid' took {format_time(end_time-start_time)} to find "
        if len(self.solutions) == 0:
            res += "no solutions"
        elif check_unique and len(self.solutions) == 1:
            res += "a unique solution"
        elif all_models:
            res += f"{len(self.solutions)} solutions"
        else:
            res += f"{len(self.solutions)}+ solutions"
        
        print(res)
        return res
    
    def run_pbn_solver(self, check_unique: bool = True, all_models: bool = False) -> str:
        with open("nono.temp", 'w') as f:
            nonogram = self.given_nonogram
            f.write(f"{nonogram.height} {nonogram.width}\n")
            for hints in nonogram.row_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
            f.write("#\n")
            for hints in nonogram.col_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
        args = []
        if check_unique:
            args = ["-u"]
        # if all_models:
            # Not supported?
        
        start_time = time.time()
        result = subprocess.run(["./../pbnsolve-1.09/pbnsolve",  "nono.temp"] + args, stdout=subprocess.PIPE)
        end_time = time.time()

        os.remove("nono.temp")
        result = result.stdout.decode('utf-8')
        self.solutions = []
        lines = [line.strip() for line in result.split('\n') if line.strip()]

        def parse_grid(grid_lines: List[str], nonogram: Nonogram):
            if len(grid_lines) != nonogram.height:
                raise ValueError(f"Expected {nonogram.height} lines, got {len(grid_lines)}")
            grid = []
            for line in grid_lines:
                if len(line) != nonogram.width:
                    raise ValueError(f"Expected line length {nonogram.width}, got {len(line)}")
                row = []
                for c in line:
                    if c == 'X':
                        row.append(True)
                    else:  # assuming '.'
                        row.append(False)
                grid.append(row)
            return grid

        def fill_grid(soln: NonogramSoln, grid: List[List[bool]]):
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    soln.grid[i, j] = grid[i][j]

        if lines[0].startswith("FOUND MULTIPLE SOLUTIONS:"):
            grid_lines = []
            for line in lines[1:]:
                if line.startswith("ALTERNATE SOLUTION"):
                    if grid_lines:
                        grid = parse_grid(grid_lines, self.given_nonogram)
                        soln = NonogramSoln(self.given_nonogram)
                        fill_grid(soln, grid)
                        self.solutions.append(soln)
                        grid_lines = []
                else:
                    grid_lines.append(line)
            # Add the last grid
            if grid_lines:
                grid = parse_grid(grid_lines, self.given_nonogram)
                soln = NonogramSoln(self.given_nonogram)
                fill_grid(soln, grid)
                self.solutions.append(soln)
        elif lines[0].startswith("UNIQUE") or lines[0].startswith("STOPPED"):
            soln = NonogramSoln(self.given_nonogram)
            print(lines)
            grid_lines = lines[1:]
            print(grid_lines)
            if grid_lines:
                grid = parse_grid(grid_lines, self.given_nonogram)
                fill_grid(soln, grid)
                self.solutions = [soln]

        if self.solutions:
            self.curr_soln_idx = 0

        res = f"Solver 'pbnsolve' took {format_time(end_time-start_time)} to find "
        if len(self.solutions) == 0:
            res += "no solutions"
        elif check_unique and len(self.solutions) == 1:
            res += "a unique solution"
        else:
            res += f"{len(self.solutions)}+ solutions"
            if all_models:
                res += " (finding all not supported)"
        print(res)
        return res
        
    def run_bgu_solver(self, check_unique: bool = True, all_models: bool = False) -> str:
        with open("nono.temp", 'w') as f:
            nonogram = self.given_nonogram
            f.write(f"{nonogram.height} {nonogram.width}\n")
            for hints in nonogram.row_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
            # f.write("#\n")
            for hints in nonogram.col_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
                
        if not check_unique and not all_models:
            args = ["-maxsolutions", "1"]
        elif check_unique and not all_models:
            args = ["-maxsolutions", "2"]
        else:
            args = ["-maxsolutions", "0"]
        
        start_time = time.time()
        result = subprocess.run(["java", "-jar", "./../bgusolver_cmd_102.jar", "-file", "nono.temp"] + args, stdout=subprocess.PIPE)
        end_time = time.time()

        os.remove("nono.temp")
        result = result.stdout.decode('utf-8')
        self.solutions = []
        # print(result)
        lines = [line for line in result.split('\n')]
        grid_lines = []
        for line in lines:
            if line.startswith("Solutions :"):
                num = int(line.split()[-1])
                for _ in range(num):
                    self.solutions.append(NonogramSoln(self.given_nonogram))
            elif '#' in line:
                grid_lines.append(line)
        if self.solutions:
            for i, line in enumerate(grid_lines):
                for j in range(len(line)):
                    self.solutions[0].grid[i, j] = line[j] == '#'
            self.curr_soln_idx = 0

        res = f"Solver 'bgu' took {format_time(end_time-start_time)} to find "
        if len(self.solutions) == 0:
            res += "no solutions"
        elif check_unique and len(self.solutions) == 1:
            res += "a unique solution"
        elif all_models:
            res += f"{len(self.solutions)} solutions"
        else:
            res += f"{len(self.solutions)}+ solutions"
        
        print(res)
        return res

    def run_solver(self, solver_path: str, check_unique: bool = True, all_models: bool = False) -> str:
        """Run the logic program at the given path, assume it is a nonogram solver and try to find one/two models, depending on the check_unique flag"""
        if not self.given_nonogram:
            print("Error: No nonogram to solve")
            self.curr_soln_idx = 0
            self.solutions = []
            return "Error: No nonogram to solve"
        
        if solver_path == "nonogrid":
            return self.run_nonogrid_solver(check_unique, all_models)
        if solver_path == "pbnsolve":
            return self.run_pbn_solver(check_unique, all_models)
        if solver_path == "bgu":
            return self.run_bgu_solver(check_unique, all_models)

        # Initialize the clingo control and give the dimensional constants
        ctl = Control([f"{0 if check_unique else 1}", 
                       "-c", f"w={self.given_nonogram.width}", 
                       "-c", f"h={self.given_nonogram.height}"])

        # Add the hint predicates to the base program
        for row_index, row in enumerate(self.given_nonogram.row_hints):
            for hint_index, hint_length in enumerate(row):
                ctl.add(f"row_hint({row_index+1},{hint_index+1},{hint_length}).")
        for col_index, col in enumerate(self.given_nonogram.col_hints):
            for hint_index, hint_length in enumerate(col):
                ctl.add(f"col_hint({col_index+1},{hint_index+1},{hint_length}).")
        
        # Load the solver file
        ctl.load("solvers/" + solver_path + ".lp")

        # Find the first model and track the computation times
        start_time = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time()

        handler = ctl.solve(yield_=True)
        model1 = handler.model()
        end_time = time.time()

        if model1:
            soln = NonogramSoln(self.given_nonogram)
            soln.fill_from_model(model1)
            self.solutions = [soln]
            self.curr_soln_idx = 0

        model2 = None
        unique_time = end_time
        # If checking uniqueness, try to find a second model
        if model1 and check_unique:
            handler.resume()
            model2 = handler.model()
            unique_time = time.time()

            if model2:
                soln = NonogramSoln(self.given_nonogram)
                soln.fill_from_model(model1)
                self.solutions.append(soln)

        all_time = end_time
        # If trying to find all solutions, keep going
        if model2 and check_unique and all_models:
            while True:
                # print(f"looking for model nr {len(self.solutions) + 1}...")
                handler.resume()
                next_model = handler.model()
                if next_model:
                    # print(f"found model nr {len(self.solutions) + 1}!")
                    next_soln = NonogramSoln(self.given_nonogram)
                    next_soln.fill_from_model(next_model)
                    self.solutions.append(next_soln)
                else:
                    # print(f"model nr {len(self.solutions) + 1} not found! Ending search...")
                    print()
                    break
                
            all_time = time.time()

        # Status bar output
        res = ""
        if not model1:
            res = f"Solver '{solver_path}' found no solutions after {format_time(end_time - start_time)}"

        elif not check_unique:
            res = f"Solver '{solver_path}' found a solution after {format_time(end_time - start_time)}"
        elif check_unique and not all_models:
            if not model2:
                res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find a unique solution"
            else:
                res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find at least two solutions"
        elif check_unique and all_models:
            if len(self.solutions) == 1:
                res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find a unique solution"
            else:
                res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find all {len(self.solutions)} solutions"

        print(res + ":")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        if check_unique:
            print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        if all_models and len(self.solutions) > 1:
            print(f"\tAll Solutions: {format_time(all_time - unique_time)}")
        
        return res
    
    def next_soln(self):
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx += 1
        if self.curr_soln_idx >= len(self.solutions):
            self.curr_soln_idx = 0

    def prev_soln(self):
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx -= 1
        if self.curr_soln_idx < 0:
            self.curr_soln_idx = len(self.solutions) - 1

    def solves_row(self, row: int) -> bool:
        """Does the current working solution match the hints in the specified row in the given nonogram?"""
        if not self.given_nonogram:
            return False
        
        row_hint = self.given_nonogram.row_hints[row]
        return self.get_curr_soln().row_matches_hint(row, row_hint)

    def solves_col(self, col: int) -> bool:
        """Does the current working solution match the hints in the specified column in the given nonogram?"""
        if not self.given_nonogram:
            return False
        
        col_hint = self.given_nonogram.col_hints[col]
        return self.get_curr_soln().col_matches_hint(col, col_hint)
    
    def solves_row_partial(self, row: int) -> List[int]:
        if not self.given_nonogram:
            return []
        
        row_hint = self.given_nonogram.row_hints[row]
        return self.get_curr_soln().row_matches_hint_partial(row, row_hint)

    def solves_col_partial(self, col: int) -> List[int]:
        if not self.given_nonogram:
            return []
        
        col_hint = self.given_nonogram.col_hints[col]
        return self.get_curr_soln().col_matches_hint_partial(col, col_hint)