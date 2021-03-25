#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:38:37 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtWidgets

from swan.widgets.selector_widget import SelectorWidget


class PlotGridTools(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        
        self.layout = QtWidgets.QHBoxLayout()
        
        self.selector = SelectorWidget(self)

        self.selector.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        
        self.layout.addWidget(self.selector)

        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(self.layout)
