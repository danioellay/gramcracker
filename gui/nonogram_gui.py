import tkinter as tk

from .handlers.nonogram_handler import NonogramHandler

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1000

class NonogramGUI(tk.Tk):

    def __init__(self, args) -> None:
        tk.Tk.__init__(self)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.title("Nonogram GUI")
        self.protocol("WM_DELETE_WINDOW", self._on_del_window)
        self.protocol("tk::mac::Quit", self._on_del_window)

        self.nonogram_handler = NonogramHandler()
        if len(args) > 1:
            self.nonogram_handler.load_file(args[1])

    def run(self) -> None:
        self.update()
        self.update_idletasks()
        self.focus_force()
        return self.mainloop()
    
    def _on_del_window(self) -> None:
        self.quit()