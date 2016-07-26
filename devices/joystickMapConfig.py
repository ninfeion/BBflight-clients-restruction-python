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

class JoystickManager(metaclass=Singleton):
    configsDir = os.path.dirname(__file__)

    def __init__(self):
        """ Initialize and create empty config list """
        self._listOfConfigs = []

    def getConfig(self, configname):
        """ Get the button and axis mappings for an input device. """
        try:
            idx = self._listOfConfigs.index(configname)
            return self._inputConfig[idx]
        except:
            return None

    def getSettings(self, configname):
        """ Get the settings for an input device. """
        try:
            idx = self._listOfConfigs.index(configname)
            return self._inputSettings[idx]
        except:
            return None

    def getListOfConfigs(self):
        """ Reload the configurations from file. """
        try:
            configs = [os.path.basename(fileDir) for fileDir in
                       glob.glob(self.configsDir + '/[A-Za-z]*.json')]
            # configs is a list of config file name
            self._inputConfig = []
            self._inputSettings = []
            self._listOfConfigs = []
            for conf in configs:
                logging.debug("Parsing [%s]", conf)
                jsonData = open(self.configsDir + "/%s" % conf)
                data = json.load(jsonData)
                newInputDevice = {}
                newInputSettings = {'updateperiod': 10, 'springythrottle': True}
                for s in data['inputconfig']['inputdevice']:
                    if s == 'axis':
                        for a in data['inputconfig']['inputdevice']['axis']:
                            # ['axis'] including a list that is iterable
                            axis = {}
                            axis['scale'] = a['scale']
                            axis['offset'] = a['offset'] if 'offset' in a else 0.0
                            axis['type'] = a['type']
                            axis['key'] = a['key']
                            axis['name'] = a['name']
                            try:
                                ids = a['ids']
                            except:
                                ids = [a['id']]
                            for id in ids:
                                locaxis = copy.deepcopy(axis)
                                if 'ids' in a:
                                    if id == a['ids'][0]:
                                        locaxis['scale'] = locaxis['scale'] * -1
                                locaxis['id'] = id
                                # 'type'-'id' defines unique index for axis
                                index = '%s-%d' % (a['type'], id)
                                newInputDevice[index] = locaxis
                    else:
                        newInputSettings[s] = data['inputconfig']['inputdevice'][s]
                self._inputConfig.append(newInputDevice)
                self._inputSettings.append(newInputSettings)
                jsonData.close()
                self._listOfConfigs.append(conf[:-5])
        except Exception as e:
            logging.warning('Exception while parsing inputconfig file: %s', e)
        return self._listOfConfigs