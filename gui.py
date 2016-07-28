# -*- coding: utf-8 -*-

__author__ = 'Ninfeion'
__all__ = []

import sys

from ui.main import MainUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('bbproject.png'))

    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()