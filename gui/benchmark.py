from .common import *
from .handlers.solution_handler import SolutionHandler
from .handlers.nonogram_handler import NonogramHandler

import time
from os import listdir
from os.path import isfile, join

def parse_nonogram_file(file_path: str) -> List[Nonogram]:
    with open(file_path, 'r') as file:
        content = file.read().splitlines()

    nonograms = []
    i = 0
    while i < len(content):
        line = content[i]
        if line.startswith('$'):
            # Found a new nonogram, parse it
            nonogram = Nonogram()
            nonogram.width = 25
            nonogram.height = 25

            # Skip the '$' line, next 25 lines are row hints
            i += 1
            for _ in range(25):
                if i >= len(content):
                    break
                hints = list(map(int, content[i].split()))
                nonogram.row_hints.append(LineHint(hints))
                i += 1

            # Next 25 lines are column hints
            for _ in range(25):
                if i >= len(content):
                    break
                hints = list(map(int, content[i].split()))
                nonogram.col_hints.append(LineHint(hints))
                i += 1
                
            assert(nonogram.width == 25)
            assert(nonogram.height == 25)
            assert(len(nonogram.row_hints) == 25)
            assert(len(nonogram.col_hints) == 25)

            nonograms.append(nonogram)
            # print(line)
        else:
            i += 1

    return nonograms

def parse_all_files(file_paths: List[str]) -> List[Nonogram]:
    all_nonograms = []
    for file_path in file_paths:
        all_nonograms.extend(parse_nonogram_file(file_path))
    return all_nonograms


def benchmark_taai11(solver_name):
    print("benchmarking", solver_name)
    file_paths = ['../taai11-1.txt', '../taai11-2.txt', '../taai11-3.txt']
    # file_paths = ['../taai11-rand.txt']
    nonograms = parse_all_files(file_paths)
    print(f"loaded {len(nonograms)} nonograms")
    solver = SolutionHandler()
    solver.set_timeout(60.0)
    start_time = time.time()
    # with open(f"report/data/benchmark_taai11-rand-{solver_name}.txt", 'w') as f:
    with open(f"report/data/benchmark_taai11-300-{solver_name}.txt", 'w') as f:
        for i, nonogram in enumerate(nonograms):
            solver.give_nonogram(nonogram)
            res, t = solver.run_solver(solver_name)
            # if t < 300.0:
            print(f"nonogram {i}: {t}")
            f.write(f"{t}\n")
            f.flush()
            # else:
            #     f.write("0\n")
    end_time = time.time()
    print(f"total time: {end_time-start_time}")
    
def analyze_taai11(): 
    file_paths = ['../taai11-1.txt', '../taai11-2.txt', '../taai11-3.txt']
    # file_paths = ['../taai11-rand.txt']
    nonograms = parse_all_files(file_paths)
    print(f"loaded {len(nonograms)} nonograms")
    with open(f"report/data/taai11-300.txt", 'w') as f:
        for i, nonogram in enumerate(nonograms):
            width = nonogram.width
            height = nonogram.height
            rowsum = sum(sum(hint) for hint in nonogram.row_hints)
            colsum = sum(sum(hint) for hint in nonogram.col_hints)
            numrh = sum(len(hint) for hint in nonogram.row_hints)
            numch = sum(len(hint) for hint in nonogram.col_hints)
            assert(width==25 and height==25)
            assert(rowsum==colsum)
            f.write(f"{i+1}, {width}, {height}, {rowsum}, {numrh}, {numch}\n")
            
def benchmark_pbn(solver_name):
    print("benchmarking", solver_name)
    datafiles = [f for f in listdir("../pbn/") if isfile(join("../pbn/", f)) and f.endswith(".nin")]
    datafiles.sort()
    nono_handler = NonogramHandler()
    soln_handler = SolutionHandler()
    soln_handler.set_timeout(1000.0)
    with open(f"report/data/benchmark_pbn-{solver_name}.txt", 'w') as f:
        for i, file in enumerate(datafiles):
            print(file)
            nono_handler.load_file(join("../pbn/", file))
            soln_handler.give_nonogram(nono_handler.get_curr_nonogram())
            res, t = soln_handler.run_solver(solver_name)
            f.write(f"{t}\n")
            f.flush()
            
def analyze_pbn():
    datafiles = [f for f in listdir("../pbn/") if isfile(join("../pbn/", f)) and f.endswith(".nin")]
    datafiles.sort()
    nono_handler = NonogramHandler()
    with open(f"report/data/pbn.txt", 'w') as f:
        for i, file in enumerate(datafiles):
            print(file)
            nono_handler.load_file(join("../pbn/", file))
            nonogram = nono_handler.get_curr_nonogram()
            width = nonogram.width
            height = nonogram.height
            rowsum = sum(sum(hint) for hint in nonogram.row_hints)
            colsum = sum(sum(hint) for hint in nonogram.col_hints)
            numrh = sum(len(hint) for hint in nonogram.row_hints)
            numch = sum(len(hint) for hint in nonogram.col_hints)
            # assert(width==25 and height==25)
            assert(rowsum==colsum)
            f.write(f"{i+1}, {width}, {height}, {rowsum}, {numrh}, {numch}\n")
            # f.flush()