# Terrance Wong
# HandDJ

import os
# has to be set before pygame is imported anywhere
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
from PyQt5.QtWidgets import QApplication
from gui.windows import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
