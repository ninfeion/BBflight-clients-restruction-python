# -*- coding: utf-8 -*-

from ui.tab import Tab

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton

import ui
import time
import logging
import threading
import serial.tools.list_ports

from utils.callbacks import Caller
from config.bbconfig import Config
from devices.joystickMapConfig import JoystickConfig

controller_tab_class = uic.loadUiType(ui.modulePath + '/tabs/ControllerTab.ui')[0]

class ControllerTab(Tab, controller_tab_class):

    serialBrowserUpdate = pyqtSignal(str)
    _axisDataUpdate = pyqtSignal(int, float, float, float)
    _rpTrimDataUpdate = pyqtSignal(bool, bool, bool, bool)
    _exitAppUpdate = pyqtSignal(bool)
    _estopUpdate = pyqtSignal(bool)
    _altholdUpdate = pyqtSignal(bool)
    _detectMessageBoxShowOrCloseSignal = pyqtSignal(bool)
    _detectMessageBoxTitleSetSignal = pyqtSignal(str)

    _mappingDetectUpdate = pyqtSignal(object)
    #connectionFinishSignal = pyqtSignal(str)
    #disconnectedSignal = pyqtSignal(str)

    def __init__(self, joystick, serial):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Interface Setting'

        self._deviceNum = None
        self._inputDevice = joystick
        self._serial = serial

        self.joystickScan.clicked.connect(self.scanInputDevice)
        self.joystickSelect.activated[str].connect(self.selectInputDevice)

        self._pressedList = None
        self._pressedListMutex = threading.Lock()
        self.detectRoll.clicked.connect(lambda : self._mappingDetect('Input.AXIS', 'roll'))
        self.detectPitch.clicked.connect(lambda : self._mappingDetect('Input.AXIS', 'pitch'))
        self.detectYaw.clicked.connect(lambda : self._mappingDetect('Input.AXIS', 'yaw'))
        self.detectThrust.clicked.connect(lambda : self._mappingDetect('Input.AXIS', 'thrust'))
        self.detectPitchPos.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'pitchPos'))
        self.detectPitchNeg.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'pitchNeg'))
        self.detectRollPos.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'rollPos'))
        self.detectRollNeg.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'rollNeg'))
        self.detectAltHold.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'althold'))
        self.detectKillswitch.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'estop'))
        self.detectExitapp.clicked.connect(lambda : self._mappingDetect('Input.BUTTON', 'exitapp'))
        #self.detectResevered1.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered1'))
        #self.detectResevered2.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered2'))
        #self.detectResevered3.clicked.connect(lambda : self._mappingDetect(self, 'InputBUTTON', 'resevered3'))

        self._detectMessageBoxShowOrCloseSignal.connect(self._detectMessageBoxShowOrClose)
        self._detectMessageBoxTitleSetSignal.connect(self._detectMessageBoxTitleSet)
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
        self.serialOpen.clicked.connect(self.openSerialPort)
        self.serialClose.clicked.connect(self.closeSerialPort)

        self.baudRateSet.currentIndexChanged[int].connect(self.serialBaudRateSet)
        self.dataBitsSet.currentIndexChanged[int].connect(self.serialDataBitsSet)
        self.paritySet.currentIndexChanged[int].connect(self.serialParitySet)
        self.stopBitsSet.currentIndexChanged[int].connect(self.serialStopBitsSet)
        self.flowControlSet.currentIndexChanged[int].connect(self.serialFlowControlSet)

        self.baudRateSet.setCurrentIndex((lambda ite: 0 if ite == '9600' else
                                                     1 if ite == '19200' else
                                                     2 if ite == '38400' else
                                                     3 )(Config().get("serial_baudrate")))
        self.dataBitsSet.setCurrentIndex((lambda ite: 0 if ite == '8' else
                                                     1 if ite == '7' else
                                                     2 if ite == '6' else
                                                     3 )(Config().get("serial_bytesize")))
        self.paritySet.setCurrentIndex((lambda ite: 0 if ite == 'None' else
                                                   1 if ite == 'Even' else
                                                   2 if ite == 'Odd' else
                                                   3 if ite == 'Mark' else
                                                   4 )(Config().get("serial_parity")))
        self.stopBitsSet.setCurrentIndex((lambda ite: 0 if ite == '1' else
                                                     1 if ite == '1.5' else
                                                     2 )(Config().get("serial_stopbits")))
        self.flowControlSet.setCurrentIndex((lambda ite: 0 if ite == 'None' else
                                                        1 if ite == 'RTS/CTS' else
                                                        2 )(Config().get("serial_flowcontrol")))

        self.canConnectFromSerial = Caller()
        self.serialBrowserClear.clicked.connect(lambda : self.serialTextBrowser.clear())

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
        if axisorbutton == 'Input.AXIS':
            self._waitPress.setText("Put One Of Axis To Max Or Min Value\n"
                                    "Press One Which Will Be Mapped As %s." % key)
        else:
            self._waitPress.setText("Press One Of Button Which Will Be Mapped As %s." % key)
        self._singleDetectLoopFlag = True
        self._singleDetect = threading.Thread(target=self._waitSinglePressedLoop,
                                              args=(axisorbutton, key, 0.1))
        self._inputDevice.setDetectEnabled(True)
        self._singleDetect.setDaemon(True)
        self._singleDetect.start()
        self._waitPress.show()

    def _mappingDetectCancel(self):
        self._singleDetectLoopFlag = False
        self._inputDevice.setDetectEnabled(False)
        self._waitPress.close()
        logging.debug("Mapping Set Cancel")

    def _waitSinglePressedLoop(self, axisorbutton, key, offsettime):
        timeout = 8
        while self._singleDetectLoopFlag:
            time.sleep(0.2)
            if self._singleDetectLoopFlag == False:
                break
            timeout -= 0.2
            self._detectMessageBoxTitleSetSignal.emit("Wait For Single Pressed: %0.1fs" % timeout)
            if axisorbutton == 'Input.AXIS':
                self._pressedListMutex.acquire()
                if len(self._pressedList[0]) == 1:
                    time.sleep(offsettime)
                    timeout -= offsettime
                    if len(self._pressedList[0]) == 1:
                        self._setMapping('Input.AXIS', key, self._pressedList[0][0])
                        logging.debug("AXIS id: %d is detected, "
                                      "target key: %s" % (self._pressedList[0][0], key))
                        self._pressedListMutex.release()
                        break
                self._pressedListMutex.release()
            if axisorbutton == 'Input.BUTTON':
                self._pressedListMutex.acquire()
                if len(self._pressedList[1]) == 1:
                    time.sleep(offsettime)
                    timeout -= offsettime
                    if len(self._pressedList[1]) == 1:
                        self._setMapping('Input.BUTTON', key, self._pressedList[1][0])
                        logging.debug("BUTTON id: %d is detected, "
                                      "target key: %s" % (self._pressedList[1][0], key))
                        self._pressedListMutex.release()
                        break
                self._pressedListMutex.release()
            if timeout <= 0:
                break
        self._inputDevice.setDetectEnabled(False)
        self._detectMessageBoxShowOrCloseSignal.emit(False)

    def _detectMessageBoxShowOrClose(self, par):
        if par:
            self._waitPress.show()
        else:
            self._waitPress.close()

    def _detectMessageBoxTitleSet(self, string):
        self._waitPress.setWindowTitle(string)

    def _setMapping(self, axisorbutton, key, tarid):
        self._inputDevice.resetMappingAfterLoadConfig(axisorbutton, key, tarid)

    def _rawDataAnalysisForMapping(self, rawData):
        pressedAxis = []
        for i in rawData[0]:
            if (i< -0.8) or (i> 0.8):
                pressedAxis.append(rawData[0].index(i))
        pressedButton = []
        for i in rawData[1]:
            if i:
                pressedButton.append(rawData[1].index(i))
        self._pressedListMutex.acquire()
        self._pressedList = [pressedAxis, pressedButton]
        self._pressedListMutex.release()

    def getSerialList(self):
        self.portName = {}
        self.portList = list(serial.tools.list_ports.comports())
        self.serialPortSelect.clear()
        for i in range(len(self.portList)):
            self.portName[self.portList[i][0]] = self.portList[i][1]
        logging.debug("Serial Port Found List: %s" %self.portName)
        if len(self.portName):
            for p in self.portName:
                self.serialPortSelect.addItem(self.portName[p])
        self.serialOpen.setEnabled(True)
        self.baudRateSet.setEnabled(True)
        self.dataBitsSet.setEnabled(True)
        self.paritySet.setEnabled(True)
        self.stopBitsSet.setEnabled(True)
        self.flowControlSet.setEnabled(True)

    def openSerialPort(self):
        portChosen = self.serialPortSelect.currentText()

        for p in self.portName:
            if self.portName[p] == portChosen:
                self._serial.port = p

        self._serial.baudrate = int(Config().get("serial_baudrate"))
        self._serial.bytesize = int(Config().get("serial_bytesize"))
        self._serial.parity = Config().get("serial_parity")[0]
        self._serial.stopbits = (lambda string: int(string) if string != '1.5'
                          else float(string))(Config().get("serial_stopbits"))
        self._serial.rtscts = (lambda string: True if string == 'RTS/CTS'
                          else False)(Config().get("serial_flowcontrol"))
        self._serial.xonxoff = (lambda string: True if string == 'XON/XOFF'
                          else False)(Config().get("serial_flowcontrol"))
        try:
            self._serial.open()
            self.serialClose.setEnabled(True)
            self.canConnectFromSerial.call(True)
            self.serialOpen.setEnabled(False)
            logging.debug("Serial: %s Open Success" % self._serial.port)
        except Exception as e:
            logging.info("Serial: %s Open Fail: %s" %(self._serial.port, e))

    def closeSerialPort(self):
        try:
            self._serial.close()
            self.serialClose.setEnabled(False)
            self.canConnectFromSerial.call(False)
            self.serialOpen.setEnabled(True)
            logging.debug("Serial: %s Close Success" % self._serial.port)
        except Exception as e:
            logging.info("Serial: %s Close Fail: %s" %(self._serial.port, e))

    def serialBaudRateSet(self, item):
        Config().set("serial_baudrate", self.baudRateSet.itemText(item))
        logging.debug("Set Baud Rate to %s" % self.baudRateSet.itemText(item))

    def serialDataBitsSet(self, item):
        Config().set("serial_bytesize", self.dataBitsSet.itemText(item))
        logging.debug("Set Data Bits to %s" % self.dataBitsSet.itemText(item))

    def serialParitySet(self, item):
        Config().set("serial_parity", self.paritySet.itemText(item))
        logging.debug("Set Parity to %s" % self.paritySet.itemText(item))

    def serialStopBitsSet(self, item):
        Config().set("serial_stopbits", self.stopBitsSet.itemText(item))
        logging.debug("Set Stop Bits to %s" % self.stopBitsSet.itemText(item))

    def serialFlowControlSet(self, item):
        Config().set("serial_flowcontrol", self.flowControlSet.itemText(item))
        logging.debug("Set Flow Control to %s" % self.flowControlSet.itemText(item))

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
                                         "Please copy correct config file\n"
                                         "to dir,and select device again.",
                                         QMessageBox.Apply)

    def joystickConfigSelect(self):
        self._inputDevice.setMapping(self.configFileSelect.currentText())
        if not self._inputDevice.readTimer.isStart():
            self._inputDevice.readTimer.start()
        else:
            logging.debug("Reload Mapping Config File:"
                          " %s" % self.configFileSelect.currentText())
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
        if self._inputDevice.readTimer.isStart:
            self._inputDevice.readTimer.stop()
        self._deviceNum = self._inputDevice.initDevice()
        self.joystickSelect.clear()
        if self._deviceNum:
            for i in range(self._deviceNum):
                self.joystickSelect.addItem(str(i))
        logging.debug("Find %d devices" % self._deviceNum)

    def saveConfigFile(self):
        self._inputDevice.saveConfig(self.configFileSelect.currentText())
        #logging.debug("Save Mapping In File: %s" % self.configFileSelect.currentText())




