# -*- coding: utf-8 -*-

"""Get accessing for joystick data read"""

import pygame

from config.bbconfig import Config
from devices.joystickMapConfig import JoystickConfig

__author__ = 'Ninfeion'
__all__ = []

class JoystickReader(object):
    """ Thread that will read data from joystick and send data packet to BBflight. """

    inputConfig = []

    def __init__(self):
        self._inputDevice = None

        self.minThrust = 0
        self.maxThrust = 0

        self.trimRoll = Config().get("trim_roll")
        self.trimPitch = Config().get("trim_pitch")
        self.trimYaw = Config().get("trim_yaw")

