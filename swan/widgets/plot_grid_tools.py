#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:38:37 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

from swan.views.virtual_units_view import VirtualUnitsView
from swan.widgets.selector_widget import SelectorWidget


class PlotGridTools(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        
        self.layout = QtWidgets.QHBoxLayout()
        
        self.selector = SelectorWidget(self)
        self.virtual_unit_map = VirtualUnitsView(self)

        self.selector.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        self.virtual_unit_map.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        
        self.layout.addWidget(self.selector, 1)
        self.layout.addWidget(self.virtual_unit_map, 1)

        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(self.layout)
