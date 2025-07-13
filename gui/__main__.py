# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]

import sys
from PyQt5.QtWidgets import QApplication
from .nonogram_gui import NonogramGUI
# from .benchmark import benchmark_taai11, analyze_taai11, benchmark_pbn, analyze_pbn
import sys

app = QApplication(sys.argv)
window = NonogramGUI(sys.argv)

window.setFocus()
if not window.solved_on_start:
    window.set_status("Ready.")

window.show()
sys.exit(app.exec_())

# analyze_taai11()
# benchmark_taai11("copris_aot")
# benchmark_taai11("copris")
# benchmark_taai11("symbolic-block-start")
# benchmark_taai11("nonogrid")
# benchmark_taai11("sbs-improved")
# benchmark_taai11("pbnsolve")
# benchmark_taai11("bgu_aot")
# benchmark_taai11("bgu")
# benchmark_taai11("brute-force")

# analyze_pbn()
# benchmark_pbn("nonogrid")
# benchmark_pbn("sbs-improved")
# benchmark_pbn("pbnsolve")
# benchmark_pbn("bgu_aot")
# benchmark_pbn("bgu")
# benchmark_pbn("copris_aot")
# benchmark_pbn("copris")
# benchmark_pbn("symbolic-block-start")
# benchmark_pbn("brute-force")