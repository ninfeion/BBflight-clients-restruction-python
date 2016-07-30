# -*- coding: utf-8 -*-

import logging
import os

from ui.widgets.attitudeIndicator import AttitudeIndicator
from ui.tab import Tab
from config.bbconfig import Config

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

import ui

flight_tab_class = uic.loadUiType(ui.modulePath + '/tabs/flightTab.ui')[0]

class FlightTab(Tab, flight_tab_class):
    disconnectedSignal = pyqtSignal(str)
    connectionFinishSignal = pyqtSignal(str)

    _imuDataUpdate = pyqtSignal(object)

    #_altHoldDataUpdate = pyqtSignal(int, object)
    #_baroDataUpdate = pyqtSignal(int, object)

    _inputDataUpdate = pyqtSignal(int, float, float, float)
    _rpTrimUpdate = pyqtSignal(float, float)

    _emergencyStopUpdate = pyqtSignal(bool)

    def __init__(self, joystick, comemiter):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Flight Control'

        self.yawOffset.setValue(Config().get("trim_yaw"))
        self.pitchOffset.setValue(Config().get("trim_pitch"))
        self.rollOffset.setValue(Config().get("trim_roll"))

        self.attitudeIndicator = AttitudeIndicator()
        self.verticalLayout_3.addWidget(self.attitudeIndicator)
        self.splitter.setSizes([1000, 1])

        self._inputDataUpdate.connect(self._inputDataUIUpdate)
        joystick.inputUpdated.add_callback(self._inputDataUpdate.emit)
        self._imuDataUpdate.connect(self._imuUiUpdate)
        comemiter.imuDataUpdate.add_callback(self._imuDataUpdate.emit)

        self.flightModeComboBox.currentIndexChanged[int].connect(self.flightModeChange)
        self.thrustModeComboBox.currentIndexChanged[int].connect(self.thrustModeChange)
        self.yawOffset.valueChanged[float].connect(self.yawOffsetSetting)
        self.pitchOffset.valueChanged[float].connect(self.pitchOffsetSetting)
        self.rollOffset.valueChanged[float].connect(self.rollOffsetSetting)
        self.xModeRadioButton.toggled[bool].connect(self.xModeSetting)
        self.tenModeRadioButton.toggled[bool].connect(self.tenModeSetting)
        self.isInFlightmode = False

        self.maxAngle.valueChanged[int].connect(self.maxAngleSetting)
        self.maxYawAngle.valueChanged[int].connect(self.maxYawAngleSetting)
        self.maxThrust.valueChanged[float].connect(self.maxThrustSetting)
        self.minThrust.valueChanged[float].connect(self.minThrustSetting)
        self.slewLimit.valueChanged[float].connect(self.slewLimitSetting)
        self.thrustLoweringSlewRate.valueChanged[float].connect(self.thrustLoweringSlewRateSetting)

        self.maxAngle.setValue(Config().get("normal_max_rp"))
        self.maxYawAngle.setValue(Config().get("normal_max_yaw"))  # rate
        self.maxThrust.setValue(Config().get("normal_max_thrust"))
        self.minThrust.setValue(Config().get("normal_min_thrust"))
        self.slewLimit.setValue(Config().get("normal_slew_limit"))
        self.thrustLoweringSlewRate.setValue(Config().get("normal_slew_rate"))
        if Config().get("flightmode") == 'Normal':
            self.flightModeComboBox.setCurrentIndex(0)
        else:
            self.flightModeComboBox.setCurrentIndex(1)
        if Config().get("thrustmode") == 'Linear':
            self.thrustModeComboBox.setCurrentIndex(0)
        else:
            self.thrustModeComboBox.setCurrentIndex(1)

    def yawOffsetSetting(self, par):
        Config().set("trim_yaw", par)
        logging.debug("Set yaw offset to %f" % par)

    def pitchOffsetSetting(self, par):
        Config().set("trim_pitch", par)
        logging.debug("Set pitch offset to %f" % par)

    def rollOffsetSetting(self, par):
        Config().set("trim_roll", par)
        logging.debug("Set roll offset to %f" % par)

    def xModeSetting(self, par):
        if par == True:
            Config().set("is_xmode", True)
            logging.debug("Control mode is X mode")

    def tenModeSetting(self, par):
        if par == True:
            Config().set("is_xmode", False)
            logging.debug("Control mode is + mode")

    def maxAngleSetting(self, par):
        if self.isInFlightmode:
            Config().set("max_rp", par)
            logging.debug("Change maxAngle limit(roll and pitch) to %d" % par)

    def maxYawAngleSetting(self, par):
        if self.isInFlightmode:
            Config().set("max_yaw", par)
            logging.debug("Change maxYaw limit to %d" % par)

    def maxThrustSetting(self, par):
        if self.isInFlightmode:
            Config().set("max_thrust", par)
            logging.debug("Change maxThrust limit to %f" % par)

    def minThrustSetting(self, par):
        if self.isInFlightmode:
            Config().set("min_thrust", par)
            logging.debug("Change minThrust limit to %f" % par)

    def slewLimitSetting(self, par):
        if self.isInFlightmode:
            Config().set("slew_limit", par)
            logging.debug("Change slew limit to %f" % par)

    def thrustLoweringSlewRateSetting(self, par):
        if self.isInFlightmode:
            Config().set("slew_rate", par)
            logging.debug("Change thrust lowering slew rate to %f" % par)

    def thrustModeChange(self, item):
        Config().set("thrustmode", str(self.thrustModeComboBox.itemText(item)))
        logging.debug("Change thrustmode to %s" % str(self.thrustModeComboBox.itemText(item)))

    def flightModeChange(self, item):
        Config().set("flightmode", str(self.flightModeComboBox.itemText(item)))
        logging.debug("Change flightmode to %s" % str(self.flightModeComboBox.itemText(item)))
        self.isInFlightmode = False

        if item == 0:
            self.maxAngle.setValue(Config().get("normal_max_rp"))
            self.maxYawAngle.setValue(Config().get("normal_max_yaw")) # rate
            self.maxThrust.setValue(Config().get("normal_max_thrust"))
            self.minThrust.setValue(Config().get("normal_min_thrust"))
            self.slewLimit.setValue(Config().get("normal_slew_limit"))
            self.thrustLoweringSlewRate.setValue(Config().get("normal_slew_rate"))

        if item == 1:
            self.maxAngle.setValue(Config().get("max_rp")) # rate
            self.maxYawAngle.setValue(Config().get("max_yaw")) # rate
            self.maxThrust.setValue(Config().get("max_thrust"))
            self.minThrust.setValue(Config().get("min_thrust"))
            self.slewLimit.setValue(Config().get("slew_limit"))
            self.thrustLoweringSlewRate.setValue(Config().get("slew_rate"))
            self.isInFlightmode = True

        if item == 1:
            STATE = True
        else:
            STATE = False
        self.maxAngle.setEnabled(STATE)
        self.maxYawAngle.setEnabled(STATE)
        self.maxThrust.setEnabled(STATE)
        self.minThrust.setEnabled(STATE)
        self.slewLimit.setEnabled(STATE)
        self.thrustLoweringSlewRate.setEnabled(STATE)

    def _inputDataUIUpdate(self, thrust, yaw, roll, pitch):
        self.targetThrust.setText(('%d' % thrust))
        self.targetYaw.setText(('%0.2f' % yaw))
        self.targetRoll.setText(('%0.2f' % roll))
        self.targetPitch.setText(('%0.2f' % pitch))

    def _imuLabelsEnabled(self, par):
        self.actualLabel.setEnabled(par)
        self.thrustLabel_1.setEnabled(par)
        self.m1Label.setEnabled(par)
        self.m2Label.setEnabled(par)
        self.m3Label.setEnabled(par)
        self.m4Label.setEnabled(par)

    def _imuUiUpdate(self, data):
        self.actualThrust.setText('%d' % data.thrust)
        self.actualPitch.setText('0.2f' % data.pitch)
        self.actualRoll.setText('0.2f' % data.roll)
        self.actualYaw.setText('0.2f' % data.yaw)

        self.thrustProgressBar.setValue(data.thrust)
        self.m1ProgressBar.setValue(data.motor1)
        self.m2ProgressBar.setValue(data.motor2)
        self.m3ProgressBar.setValue(data.motor3)
        self.m4ProgressBar.setValue(data.motor4)

        self.attitudeIndicator.setPitch(data.pitch)
        self.attitudeIndicator.setRoll(data.roll)




