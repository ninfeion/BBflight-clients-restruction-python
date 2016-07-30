# -*- coding: utf-8 -*-

"""Get accessing for joystick data read"""

import pygame
import logging
import json

from threading import Lock
from utils.callbacks import Caller
from config.bbconfig import Config
from utils.periodictimer import PeriodicTimer
from devices.joystickMapConfig import JoystickConfig

__author__ = 'Ninfeion'
__all__ = []

class JoystickReader(object):
    """ Thread that will read data from joystick and send data packet to BBflight.
        Initialize Device Firstly,Set Device,Set Mapping, start timer """

    def __init__(self):
        self._inputDevice = None
        self._mappingConfig = None
        self._mappingMutex = Lock()

        if Config().get("flightmode") == 'Normal':
            self.minThrust = Config().get("normal_min_thrust")
            self.maxThrust = Config().get("normal_max_thrust")
            self.maxAngle = Config().get("normal_max_rp")
            self.maxYawAngle = Config().get("normal_max_yaw")
            self.slewLimit = Config().get("normal_slew_limit")
            self.thrustLoweringSlewRate = Config().get("normal_slew_rate")
        else:
            self.minThrust = Config().get("min_thrust")
            self.maxThrust = Config().get("max_thrust")
            self.maxAngle = Config().get("max_rp")
            self.maxYawAngle = Config().get("max_yaw")
            self.slewLimit = Config().get("slew_limit")
            self.thrustLoweringSlewRate = Config().get("slew_rate")

        self.inputUpdated = Caller()
        self.rpTrimUpdated = Caller()
        self.eStopUpdated = Caller()
        self.exitAppUpdated = Caller()
        self.altholdUpdated = Caller()

        self._joystickDetectEnabled = False
        self.rawDataForDetect = Caller()

        self.readTimer = PeriodicTimer(0.01, self.readInput)

    def initDevice(self):
        pygame.quit()
        pygame.joystick.quit()
        pygame.init()
        pygame.joystick.init()
        logging.debug("Joystick system initializing done")

        return pygame.joystick.get_count()

    def setDevice(self, deviceid):
        # TODO: deviceid should be a value from 0 to count-1
        if pygame.joystick.get_init() == True:
            self._inputDevice = pygame.joystick.Joystick(deviceid)
            self._inputDevice.init()
            return self._inputDevice.get_name()
        else:
            logging.info("Pygame joystick not initialized!")

    def disableDevice(self):
        if self._inputDevice:
            self._inputDevice.quit()
            self._inputDevice = None

    def setMapping(self, filename):
        """ Accept a config file name and set the current config.
            Return a dict. """
        self._mappingMutex.acquire()
        self._mappingConfig = JoystickConfig().getConfig(filename)
        self._mappingMutex.release()

    def readRawData(self):
        if self._inputDevice.get_init() == True:
            pygame.event.get()

            axis = []
            hat = []
            button = []
            for i in range(self._inputDevice.get_numaxes()):
                axis.append(self._inputDevice.get_axis(i))
            for i in range(self._inputDevice.get_numhats()):
                hat.append(self._inputDevice.get_hat(i))
            for i in range(self._inputDevice.get_numbuttons()):
                button.append(self._inputDevice.get_button(i))
            if self._joystickDetectEnabled:
                self.rawDataForDetect.call([axis, button])
            return {'axis': axis, 'button': button, 'hat': hat}
        else:
            logging.debug("Class Joystick not initialized!")
            return None

    def setDetectEnabled(self, par):
        self._joystickDetectEnabled = par

    def readInput(self):
        rawData = self.readRawData()
        inputData = {}

        self._mappingMutex.acquire()
        if rawData:
            for d in rawData:
                if d == 'axis':
                    for i in range(len(rawData[d])):
                        if ('Input.AXIS-%d'%i) in self._mappingConfig:
                            if self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'thrust':
                                if Config().get('thrustmode') == 'Linear':
                                    inputData['thrust'] = rawData[d][i] * 1000 + 1000
                                elif Config().get('thrustmode') == 'Quadratic':
                                    if rawData[d][i] >= 0:
                                        inputData['thrust'] = rawData[d][i] **2 * 1000 + 1000
                                    else:
                                        inputData['thrust'] = rawData[d][i] **2 * -1000 + 1000
                                inputData['thrust'] = inputData['thrust'] / 2000 * (
                                    self.maxThrust - self.minThrust) * 20 + self.minThrust *20
                                # Or:inputData['thrust'] = self.maxThrust *20 - inputData['thrust'] /(
                                # 2000 * (self.maxThrust - self.minThrust) * 20)
                            elif self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'yaw':
                                inputData['yaw'] = rawData[d][i] * 180
                                trimVal = Config().get("trim_yaw")
                                if abs(inputData['yaw']) < trimVal:
                                    inputData['yaw'] = 0
                                else:
                                    if inputData['yaw'] >= 0:
                                        inputData['yaw'] = (inputData['yaw'] - trimVal) / (
                                            180.0 - trimVal) * self.maxYawAngle
                                    else:
                                        inputData['yaw'] = (inputData['yaw'] + trimVal) / (
                                            180.0 - trimVal) * self.maxYawAngle
                            elif self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'roll':
                                inputData['roll'] = - rawData[d][i] * 180
                                trimVal = Config().get("trim_roll")
                                if abs(inputData['roll']) < trimVal:
                                    inputData['roll'] = 0
                                else:
                                    if inputData['roll'] >= 0:
                                        inputData['roll'] = (inputData['roll'] - trimVal) / (
                                        180.0 - trimVal) * self.maxAngle
                                    else:
                                        inputData['roll'] = (inputData['roll'] + trimVal) / (
                                        180.0 - trimVal) * self.maxAngle
                            elif self._mappingConfig['Input.AXIS-%d'%i]['key'] == 'pitch':
                                inputData['pitch'] = rawData[d][i] * 180
                                trimVal = Config().get("trim_pitch")
                                if abs(inputData['pitch']) < trimVal:
                                    inputData['pitch'] = 0
                                else:
                                    if inputData['pitch'] >= 0:
                                        inputData['pitch'] = (inputData['pitch'] - trimVal) / (
                                        180.0 - trimVal) * self.maxAngle
                                    else:
                                        inputData['pitch'] = (inputData['pitch'] + trimVal) / (
                                        180.0 - trimVal) * self.maxAngle
                #if d == 'hat':
                    #for i in range(len(rawData[d])):
                        #if ('Input.HAT-%d'%i) in self._mappingConfig:
                            #if self._mappingConfig['Input.HAT-%d'%i]['key'] == 'pitchNeg':
                            #    inputData['pitchNeg'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'pitchPos':
                            #    inputData['pitchPos'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'rollNeg':
                            #    inputData['rollNeg'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'rollPos':
                            #    inputData['rollPos'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'estop':
                            #    inputData['estop'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'althold':
                            #    inputData['althold'] = rawData[d][i]
                            #elif self._mappingConfig['Input.HAT-%d'%i]['key'] == 'exitapp':
                            #    inputData['exitapp'] = rawData[d][i]
                if d == 'button':
                    for i in range(len(rawData[d])):
                        if ('Input.BUTTON-%d'%i) in self._mappingConfig:
                            if self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'pitchNeg':
                                inputData['pitchNeg'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'pitchPos':
                                inputData['pitchPos'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'rollNeg':
                                inputData['rollNeg'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'rollPos':
                                inputData['rollPos'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'estop':
                                inputData['estop'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'althold':
                                inputData['althold'] = rawData[d][i]
                            elif self._mappingConfig['Input.BUTTON-%d'%i]['key'] == 'exitapp':
                                inputData['exitapp'] = rawData[d][i]
            self._mappingMutex.release()
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

    def resetMappingAfterLoadConfig(self, type, key, tarid):
        self._mappingMutex.acquire()
        if ("%s-%d" % (type, tarid)) in self._mappingConfig:
            for d in self._mappingConfig:
                if self._mappingConfig[d]["key"] == key:
                    (self._mappingConfig[d],
                    self._mappingConfig["%s-%d" % (type, tarid)]) = (
                    self._mappingConfig["%s-%d" % (type, tarid)],
                    self._mappingConfig[d])
                    (self._mappingConfig[d]['id'],
                    self._mappingConfig["%s-%d" % (type, tarid)]['id']) = (
                    self._mappingConfig["%s-%d" % (type, tarid)]['id'],
                    self._mappingConfig[d]['id'])
        else:
            for d in self._mappingConfig:
                if self._mappingConfig[d]["key"] == key:
                    del(self._mappingConfig[d])
                    break
            self._mappingConfig["%s-%d" % (type, tarid)] = {"scale": 1.0,
                                                            "type": type,
                                                            "id": tarid,
                                                            "key": key,
                                                            "name": key}
        self._mappingMutex.release()

    def saveConfig(self, filename):
        config = {'inputconfig': {'inputdevice': {'updateperiod': 10,
                                                  'name': self._inputDevice.get_name(),
                                                  'axis': [],
                                                  'hat': [],
                                                  'button': []}}}
        self._mappingMutex.acquire()
        for d in self._mappingConfig:
            if self._mappingConfig[d]["type"] == "Input.AXIS":
                config['inputconfig']['inputdevice']['axis'].append(self._mappingConfig[d])
            elif self._mappingConfig[d]["type"] == "Input.BUTTON":
                config['inputconfig']['inputdevice']['button'].append(self._mappingConfig[d])
            #elif self._mappingConfig[d]["type'] == "Input.HAT"
        self._mappingMutex.release()
        filedir = JoystickConfig().configsDir + "/%s.json" % filename
        json_data = open(filedir, 'w')
        json_data.write(json.dumps(config, indent=2))
        json_data.close()
        logging.info("Saving config to [%s]", filename)
        JoystickConfig().readConfigFile()
        self.setMapping(filename)



