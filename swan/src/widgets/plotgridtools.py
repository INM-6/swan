#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:38:37 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtWidgets
from swan.src.widgets.selectorwidget import SelectorWidget

class plotGridTools(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        
        self.selector = SelectorWidget(self)
        
        self.details = QtGui.QTableWidget(self)
        self.details.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.details.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.details.setWordWrap(True)
        self.details.setCornerButtonEnabled(False)
        self.details.setObjectName("Details")
        self.details.setColumnCount(1)
        self.details.setRowCount(5)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.details.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(1, 0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(2, 0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(3, 0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(4, 0, item)
        self.details.horizontalHeader().setStretchLastSection(True)
        self.details.verticalHeader().setStretchLastSection(True)
        self.details.setMaximumWidth(500)
        self.details.setMinimumWidth(0)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        self.details.setSizePolicy(sizePolicy)
        
        self.setup()
        
    def setup(self):
        
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.selector, 0, 0, 1, 1)
        self.layout.addWidget(self.details, 0, 1, 1, 1)
        
        self.setLayout(self.layout)