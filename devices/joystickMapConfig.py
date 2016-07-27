# -*- coding: utf-8 -*-

"""
Manager for loading/accesing input device mappings.
"""

import json
import os
import glob
import logging
import copy

from utils.callbacks import Caller
from utils.singleton import Singleton

__author__ = 'Ninfeion'

class JoystickConfig(metaclass=Singleton):
    configsDir = os.path.dirname(__file__)

    def __init__(self):
        """ Initialize and create empty config list """
        self._listOfConfigs = []

    def getConfig(self, configname):
        """ Get the button and axis mappings for an input device. """
        try:
            idx = self._listOfConfigs.index(configname)
            return self._inputConfigs[idx]
        except:
            return None

    def getSettings(self, configname):
        """ Get the settings for an input device. """
        try:
            idx = self._listOfConfigs.index(configname)
            return self._inputSettings[idx]
        except:
            return None

    def readConfigFile(self):
        """ Reload the configurations from file. """
        try:
            configs = [os.path.basename(fileDir) for fileDir in
                       glob.glob(self.configsDir + '/*.json')]
            # configs is a list of config file name
            self._listOfConfigs = []
            self._inputSettings = []
            self._inputConfigs = []

            for conf in configs:
                logging.debug("Parsing [%s]", conf)
                jsonData = open(self.configsDir + "/%s" % conf)
                data = json.load(jsonData)

                newInputSettings = {}
                newInputConfigs = {}

                for sub in data['inputconfig']['inputdevice']:
                    if sub == 'updateperiod':
                        newInputConfigs['updateperiod'] = data['inputconfig'][
                            'inputdevice']['updateperiod']
                    if sub == 'name':
                        newInputConfigs['name'] = data['inputconfig'][
                            'inputdevice']['name']

                    if sub == 'axis':
                        for a in data['inputconfig']['inputdevice']['axis']:
                            index = '%s-%d' % (a['type'],a['id'])
                            newInputSettings[index] = a
                    if sub == 'hat':
                        for h in data['inputconfig']['inputdevice']['hat']:
                            index = '%s-%d' % (h['type'],h['id'])
                            newInputSettings[index] = h
                    if sub == 'button':
                        for b in data['inputconfig']['inputdevice']['button']:
                            index = '%s-%d' % (b['type'],b['id'])
                            newInputSettings[index] = b

                self._inputSettings.append(newInputSettings)
                self._inputConfigs.append(newInputConfigs)
                self._listOfConfigs.append(conf[:-5]) # cut out the extension name
                jsonData.close()
            return self._listOfConfigs
        except Exception as e:
            logging.warning('Exception while parsing inputconfig file: %s', e)
            return None
