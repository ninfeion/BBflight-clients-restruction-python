# -*- coding: utf-8 -*-

import os

from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

import ui
from devices.joystick import JoystickReader
from devices.joystickMapConfig import JoystickConfig

controller_tab_class = uic.loadUiType(ui.modulePath + '/tabs/ControllerTab.ui')[0]

class ControllerTab(Tab, controller_tab_class):
    serialBrowserUpdate = pyqtSignal(str)

    _devicesListUpdate = pyqtSignal(object)
    _devicesSelect = pyqtSignal(int)
    _serialPortListUpdate = pyqtSignal(object)
    _serialPortSelect = pyqtSignal(str)

    connectionFinishSignal = pyqtSignal(str)
    disconnectedSignal = pyqtSignal(str)

    def __init__(self, joystick, serial):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Interface Setting'

        self._deviceNum = None
        self._inputDevice = joystick

        self.joystickScan.clicked.connect(self.scanInputDevice)
        self.joystickSelect.activated[str].connect(self)

        self.detectRoll.clicked.connect
        self.detectPitch.clicked.connect
        self.detectYaw.clicked.connect
        self.detectThrust.clicked.connect
        self.detectPitchPos.clicked.connect
        self.detectPitchNeg.clicked.connect
        self.detechRollPos.clicked.connect
        self.detectRollNeg.clicked.connect
        self.detectAltHold.clicked.connect
        self.detectKillswitch.clicked.connect
        self.detectExitapp.clicked.connect
        self.detectResevered1.clicked.connect
        self.detectResevered2.clicked.connect
        self.detectResevered3.clicked.connect

        self.configSave.clicked.connect
        self.configLoad.clicked.connect
        self.configSetDefault.clicked.connect
        self.configFileSelect.activated[str].connect

        self.splitter.setSizes([1000, 1])

        self.serialPortScan.clicked.connect

    def scanInputDevice(self):
        self._deviceNum = self._inputDevice.initDevice()
        self.joystickSelect.clear()
        if self._deviceNum:
            for i in self._deviceNum:
                self.joystickSelect.addItem(str(i))



    def saveConfigFile(self):
        configName = str(self.configFileSelect.currentText())

        mapping = {'inputconfig': {'inputdevice': {'axis': [], 'hat': [],
                                                   'button': []}}}


