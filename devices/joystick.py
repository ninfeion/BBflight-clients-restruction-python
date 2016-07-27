# -*- coding: utf-8 -*-

"""Get accessing for joystick data read"""

import pygame
import logging

from utils.callbacks import Caller
from config.bbconfig import Config
from utils.periodictimer import PeriodicTimer
from devices.joystickMapConfig import JoystickConfig

__author__ = 'Ninfeion'
__all__ = []

class JoystickReader(object):
    """ Thread that will read data from joystick and send data packet to BBflight.
        Set Mapping Firstly,Initialize Device,Set Device. """

    def __init__(self):
        self._inputDevice = None
        self._mappingConfig = None

        self.minThrust = 0
        self.maxThrust = 0

        self.trimRoll = Config().get("trim_roll")
        self.trimPitch = Config().get("trim_pitch")
        self.trimYaw = Config().get("trim_yaw")

        JoystickConfig.readConfigFile()

        self.inputUpdated = Caller()
        self.rpTrimUpdated = Caller()
        self.eStopUpdated = Caller()
        self.exitAppUpdated = Caller()
        self.altholdUpdated = Caller()

        self._readTimer = PeriodicTimer(0.01, self.readInput)

    def initDevice(self):
        pygame.quit()
        pygame.joystick.quit()
        pygame.init()
        pygame.joystick.init()

        return pygame.joystick.get_count()

    def setDevice(self, deviceid):
        # TODO: deviceid should be a value from 0 to count-1
        if pygame.joystick.get_init() == True:
            self._inputDevice = pygame.joystick.Joystick(deviceid)
            self._inputDevice.init()
            return self._inputDevice.get_name()
        else:
            logging.debug("Pygame joystick not initialized!")

    def disableDevice(self):
        if self._inputDevice:
            self._inputDevice.quit()
            self._inputDevice = None

    def setMapping(self, filename):
        """ Accept a config file name and set the current config.
            Return a dict. """
        self._mappingConfig = JoystickConfig.getConfig(filename)

    def readRawData(self):
        if self._inputDevice.get_init() == True:
            pygame.event.get()

            axis = []
            hat = []
            button = []

            for i in range(self._inputDevice.get_numaxes()):
                axis[i] = self._inputDevice.get_axis[i]
            for i in range(self._inputDevice.get_numhats()):
                hat[i] = self._inputDevice.get_hat[i]
            for i in range(self._inputDevice.get_numbuttons()):
                button[i] = self._inputDevice.get_button[i]

            return {'axis': axis, 'button': button, 'hat': hat}
        else:
            logging.debug("Class Joystick not initialized!")
            return None

    def readInput(self):
        rawData = self.readRawData()
        inputData = {}

        if rawData:
            for d in rawData:
                if d == 'axis':
                    for i in range(len(rawData[d])):
                        if self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'thrust':
                            inputData['thrust'] = rawData[d][i]
                        if self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'yaw':
                            inputData['yaw'] = rawData[d][i]
                        if self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'roll':
                            inputData['roll'] = rawData[d][i]
                        if self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'pitch':
                            inputData['pitch'] = rawData[d][i]

                if d == 'hat':
                    for i in range(len(rawData[d])):
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'pitchNeg':
                            inputData['pitchNeg'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'pitchPos':
                            inputData['pitchPos'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'rollNeg':
                            inputData['rollNeg'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'rollPos':
                            inputData['rollPos'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'estop':
                            inputData['estop'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'althold':
                            inputData['althold'] = rawData[d][i]
                        if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'exitapp':
                            inputData['exitapp'] = rawData[d][i]

                if d == 'button':
                    for i in range(len(rawData[d])):
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'pitchNeg':
                            inputData['pitchNeg'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'pitchPos':
                            inputData['pitchPos'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'rollNeg':
                            inputData['rollNeg'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'rollPos':
                            inputData['rollPos'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'estop':
                            inputData['estop'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'althold':
                            inputData['althold'] = rawData[d][i]
                        if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'exitapp':
                            inputData['exitapp'] = rawData[d][i]

            self.inputUpdated.call(inputData['thrust'],
                                   inputData['yaw'],
                                   inputData['roll'],
                                   inputData['pitch'])
            self.rpTrimUpdated.call(inputData['pitchNeg'],
                                    inputData['pitchPos'],
                                    inputData['rollNeg'],
                                    inputData['rollPos'])
            self.eStopUpdated.call(inputData['estop'])
            self.exitAppUpdated.call(inputData['exitapp'])
            self.altholdUpdated.call(inputData['althold'])














