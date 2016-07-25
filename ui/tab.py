# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets

__author__ = 'Ninfeion'
__all__ = ['Tab']

class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.tabName = "N/A"
        self.enabled = True

    def getTabName(self):
        """Return the name of the tab that will be shown in the tab"""
        return self.tabName