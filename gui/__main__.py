# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]

from .nonogram_gui import NonogramGUI
import sys

app = NonogramGUI(sys.argv)
app.run()