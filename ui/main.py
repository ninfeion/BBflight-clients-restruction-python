# -*- coding: utf-8 -*-

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

class MainUI(QtWidgets.QMainWindow, main_window_class):

    batteryUiUpdate = pyqtSignal(int)
    linkQualityUiUpdate = pyqtSignal(int)
    flightConnectStatus = pyqtSignal(bool)

    canConnect_Serial = pyqtSignal(bool)
    serialRawDataShow = pyqtSignal(object)

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
        self.bbCommander.batteryUpdate.add_callback(self.batteryUiUpdate.emit)
        self.bbCommander.linkQualityUpdate.add_callback(self.linkQualityUiUpdate.emit)

        self.address.setText(Config().get("device_address"))

        self.batteryUiUpdate.connect(self.batteryUiValSet)
        self.linkQualityUiUpdate.connect(self.linkQualityUiValSet)

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

        self.canConnect_Serial.connect(self.connectReady)
        self.loadedTabs['Interface Setting'].canConnectFromSerial.add_callback(
            self.canConnect_Serial.emit)
        self.serialRawDataShow.connect(self.serialBrowserUpdate)
        self.bbCommander.rawRecieveUpdate.add_callback(self.serialRawDataShow.emit)

    def serialBrowserUpdate(self, rawbytes):
        willshow = binascii.b2a_hex(rawbytes).decode('ascii')
        string = ""
        while len(willshow):
            string = string + "\\x" + willshow[:2]
            willshow = willshow[2:]
        self.loadedTabs['Interface Setting'].serialTextBrowser.append(string)

    def connectReady(self, par):
        if par:
            self.ConnectPushButton.setText("No Connect")
            self.ConnectPushButton.setEnabled(True)
            self.bbCommander.comRxTimer.start()
        else:
            self.ConnectPushButton.setText("No Ready")
            self.ConnectPushButton.setEnabled(False)
            self.bbCommander.comRxTimer.stop()

    def batteryUiValSet(self, val):
        self.batteryProgressBar.setValue(val)

    def linkQualityUiValSet(self, val):
        self.linkQualityProgressBar.setValue(val)

    def saveClientConfig(self):
        Config().saveFile()

    def aboutBBFlight(self):
        pass







