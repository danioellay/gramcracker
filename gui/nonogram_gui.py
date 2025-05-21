from clingo import Control
import tkinter as tk

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class NonogramGUI(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.title("Nonogram GUI")
        self.protocol("WM_DELETE_WINDOW", self._on_del_window)
        self.protocol("tk::mac::Quit", self._on_del_window)

        # test
        c = Control()
        print("fsdf")

    def run(self) -> None:
        self.update()
        self.update_idletasks()
        self.focus_force()
        return self.mainloop()
    
    def _on_del_window(self) -> None:
        self.quit()