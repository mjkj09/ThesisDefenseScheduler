import os
import sys
import tkinter as tk

from src.gui.main_window import MainWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
