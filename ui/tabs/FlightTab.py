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

    _inputDataUpdate = pyqtSignal(float, float, float, float)
    _rpTrimUpdate = pyqtSignal(float, float)

    _emergencyStopUpdate = pyqtSignal(bool)

    def __init__(self, joystick, serial):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Flight Control'

        self.attitudeIndicator = AttitudeIndicator()
        self.verticalLayout_3.addWidget(self.attitudeIndicator)
        self.splitter.setSizes([1000, 1])

        self._inputDataUpdate.connect(self._inputDataUIUpdate)
        joystick.inputUpdated.add_callback(self._inputDataUpdate.emit)

    def _inputDataUIUpdate(self, thrust, yaw, roll, pitch):
        self.targetThrust.setText('%0.2f' % thrust)
        self.targetYaw.setText('%0.2f' % yaw)
        self.targetRoll.setText('%0.2f' % roll)
        self.targetPitch.setText('%0.2f' % pitch)



