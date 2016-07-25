# -*- coding: utf-8 -*-

import logging
import os

import ui.tabs
import ui.widgets
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

__author__ = 'Ninfeion'
__all__ = ['MainUI']

main_window_class = uic.loadUiType(os.path.dirname(__file__) + '/main.ui')[0]

class MainUI(QtWidgets.QMainWindow, main_window_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Load and connect tabs
        self.loadedTabs = []
        for tabClass in ui.tabs.AVAILABLE_TAB:
            tab = tabClass()
            self.bbTabs.addTab(tab, tab.getTabName())
            self.loadedTabs.append(tab)







