# -*- coding: utf-8 -*-

""" Create Or Analyze Commander Send Or Recieve. """

import struct
import logging
from utils.callbacks import Caller
from utils.periodictimer import PeriodicTimer


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

    def setRPTrim(self, pitchNeg, pitchPos, rollNeg, rollPos):
        self.pitchNeg = pitchNeg
        self.pitchPos = pitchPos
        self.rollNeg = rollNeg
        self.rollPos = rollPos

    def setEStop(self, enabled):
        self.estop = enabled

    def setTryConnect(self, enabled):
        self.tryConnect = enabled

    def setAltHold(self, enabled):
        self.altHold = enabled


class ImuData(object):
    yaw = 0.0
    pitch = 0.0
    roll = 0.0
    thrust = 0

    broVal = 0.0

    motor1 = 0
    motor2 = 0
    motor3 = 0
    motor4 = 0


class Commander(object):

    def __init__(self, radiodev, serialclass):
        self._radio = radiodev
        self._bbSerial = serialclass
        self._isXMode = False

        self.txEnabledMonitor = True

        self.comRxTimer = PeriodicTimer(0.05, self.analyzeThread)
        self.comTxTimer = PeriodicTimer(0.2, self.comSendThread)

        self.imuDataUpdate = Caller()
        self.batteryUpdate = Caller()
        self.linkQualityUpdate = Caller()
        self.flightConnectionUpdate = Caller()
        self.haveBroDetected = Caller()

        self.rawRecieveUpdate = Caller()

    def setXMode(self, enabled):
        self._isXMode = enabled

    def analyzeThread(self):
        data = self._bbSerial.read(self._bbSerial.in_waiting)
        if data:
            self.rawRecieveUpdate.call(data)
            try:
                okdata = struct.unpack('<BBhfffBBBBHBBf??BB', data[:32])
                if okdata[0] == 0xaa and okdata[-1] == 0xff:
                    self.txEnabledMonitor = True
                    imuReturnData = ImuData()
                    imuReturnData.thrust = okdata[2]
                    imuReturnData.roll = okdata[3]
                    imuReturnData.pitch = okdata[4]
                    imuReturnData.yaw = okdata[5]
                    imuReturnData.motor1 = okdata[6]
                    imuReturnData.motor2 = okdata[7]
                    imuReturnData.motor3 = okdata[8]
                    imuReturnData.motor4 = okdata[9]
                    batteryData = okdata[10]
                    linkQuality = (100 - okdata[11]) #lostpacket equal to linkquality
                    resevered = okdata[12]
                    imuReturnData.broVal = okdata[13]
                    haveBro = okdata[14]
                    flightConnection = okdata[15]

                    self.haveBroDetected.call(haveBro)
                    self.imuDataUpdate.call(imuReturnData)
                    self.batteryUpdate.call(batteryData)
                    self.linkQualityUpdate.call(linkQuality)
                    self.flightConnectionUpdate.call(flightConnection)
            except:
                logging.debug('Recieve Command Data Abandon:')
                import binascii
                abandonData = binascii.b2a_hex(data).decode('ascii')
                string = ""
                while len(abandonData):
                    string = string + "\\x" + abandonData[:2]
                    abandonData = abandonData[2:]
                logging.debug(string)

    def comSendThread(self):
        if self._isXMode:
            roll, pitch = (0.707 * (self._radio.roll - self._radio.pitch),
                           0.707 * (self._radio.roll + self._radio.pitch))
        else:
            roll, pitch = self._radio.roll, self._radio.pitch

        dataPacket = struct.pack('<BBBBBBBBhfffBBBBBBBBBB',
                                 0xaa,
                                 0xaa,
                                 self._radio.devAdd[0],
                                 self._radio.devAdd[1],
                                 self._radio.devAdd[2],
                                 self._radio.devAdd[3],
                                 self._radio.devAdd[4],
                                 self._radio.tryConnect,
                                 self._radio.thrust,
                                 roll,
                                 pitch,
                                 self._radio.yaw,
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
        if self.txEnabledMonitor == True:
            self._bbSerial.write(dataPacket)
            self.txEnabledMonitor = False

