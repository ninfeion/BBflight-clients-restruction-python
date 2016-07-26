# -*- coding: utf-8 -*-

import logging
import os

from ui.widgets.attitudeIndicator import AttitudeIndicator
from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

import ui

flight_tab_class = uic.loadUiType(ui.modulePath + '/tabs/flightTab.ui')[0]

class FlightTab(Tab, flight_tab_class):
    disconnectedSignal = pyqtSignal(str)
    connectionFinishSignal = pyqtSignal(str)

    _motorDataUpdate = pyqtSignal(int, object)
    _imuDataUpdate = pyqtSignal(int, object)
    _altHoldDataUpdate = pyqtSignal(int, object)
    _baroDataUpdate = pyqtSignal(int, object)

    _joystickUpdate = pyqtSignal(float, float, float, float)
    _rpTrimUpdate = pyqtSignal(float, float)

    _emergencyStopUpdate = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Flight Control'

        self.attitudeIndicator = AttitudeIndicator()
        self.verticalLayout_3.addWidget(self.attitudeIndicator)
        self.splitter.setSizes([1000, 1])


