# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import subprocess, os
import time
from copy import deepcopy
from typing import List, Tuple


class SolutionHandler:
    def __init__(self):
        """Init a handler that can be given nonograms to solve"""
        self.given_nonogram: Nonogram
        self.solutions: List[NonogramSoln] = []
        self.curr_soln_idx: int = -1 # == -1 if in working solution
        self.working_soln: NonogramSoln
        self.timeout: float = 1.0
        self.found_all = False

    def give_nonogram(self, nonogram: Nonogram) -> None:
        """Give a reference to a nonogram that will be solved when run_solver is called"""
        self.given_nonogram = nonogram
        self.curr_soln_idx = -1
        self.solutions = []
        self.working_soln = NonogramSoln(nonogram)

    def set_timeout(self, t: float) -> None:
        """Set the maximum time the solver can take before aborting"""
        self.timeout = t

    def get_curr_soln(self) -> NonogramSoln:
        """Get the currently selected solution; use use_working_soln, next_soln or prev_soln methods to switch between solution"""
        if self.curr_soln_idx < 0:
            return self.working_soln
        return self.solutions[self.curr_soln_idx]
    
    def use_working_soln(self):
        """Create a copy of the current solution to make it available for editing"""
        self.working_soln = deepcopy(self.get_curr_soln())
        self.curr_soln_idx = -1

    def next_soln(self):
        """Switch to the next solution the solver found (wraps around)"""
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx += 1
        if self.curr_soln_idx >= len(self.solutions):
            self.curr_soln_idx = 0

    def prev_soln(self):
        """Switch to the previous solution the solver found (wraps around)"""
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx -= 1
        if self.curr_soln_idx < 0:
            self.curr_soln_idx = len(self.solutions) - 1

    def get_cautious_pixels(self) -> np.ndarray:
        """Find all solutions if not done already and return the coordinates of the pixels that are filled in every solution"""
        if not self.found_all:
            # If we did not find all solutions previously, do it now
            self.run_solver_auto(True, True)

        grids = [solution.grid for solution in self.solutions]
        stacked_grids = np.stack(grids, axis=0)
        common_grid = np.logical_and.reduce(stacked_grids, axis=0)
        return common_grid
    
    def run_solver_auto(self, check_unique: bool = True, all_models: bool = False) -> Tuple[str, float]:
        """Auto-select the best solver and run it"""
        return self.run_solver("sbs-improved", check_unique, all_models)
    
    def run_nonogrid_solver(self, check_unique: bool = True, all_models: bool = False) -> Tuple[str, float]:
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
        try:
            result = subprocess.run(["./nonogrid/target/release/nonogrid",  "nono.temp"] + args, stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
        except:
            return "Timed out", self.timeout + 1.0

        end_time = time.time()

        os.remove("nono.temp")
        result = result.stdout.decode('utf-8')

        self.solutions = []
        if "?" in result:
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
        return res, end_time-start_time
    
    def run_pbn_solver(self, check_unique: bool = True, all_models: bool = False) -> Tuple[str, float]:
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
        try:
            result = subprocess.run(["./pbnsolve/pbnsolve",  "nono.temp"] + args, stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
        except:
            return "Timed out", self.timeout + 1.0
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
            grid_lines = lines[1:]
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
        print(res)
        return res, end_time-start_time
        
    def run_bgu_solver(self, check_unique: bool = True, all_models: bool = False, use_aot: bool = False) -> Tuple[str, float]:
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
        try:
            if use_aot:
                result = subprocess.run(["./solvers/bgu-aot", "-file", "nono.temp"] + args , stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
                # result = subprocess.run(["./solvers/bgu-aot", "-file", "nono.temp"] + args, stdout=subprocess.PIPE)
            else:
                result = subprocess.run(["java", "-jar", "solvers/bgusolver_cmd_102.jar", "-file", "nono.temp"] + args, stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
                # result = subprocess.run(["java", "-jar", "solvers/bgusolver_cmd_102.jar", "-file", "nono.temp"] + args, stdout=subprocess.PIPE)
        except:
            return "Timed out", self.timeout + 1.0

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

        res = f"Solver 'bgu{"_aot" if use_aot else ""}' took {format_time(end_time-start_time)} to find "
        if len(self.solutions) == 0:
            res += "no solutions"
        elif check_unique and len(self.solutions) == 1:
            res += "a unique solution"
        elif all_models:
            res += f"{len(self.solutions)} solutions"
        else:
            res += f"{len(self.solutions)}+ solutions"
        
        print(res)
        return res, end_time-start_time
    
    def run_copris_solver(self, check_unique: bool = True, all_models: bool = False, use_aot = False) -> Tuple[str, float]:
        with open("nono.temp", 'w') as f:
            nonogram = self.given_nonogram
            f.write(f"{nonogram.height}\n{nonogram.width}\n")
            for hints in nonogram.row_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
            f.write("#\n")
            for hints in nonogram.col_hints:
                for l in hints:
                    f.write(str(l) + ' ')
                f.write("\n")
        
        start_time = time.time()
        # result = subprocess.run(["java", "-jar", "-Xmx2048m", "../copris-nonogram-v1-2/target/scala-2.10/copris-nonogram-assembly-1.2.jar", "-s1", "clasp", "nono.temp"], stdout=subprocess.PIPE)
        # result = subprocess.run(["../copris/copris", "nono.temp"], stdout=subprocess.PIPE)
        try:
            if use_aot:
                result = subprocess.run(["./copris/copris-aot", "-s1", "clasp", "nono.temp"], stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
                # result = subprocess.run(["./copris/copris-aot", "-s1", "clasp", "nono.temp"], stdout=subprocess.PIPE)
            else:
                result = subprocess.run(["scala", "-cp", "solvers/copris-puzzles-2.0.jar", "nonogram.Solver", "-s1", "clasp", "nono.temp"], stdout=subprocess.PIPE, timeout=self.timeout if self.timeout < float('inf') else None)
                # result = subprocess.run(["scala", "-cp", "solvers/copris-puzzles-2.0.jar", "nonogram.Solver", "-s1", "clasp", "nono.temp"], stdout=subprocess.PIPE)
        except:
            return "Timed out", self.timeout + 1.0
        end_time = time.time()

        os.remove("nono.temp")
        result = result.stdout.decode('utf-8')
        self.solutions = []
        # print(result)
        if "Unique solution" in result:
            self.solutions = [NonogramSoln(self.given_nonogram)]
        elif "Multiple solutions" in result:
            self.solutions = [NonogramSoln(self.given_nonogram), NonogramSoln(self.given_nonogram)]
        else:
            self.solutions = []

        if self.solutions:
            lines = [line for line in result.split('\n')]
            grid_lines = [line for line in lines if '#' in line or '.' in line]
            for i, line in enumerate(grid_lines):
                for j in range(len(line)):
                    self.solutions[0].grid[i, j] = line[j] == '#'
            self.curr_soln_idx = 0

        res = f"Solver 'copris{"_aot" if use_aot else ""}' took {format_time(end_time-start_time)} to find "
        if len(self.solutions) == 0:
            res += "no solutions"
        elif check_unique and len(self.solutions) == 1:
            res += "a unique solution"
        elif len(self.solutions) > 1:
            res += "a non-unique solution"
        else:
            res += "a solution"
        
        print(res)
        return res, end_time-start_time

    def run_solver(self, solver_path: str, check_unique: bool = True, all_models: bool = False) -> Tuple[str, float]:
        """Run the logic program at the given path, assume it is a nonogram solver and try to find one/two models, depending on the check_unique flag"""
        if not self.given_nonogram:
            print("Error: No nonogram to solve")
            self.curr_soln_idx = 0
            self.solutions = []
            return "Error: No nonogram to solve", -1.0
        
        if solver_path == "nonogrid":
            return self.run_nonogrid_solver(check_unique, all_models)
        if solver_path == "pbnsolve":
            return self.run_pbn_solver(check_unique, all_models)
        if solver_path == "copris":
            return self.run_copris_solver(check_unique, all_models)
        if solver_path == "copris_aot":
            return self.run_copris_solver(check_unique, all_models, True)
        if solver_path == "bgu":
            return self.run_bgu_solver(check_unique, all_models)
        if solver_path == "bgu_aot":
            return self.run_bgu_solver(check_unique, all_models, True)

        # Initialize the clingo control and give the dimensional constants
        num = 1
        if check_unique:
            num = 2
        if all_models:
            num = 0
        ctl = Control([f"{num}", 
                       "-c", f"w={self.given_nonogram.width}", 
                       "-c", f"h={self.given_nonogram.height}"])

        # Add the hint predicates to the base program
        for row_index, row in enumerate(self.given_nonogram.row_hints):
            for hint_index, hint_length in enumerate(row):
                ctl.add(f"row_hint({row_index+1},{hint_index+1},{hint_length}).")
        for col_index, col in enumerate(self.given_nonogram.col_hints):
            for hint_index, hint_length in enumerate(col):
                ctl.add(f"col_hint({col_index+1},{hint_index+1},{hint_length}).")
        
        # Load the solver file and ground the program
        ctl.load("solvers/" + solver_path + ".lp")

        start_time = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time()

        # Find the models and track the computation times
        self.solutions.clear()
        self.curr_soln_idx = -1
        timed_out = False

        with ctl.solve(async_=True, on_model=self._on_model) as handle:
            while not handle.wait(1.0):
                if time.time() - ground_time > self.timeout:
                    handle.cancel()
                    timed_out = True
                    break

        # Find the models and track the computation times
        self.solutions.clear()
        self.curr_soln_idx = -1
        timed_out = False

        with ctl.solve(async_=True, on_model=self._on_model) as handle:
            while not handle.wait(1.0):
                if time.time() - ground_time > self.timeout:
                    handle.cancel()
                    timed_out = True
                    break

        end_time = time.time()

        if self.solutions:
            self.curr_soln_idx = 0

        if all_models:
            self.found_all = True
        else:
            self.found_all = False

        # Status bar output
        form_time = format_time(end_time - start_time)
        self.res = ""

        if not self.solutions:
            self.res = f"Solver '{solver_path}' found no solutions after {form_time}"
        form_time = format_time(end_time - start_time)
        self.res = ""

        if not self.solutions:
            self.res = f"Solver '{solver_path}' found no solutions after {form_time}"

        elif not check_unique:
            self.res = f"Solver '{solver_path}' found a solution after {form_time}"
        elif check_unique and not all_models:
            if len(self.solutions) == 1:
                self.res = f"Solver '{solver_path}' took {form_time} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {form_time} to find two distinct solutions (more may exist)"
        elif check_unique and all_models:
            if len(self.solutions) == 1:
                self.res = f"Solver '{solver_path}' took {form_time} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {form_time} to find {"all" if not timed_out else ""} {len(self.solutions)} solutions"

        if timed_out:
            self.res += " (timeout)"

        print(self.res + ":")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        # if check_unique:
        #     print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        # if all_models and len(self.solutions) > 1:
        #     print(f"\tAll Solutions: {format_time(all_time - unique_time)}")
        # if check_unique:
        #     print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        # if all_models and len(self.solutions) > 1:
        #     print(f"\tAll Solutions: {format_time(all_time - unique_time)}")
        
        return self.res, end_time - start_time
    
    def _on_model(self, model: Model) -> None:
        """Clingo 'model found' callback to convert the model into a NonogramSoln and store it"""
        soln = NonogramSoln(self.given_nonogram)
        soln.fill_from_model(model)
        self.solutions.append(soln)

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
        """Which row hints are satisfied?"""
        if not self.given_nonogram:
            return []
        
        row_hint = self.given_nonogram.row_hints[row]
        return self.get_curr_soln().row_matches_hint_partial(row, row_hint)

    def solves_col_partial(self, col: int) -> List[int]:
        """Which column hints are satisfied?"""
        if not self.given_nonogram:
            return []
        
        col_hint = self.given_nonogram.col_hints[col]
        return self.get_curr_soln().col_matches_hint_partial(col, col_hint)