# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]

import sys
from PyQt5.QtWidgets import QApplication
from .nonogram_gui import NonogramGUI

app = QApplication(sys.argv)
window = NonogramGUI(sys.argv)

window.setFocus()
if not window.solved_on_start:
    window.set_status("Ready.")

window.show()
sys.exit(app.exec_())