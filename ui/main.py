# -*- coding: utf-8 -*-

import time
import serial
import logging
import binascii

import ui
import ui.tabs
import ui.widgets
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from devices.joystick import JoystickReader
from devices.commander import RadioDevice
from devices.commander import Commander

__author__ = 'Ninfeion'
__all__ = ['MainUI']

main_window_class = uic.loadUiType(ui.modulePath + '/main.ui')[0]
logging.basicConfig(level=logging.DEBUG)

from config.bbconfig import Config


class ConnectedState:
    NOTCONNECTALLOW = 0
    CONNECTREADY = 1
    CONNECTING = 2
    CONNECTED = 3


class BatteryState:
    GOOD, MIDDLE, LOW, DANGER = list(range(4))

COLORBLUE = '#3399ff'
COLORGREEN = '#00ff60'
COLORRED = '#cc0404'


def progressbar_stylesheet(color):
    return """
        QProgressBar {
            border: 1px solid #333;
            background-color: transparent;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: """ + color + """;
        }
    """

# CSS EXAMPLES
"""
QDialog#MainDlg{
    background-image: url("bg.png");
    border: 1px solid #999;
    border-radius: 5px;
}

QPushButton{
    color:white;
    border-radius:3px;
    background-color: black;
}

QLabel{
    color:blue;
}

QLineEdit{
    text-align: center;
    color:red;
    background-color: transparent;
    border: 1px solid white;
    selection-color:yellow;
    selection-background-color:green;
}

QRadioButton{
    color: slateblue;
}

QRadioButton::indicator:on{
    background-image: url("1.gif");
}

QComboBox{
    min - width: 4em;
    background-color: transparent;
}

QComboBox:on{
    color:red;
}

QComboBox:off{
    color:black;
}

QComboBox QAbstractItemView{
    border: 1px solid black;
    color:black;
    selection-color: red;
    selection-background-color: green;
}

QProgressBar{
    border: 1px solid  #999;
    border-radius:5px;
    text-align: center;
    background-color: transparent;
}

QProgressBar::chunk{
    background-color: #CD96CD;
    width: 10px;
}
"""


class MainUI(QtWidgets.QMainWindow, main_window_class):

    batteryUiUpdate = pyqtSignal(int)
    linkQualityUiUpdate = pyqtSignal(int)
    flightConnectStatus = pyqtSignal(bool)

    canConnect_Serial = pyqtSignal(bool)
    serialRawDataShow = pyqtSignal(object)
    slaveConnectionState = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bbFlight = RadioDevice()
        self.bbJoystick = JoystickReader()
        self.bbJoystick.inputUpdated.add_callback(self.bbFlight.setControlPar)
        self.bbJoystick.rpTrimUpdated.add_callback(self.bbFlight.setRPTrim)
        self.bbJoystick.altholdUpdated.add_callback(self.bbFlight.setAltHold)
        self.bbJoystick.eStopUpdated.add_callback(self.bbFlight.setEStop)

        self.bbSerial = serial.Serial()
        self.bbCommander = Commander(self.bbFlight, self.bbSerial)
        self.bbCommander.batteryUpdate.add_callback(self.batteryUiUpdate.emit)
        self.bbCommander.linkQualityUpdate.add_callback(self.linkQualityUiUpdate.emit)

        self.address.setText(Config().get("device_address"))
        self._connectState = ConnectedState.NOTCONNECTALLOW
        self.linkQualityProgressBar.setStyleSheet(progressbar_stylesheet(COLORRED))
        self.batteryProgressBar.setStyleSheet(progressbar_stylesheet(COLORRED))
        self._batteryState = BatteryState.DANGER

        self.batteryUiUpdate.connect(self.batteryUiValSet)
        self.linkQualityUiUpdate.connect(self.linkQualityUiValSet)

        self.connectPushButton.clicked.connect(self.connectAction)
        self.slaveConnectionState.connect(self.slaveConnectRespond)
        self.bbCommander.flightConnectionUpdate.add_callback(self.slaveConnectionState.emit)

        # Set Menu Bar
        self.actionSaveConfig.triggered.connect(self.saveClientConfig)
        self.actionAbout.triggered.connect(self.aboutBBFlight)

        # Load and connect tabs
        self.loadedTabs = {}
        tab = ui.tabs.AVAILABLE_TAB[0](self.bbJoystick, self.bbCommander)
        self.bbTabs.addTab(tab, tab.getTabName())
        self.loadedTabs[tab.getTabName()] = tab
        tab = ui.tabs.AVAILABLE_TAB[1](self.bbJoystick, self.bbSerial)
        self.bbTabs.addTab(tab, tab.getTabName())
        self.loadedTabs[tab.getTabName()] = tab

        self.bbTabs.setCurrentIndex(1)

        self.canConnect_Serial.connect(self.connectReady)
        self.loadedTabs['Interface Setting'].canConnectFromSerial.add_callback(
            self.canConnect_Serial.emit)
        self.serialRawDataShow.connect(self.serialBrowserUpdate)
        self.bbCommander.rawRecieveUpdate.add_callback(self.serialRawDataShow.emit)

        self.loadedTabs['Flight Control'].PGainSet.valueChanged[int].connect(self.pidSetupMethod)
        self.loadedTabs['Flight Control'].thrustProgressBar.setStyleSheet(progressbar_stylesheet(COLORBLUE))
        self.loadedTabs['Flight Control'].m1ProgressBar.setStyleSheet(progressbar_stylesheet(COLORBLUE))
        self.loadedTabs['Flight Control'].m2ProgressBar.setStyleSheet(progressbar_stylesheet(COLORBLUE))
        self.loadedTabs['Flight Control'].m3ProgressBar.setStyleSheet(progressbar_stylesheet(COLORBLUE))
        self.loadedTabs['Flight Control'].m4ProgressBar.setStyleSheet(progressbar_stylesheet(COLORBLUE))

    def pidSetupMethod(self, val):
        self.loadedTabs['Flight Control'].pidTypeLabelMap[
            self.loadedTabs['Flight Control'].PGainAngle.currentIndex()].setEnabled(True)

        pidtype = self.loadedTabs['Flight Control'].PGainAngle.currentIndex()
        self.loadedTabs['Flight Control'].pidTypeLabelMap[pidtype].setText(
            self.loadedTabs['Flight Control'].pidTypeIndexMap[pidtype] + str(val))
        self.bbFlight.pidSetup(pidtype + 1, val)
        logging.debug("Pid Parameter Change: %s%d" % (
            self.loadedTabs['Flight Control'].pidTypeIndexMap[pidtype],val))

    def slaveConnectRespond(self, par):
        pass
        #if self._connectState == ConnectedState.CONNECTING and par == True:
        #    self._connectState = ConnectedState.CONNECTED
        #    self.connectPushButton.setText("Connect Done")


    def connectAction(self):
        pass
        #if self._connectState == ConnectedState.NOTCONNECTALLOW:
        #    pass
        #elif self._connectState == ConnectedState.CONNECTREADY:
        #    self.connectPushButton.setText("Connecting...")
        #    self.bbStatusbar.showMessage("Start Build Connection To Radio!")
        #    self._connectState = ConnectedState.CONNECTING
        #    self.bbFlight.setTryConnect(True)

        #elif self._connectState == ConnectedState.CONNECTING:
        #    self.connectPushButton.setText("No Connect")
        #    self.bbStatusbar.showMessage("Connection Cancel!")
        #    self._connectState = ConnectedState.CONNECTREADY
        #    self.bbFlight.setTryConnect(False)

        #elif self._connectState == ConnectedState.CONNECTED:
        #    self.bbStatusbar.showMessage("Shut Down The Connection!")
        #    self.bbFlight.setTryConnect(False)

        #else:
        #    return None

    def serialBrowserUpdate(self, rawbytes):
        willshow = binascii.b2a_hex(rawbytes).decode('ascii')
        string = ""
        while len(willshow):
            string = string + "\\x" + willshow[:2]
            willshow = willshow[2:]
        self.loadedTabs['Interface Setting'].serialTextBrowser.append(time.strftime(
            "%H:%M:%S", time.localtime()) + ':\n' + string)

    def connectReady(self, par):
        if par:
            self.connectPushButton.setText("No Connect")
            self.connectPushButton.setEnabled(True)
            self.bbStatusbar.showMessage("Serial Open, Trying Connect Is Allowed!")
            self.bbCommander.comRxTimer.start()
            self.bbCommander.comTxTimer.start()
            logging.debug("Command Recieving And Sending Start!")
            self._connectState = ConnectedState.CONNECTREADY
        else:
            self.connectPushButton.setText("No Ready")
            self.connectPushButton.setEnabled(False)
            self.bbCommander.comRxTimer.stop()
            self.bbCommander.comTxTimer.stop()
            logging.debug("Command Recieving And Sending Stop!")
            self._connectState = ConnectedState.NOTCONNECTALLOW

    def batteryUiValSet(self, val):
        if val >= 3600:
            self._batteryState = BatteryState.GOOD
            color = COLORGREEN
        elif 3300 <= val < 3600:
            self._batteryState = BatteryState.MIDDLE
            color = COLORBLUE
        elif val < 3300:
            self._batteryState = BatteryState.LOW
            color = COLORRED
        else:
            color = COLORRED
        self.batteryProgressBar.setStyleSheet(progressbar_stylesheet(color))
        self.batteryProgressBar.setValue(val)

    def linkQualityUiValSet(self, val):
        if val >= 50:
            color = COLORGREEN
        elif 20 <= val < 50:
            color = COLORBLUE
        else:
            color = COLORRED
        self.linkQualityProgressBar.setStyleSheet(progressbar_stylesheet(color))
        self.linkQualityProgressBar.setValue(val)

    def saveClientConfig(self):
        Config().saveFile()

    def aboutBBFlight(self):
        pass
