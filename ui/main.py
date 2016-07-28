# -*- coding: utf-8 -*-

import logging
import os
import serial

import ui.tabs
import ui.widgets
from PyQt5 import uic
from PyQt5 import QtWidgets
from devices.joystick import JoystickReader
from devices.serial import SerialApi
from devices.commander import RadioDevice
from devices.commander import Commander
from PyQt5 import QtGui
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

import ui

__author__ = 'Ninfeion'
__all__ = ['MainUI']

main_window_class = uic.loadUiType(ui.modulePath + '/main.ui')[0]
logging.basicConfig(level=logging.DEBUG)

class MainUI(QtWidgets.QMainWindow, main_window_class):

    batteryUiUpdate = pyqtSignal(int)
    linkQualityUiUpdate = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bbFlight = RadioDevice()
        self.bbJoystick = JoystickReader()
        self.bbJoystick.inputUpdated.add_callback(self.bbFlight.setControlPar)
        self.bbJoystick.altholdUpdated.add_callback(self.bbFlight.setAltHold)
        self.bbJoystick.eStopUpdated.add_callback(self.bbFlight.setEStop)


        self.bbSerial = serial.Serial()
        self.bbCommander = Commander(self.bbFlight, self.bbSerial)

        # Load and connect tabs
        self.loadedTabs = {}
        tab = ui.tabs.AVAILABLE_TAB[0](self.bbJoystick, self.bbCommander)
        self.bbTabs.addTab(tab, tab.getTabName())
        self.loadedTabs[tab.getTabName()] = tab
        tab = ui.tabs.AVAILABLE_TAB[1](self.bbJoystick, self.bbSerial)
        self.bbTabs.addTab(tab, tab.getTabName())
        self.loadedTabs[tab.getTabName()] = tab









