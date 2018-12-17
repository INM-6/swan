#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:38:37 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from swan.src.widgets.selectorwidget import SelectorWidget

class plotGridTools(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        
        self.selector = SelectorWidget(self)

        self.details = QtGui.QTableWidget(self)
        self.details.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.details.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.details.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.details.setWordWrap(False)
        self.details.setCornerButtonEnabled(False)
        self.details.setObjectName("Details")
        self.details.setColumnCount(2)
        self.details.setRowCount(4)

        item = QtGui.QTableWidgetItem("Project File")
        self.details.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem("Working Directory")
        self.details.setItem(1, 0, item)
        item = QtGui.QTableWidgetItem("VUM File")
        self.details.setItem(2, 0, item)
        item = QtGui.QTableWidgetItem("Source Files")
        self.details.setItem(3, 0, item)

        item = QtGui.QTableWidgetItem(".")
        self.details.setItem(0, 1, item)
        item = QtGui.QTableWidgetItem(".")
        self.details.setItem(1, 1, item)
        item = QtGui.QTableWidgetItem(".")
        self.details.setItem(2, 1, item)
        item = QtGui.QTableWidgetItem(".")
        self.details.setItem(3, 1, item)

        self.details.horizontalHeader().setStretchLastSection(True)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        # self.details.setSizePolicy(sizePolicy)
        
        self.setup()
        
    def setup(self):
        
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.selector, 0, 0, 1, 1)
        self.layout.addWidget(self.details, 0, 1, 1, 1)
        
        self.setLayout(self.layout)