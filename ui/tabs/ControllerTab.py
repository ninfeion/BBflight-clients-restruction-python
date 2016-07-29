# -*- coding: utf-8 -*-

import logging

from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox

import ui
from devices.joystick import JoystickReader
from devices.joystickMapConfig import JoystickConfig

controller_tab_class = uic.loadUiType(ui.modulePath + '/tabs/ControllerTab.ui')[0]

class ControllerTab(Tab, controller_tab_class):

    serialBrowserUpdate = pyqtSignal(str)

    _axisDataUpdate = pyqtSignal(int, float, float, float)

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

        self._axisIndicators = {"roll": self.rollAxisValue,
                                "pitch": self.pitchAxisValue,
                                "yaw": self.yawAxisValue,
                                "thrust": self.thrustAxisValue}

        self._hatButtonIndicators = {"pitchNeg": self.pitchNeg,
                                    "pitchPos": self.pitchPos,
                                    "rollNeg": self.rollNeg,
                                    "rollPos": self.rollPos,
                                    "althold": self.althold,
                                    "killswitch": self.killswitch,
                                    "exitapp": self.exitapp,
                                    "resevered1": self.resevered1,
                                    "resevered2": self.resevered2,
                                    "resevered3": self.resevered3}

        self.joystickScan.clicked.connect(self.scanInputDevice)
        self.joystickSelect.activated[str].connect(self.selectInputDevice)

        self.detectRoll.clicked.connect(self.axisDetect)
        self.detectPitch.clicked.connect(self.axisDetect)
        self.detectYaw.clicked.connect(self.axisDetect)
        self.detectThrust.clicked.connect(self.axisDetect)
        self.detectPitchPos.clicked.connect(self.hatOrButtonDetect)
        self.detectPitchNeg.clicked.connect(self.hatOrButtonDetect)
        self.detectRollPos.clicked.connect(self.hatOrButtonDetect)
        self.detectRollNeg.clicked.connect(self.hatOrButtonDetect)
        self.detectAltHold.clicked.connect(self.hatOrButtonDetect)
        self.detectKillswitch.clicked.connect(self.hatOrButtonDetect)
        self.detectExitapp.clicked.connect(self.hatOrButtonDetect)
        self.detectResevered1.clicked.connect(self.hatOrButtonDetect)
        self.detectResevered2.clicked.connect(self.hatOrButtonDetect)
        self.detectResevered3.clicked.connect(self.hatOrButtonDetect)

        self.configSave.clicked.connect(self.saveConfigFile)
        self.configLoad.clicked.connect(self.joystickConfigSelect)
        #self.configFileSelect.activated[str].connect()

        self.splitter.setSizes([1000, 1])

        self.serialPortScan.clicked.connect(self.getSerialList)

    def axisDetect(self):
        pass

    def hatOrButtonDetect(self):
        pass

    def getSerialList(self):
        pass

    def selectInputDevice(self, par):
        self.joystickName.setText(self._inputDevice.setDevice(int(par)))
        self.configFileSelect.setEnabled(True)

        configList = JoystickConfig().readConfigFile()
        if configList:
            self.configFileSelect.clear()
            for fn in configList:
                self.configFileSelect.addItem(fn)

            self.configLoad.setEnabled(True)

        else:
            error = QMessageBox.warning(self, 'Have Not Found Config File',
                                         "Please copy correct config file\nto dir, and select device again.",
                                         QMessageBox.Apply)

    def joystickConfigSelect(self):
        self._inputDevice.setMapping(self.configFileSelect.currentText())
        self._inputDevice.readTimer.start()
        self.detectButtonEnabled(True)

    def detectButtonEnabled(self, par):
        self.configSave.setEnabled(par)
        self.detectRoll.setEnabled(par)
        self.detectPitch.setEnabled(par)
        self.detectYaw.setEnabled(par)
        self.detectThrust.setEnabled(par)
        self.detectPitchPos.setEnabled(par)
        self.detectPitchNeg.setEnabled(par)
        self.detectRollPos.setEnabled(par)
        self.detectRollNeg.setEnabled(par)
        self.detectAltHold.setEnabled(par)
        self.detectKillswitch.setEnabled(par)
        self.detectExitapp.setEnabled(par)
        self.detectResevered1.setEnabled(par)
        self.detectResevered2.setEnabled(par)
        self.detectResevered3.setEnabled(par)

    def scanInputDevice(self):
        self._deviceNum = self._inputDevice.initDevice()
        self.joystickSelect.clear()
        if self._deviceNum:
            for i in range(self._deviceNum):
                self.joystickSelect.addItem(str(i))
        logging.debug("Find %d devices." % self._deviceNum)

    def saveConfigFile(self):
        configName = str(self.configFileSelect.currentText())

        mapping = {'inputconfig': {'inputdevice': {'axis': [], 'hat': [],
                                                   'button': []}}}


