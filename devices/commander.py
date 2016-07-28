# -*- coding: utf-8 -*-

""" Create Or Analyze Commander Send Or Recieve. """

import struct
import queue

from utils.callbacks import Caller

class RadioDevice(object):
    def __init__(self):
        self.devName = None
        self.devAdd  = [0xff,
                         0xff,
                         0xff,
                         0xff,
                         0xff]
        self.estop = False

        self.thrust = 0
        self.yaw = 0.0
        self.roll = 0.0
        self.pitch = 0.0

        self.rollNeg = False
        self.rollPos = False
        self.pitchNeg = False
        self.pitchPos = False

        self.altHold = False
        self.tryConnect = False

    def setControlPar(self, thrust, yaw, roll, pitch):
        self.thrust = thrust
        self.yaw = yaw
        self.roll = roll
        self.pitch = pitch

    def setEStop(self, enabled):
        self.estop = enabled

    def setTryConnect(self, enabled):
        self.tryConnect = enabled

    def setAltHold(self, enabled):
        self.altHold = enabled


class Commander(object):

    def __init__(self, radiodev):
        self._radio = radiodev

        self._isXMode = False
        self._rxQueue = queue.Queue()

        self.imuDataUpdate = Caller()
        self.motorUpdate = Caller()

    def setXMode(self, enabled):
        self._isXMode = enabled

    def queueUpdate(self, bytesdate):


    def createCommander(self):

        if self._isXMode:
            roll, pitch = (0.707 * (self._radio.roll - self._radio.pitch),
                           0.707 * (self._radio.roll + self._radio.pitch))
        else:
            roll, pitch = self._radio.roll, self._isXMode.pitch

        dataPacket = struct.pack('<BBBBBBBBfffHBBBBBBBBBB',
                                 0xaa,
                                 0xaa,
                                 self._radio.devAdd[0],
                                 self._radio.devAdd[1],
                                 self._radio.devAdd[2],
                                 self._radio.devAdd[3],
                                 self._radio.devAdd[4],
                                 self._radio.tryConnect,
                                 roll,
                                 pitch,
                                 self._radio.yaw,
                                 self._radio.thrust,
                                 self._radio.estop,
                                 self._radio.altHold,
                                 self._radio.pitchNeg,
                                 self._radio.pitchPos,
                                 self._radio.rollNeg,
                                 self._radio.rollPos,
                                 0x00,
                                 0x00,
                                 0xff,
                                 0xff)
        return dataPacket

    def analyzeCommander(self):


        self.imuDataUpdate.call(thrust, yaw, roll, pitch)
        self.motorUpdate.call(m1Val, m2Val, m3Val, m4Val)

