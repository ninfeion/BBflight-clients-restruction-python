# -*- coding: utf-8 -*-

import os

from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

import ui

controller_tab_class = uic.loadUiType(ui.modulePath + '/tabs/ControllerTab.ui')[0]

class ControllerTab(Tab, controller_tab_class):
    serialBrowserUpdate = pyqtSignal(str)

    _devicesListUpdate = pyqtSignal(object)
    _devicesSelect = pyqtSignal(int)
    _serialPortListUpdate = pyqtSignal(object)
    _serialPortSelect = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Interface Setting'

        self.splitter.setSizes([1000, 1])


