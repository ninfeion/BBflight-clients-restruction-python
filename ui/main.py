# -*- coding: utf-8 -*-

import logging
import os

import ui.tabs
import ui.widgets
from PyQt5 import uic
from PyQt5 import QtWidgets
from devices.joystick import JoystickReader
from devices.serial import SerialApi
from PyQt5 import QtGui
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

import ui

__author__ = 'Ninfeion'
__all__ = ['MainUI']

main_window_class = uic.loadUiType(ui.modulePath + '/main.ui')[0]

class MainUI(QtWidgets.QMainWindow, main_window_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bbJoystick = JoystickReader()
        self.bbSerial = SerialApi()

        # Load and connect tabs
        self.loadedTabs = {}
        for tabClass in ui.tabs.AVAILABLE_TAB:
            tab = tabClass(self.bbJoystick, self.bbSerial)
            self.bbTabs.addTab(tab, tab.getTabName())
            self.loadedTabs[tab.getTabName()] = tab







