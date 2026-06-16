# main.py — Entry point for Braille Converter v1.0

import sys
import os
import io
from contextlib import redirect_stderr, redirect_stdout

# Ensure local imports work
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui import MainWindow

def main():
    # Suppress startup output
    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
        app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    app.setApplicationName("LipiSync")
    app.setApplicationVersion("2.0.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
