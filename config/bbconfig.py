# -*- coding: utf-8 -*-

"""BBFlight Config And Configuration Files(json) Relating Method """

import os
import json
import logging

from utils.singleton import Singleton

__author__ = 'Ninfeion'
__all__ = []

class Config(metaclass=Singleton):

    def __init__(self):
        self._configDir = os.path.dirname(__file__) + '/bbconfig.json'

        [self._readonly, self._writable] = self._readDistfile()

    def _readDistfile(self):
        """ Read the distribution config file containing the defaults """
        file = open(self._configDir, 'r')
        data = json.load(file)
        file.close()
        logging.info("BB Config read from %s" % self._configDir)

        return [data["read-only"], data["writable"]]

    def set(self, key, value):
        """ Set the value of a config parameter """

        try:
            self._writable[key] = value
        except KeyError:
            logging.info("Couldn't set the parameter [%s]" % key)

    def get(self, key):
        """ Get the value of a config parameter """

        value = None
        if (key in self._writable):
            value = self._writable[key]
        elif (key in self._readonly):
            value = self._readonly[key]
        else:
            logging.info("Couldn't get the parameter [%s]" % key)

        #if not isinstance(value, str):
            #value = str(value)
        return value

    def saveFile(self):
        """ Save the user config to file """
        configTemp = {}
        configTemp["writable"] = self._writable
        configTemp["read-only"] = self._readonly
        jsonFile = open(self._configDir, 'w')
        jsonFile.write(json.dumps(configTemp, indent=2))
        jsonFile.close()
        logging.info("Config file saved to [%s]" % self._configDir)





