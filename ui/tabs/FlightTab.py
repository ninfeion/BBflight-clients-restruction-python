# -*- coding: utf-8 -*-

import logging
import os

from ui.widgets.attitudeIndicator import AttitudeIndicator
from ui.tab import Tab

from PyQt5 import uic

flight_tab_class = uic.loadUiType(os.path.dirname(__file__) + '/flightTab.ui')[0]

class FlightTab(Tab, flight_tab_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabName = 'Flight Control'

        self.attitudeIndicator = AttitudeIndicator()
        self.verticalLayout_3.addWidget(self.attitudeIndicator)
        self.splitter.setSizes([1000, 1])

