# -*- coding: utf-8 -*-

import logging

from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton

import ui
import threading
import time
from devices.joystickMapConfig import JoystickConfig

controller_tab_class = uic.loadUiType(ui.modulePath + '/tabs/ControllerTab.ui')[0]

class ControllerTab(Tab, controller_tab_class):

    serialBrowserUpdate = pyqtSignal(str)

    _axisDataUpdate = pyqtSignal(int, float, float, float)
    _rpTrimDataUpdate = pyqtSignal(bool, bool, bool, bool)
    _exitAppUpdate = pyqtSignal(bool)
    _estopUpdate = pyqtSignal(bool)
    _altholdUpdate = pyqtSignal(bool)

    #_devicesListUpdate = pyqtSignal(object)
    #_devicesSelect = pyqtSignal(int)
    #_serialPortListUpdate = pyqtSignal(object)
    #_serialPortSelect = pyqtSignal(str)

    _mappingDetectUpdate = pyqtSignal(object)
    #_buttonDetectUpdate = pyqtSignal(object)

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

        self._buttonIndicators = {"pitchNeg": self.pitchNeg,
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

        self.detectRoll.clicked.connect(lambda : self._mappingDetect('InputAXIS', 'roll'))
        self.detectPitch.clicked.connect(lambda : self._mappingDetect('InputAXIS', 'pitch'))
        self.detectYaw.clicked.connect(lambda : self._mappingDetect('InputAXIS', 'yaw'))
        self.detectThrust.clicked.connect(lambda : self._mappingDetect('InputAXIS', 'thrust'))
        self.detectPitchPos.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'pitchPos'))
        self.detectPitchNeg.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'pitchNeg'))
        self.detectRollPos.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'rollPos'))
        self.detectRollNeg.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'rollNeg'))
        self.detectAltHold.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'althold'))
        self.detectKillswitch.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'killswitch'))
        self.detectExitapp.clicked.connect(lambda : self._mappingDetect('InputBUTTON', 'exitapp'))
        #self.detectResevered1.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered1'))
        #self.detectResevered2.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered2'))
        #self.detectResevered3.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered3'))

        self.configSave.clicked.connect(self.saveConfigFile)
        self.configLoad.clicked.connect(self.joystickConfigSelect)

        self._mappingDetectUpdate.connect(self._rawDataAnalysisForMapping)
        self._inputDevice.rawDataForDetect.add_callback(self._mappingDetectUpdate.emit)

        self._axisDataUpdate.connect(self._axisSliderUpdate)
        self._inputDevice.inputUpdated.add_callback(self._axisDataUpdate.emit)
        self._rpTrimDataUpdate.connect(self._rpTrimUiUpdate)
        self._inputDevice.rpTrimUpdated.add_callback(self._rpTrimDataUpdate.emit)
        self._exitAppUpdate.connect(self._exitAppUiUpdate)
        self._inputDevice.exitAppUpdated.add_callback(self._exitAppUpdate.emit)
        self._estopUpdate.connect(self._estopUiUpdate)
        self._inputDevice.eStopUpdated.add_callback(self._estopUpdate.emit)
        self._altholdUpdate.connect(self._altholdUiUpdate)
        self._inputDevice.altholdUpdated.add_callback(self._altholdUpdate.emit)

        self.splitter.setSizes([1000, 1])
        self.splitter_2.setSizes([1000, 1])
        self.serialPortScan.clicked.connect(self.getSerialList)

    def _axisSliderUpdate(self, thrust, yaw, roll, pitch):
        self.thrustAxisValue.setValue(thrust)
        self.yawAxisValue.setValue(yaw)
        self.rollAxisValue.setValue(roll)
        self.pitchAxisValue.setValue(pitch)

    def _rpTrimUiUpdate(self, pitchNeg, pitchPos, rollNeg, rollPos):
        self.pitchNeg.setChecked(pitchNeg)
        self.pitchPos.setChecked(pitchPos)
        self.rollNeg.setChecked(rollNeg)
        self.rollPos.setChecked(rollPos)

    def _exitAppUiUpdate(self, exitapp):
        self.exitapp.setChecked(exitapp)

    def _estopUiUpdate(self, estop):
        self.killswitch.setChecked(estop)

    def _altholdUiUpdate(self, althold):
        self.althold.setChecked(althold)

    def _mappingDetect(self, axisorbutton, key):
        logging.debug("Start Detect Type: %s, Key: %s" % (axisorbutton, key))

        self._waitPress = QMessageBox()

        self._waitPressCancel = QPushButton('Cancel')
        self._waitPressCancel.clicked.connect(self._mappingDetectCancel)
        self._waitPress.addButton(self._waitPressCancel, QMessageBox.DestructiveRole)

        self._waitPress.setWindowTitle("Wait For Single Pressed")
        self._waitPress.setText("Put One Of Axis To Max Or Press One\nOf Button Those Will Be Mapped.")

        self._singleDetectLoopFlag = True
        self._singleDetect = threading.Thread(target=self._waitSinglePressedLoop,args=(axisorbutton, key))

        self._inputDevice.setDetectEnabled(True)
        self._singleDetect.setDaemon(True)
        self._singleDetect.start()

        self._waitPress.show()

    def _mappingDetectCancel(self):
        self._singleDetectLoopFlag = True
        self._inputDevice.setDetectEnabled(False)
        self._waitPress.close()
        logging.debug("Mapping Set Cancel")

    def _waitSinglePressedLoop(self, axisorbutton, key):
        timeout = 8
        while self._singleDetectLoopFlag:
            time.sleep(0.2)
            timeout -= 0.2
            self._waitPress.setWindowTitle("Wait For Single Pressed: %0.1fs" % timeout)
            if axisorbutton == 'Input.AXIS':
                if len(self._pressedList[0]) == 1:
                    self._setMapping('Input.AXIS', key, self._pressedList[0][0])
                    break
            if axisorbutton == 'Input.BUTTON':
                if len(self._pressedList[1]) == 1:
                    self._setMapping('Input.BUTTON', key, self._pressedList[1][0])
                    break
            if timeout <= 0:
                break
        self._inputDevice.setDetectEnabled(False)
        self._waitPress.close()

    def _setMapping(self, axisorbutton, key, tarid):
        pass

    def _rawDataAnalysisForMapping(self, rawData):
        pressedAxis = []
        for i in rawData[0]:
            if (i< -0.8) or (i> 0.8):
                pressedAxis.append(rawData[0].index(i))
        pressedButton = []
        for i in rawData[1]:
            if i:
                pressedButton.append(rawData[1].index(i))

        self._pressedList = [pressedAxis, pressedButton]
        logging.debug([pressedAxis, pressedButton])


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
                                         "Please copy correct config file\nto dir,and select device again.",
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
        logging.debug("Find %d devices" % self._deviceNum)

    def saveConfigFile(self):
        configName = str(self.configFileSelect.currentText())

        mapping = {'inputconfig': {'inputdevice': {'axis': [], 'hat': [],
                                                   'button': []}}}


