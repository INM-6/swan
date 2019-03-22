#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:19:42 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtWidgets, QtCore

class Ui_isiOptions(QtWidgets.QWidget):
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent = parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.setupUi(parent)
        
    def setupUi(self, isiWidget):
        
        self.ggl = QtGui.QGridLayout(self)
        w = QtGui.QWidget()
        y = QtGui.QWidget()
        l1 = QtGui.QLabel("Bin Max (ms):")
        l2 = QtGui.QLabel("Bin Step (ms):")
        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
        self.ghl1 = QtGui.QHBoxLayout(w)
        self.ghl2 = QtGui.QHBoxLayout(y)
        
        self.binMaxPlusBtn = QtGui.QPushButton("+")
        self.binMaxPlusBtn.setMinimumWidth(30)
        self.binMaxPlusBtn.setMaximumWidth(50)
        self.binMaxEdit = QtGui.QLineEdit()
        self.binMaxEdit.setMinimumWidth(30)
        self.binMaxEdit.setMaximumWidth(50)
        self.binMaxEdit.setText(str(isiWidget.binMax))
        self.binMaxMinusBtn = QtGui.QPushButton("-")
        self.binMaxMinusBtn.setMinimumWidth(30)
        self.binMaxMinusBtn.setMaximumWidth(50)
        self.binStepPlusBtn = QtGui.QPushButton("+")
        self.binStepPlusBtn.setMinimumWidth(30)
        self.binStepPlusBtn.setMaximumWidth(50)
        self.binStepEdit = QtGui.QLineEdit()
        self.binStepEdit.setMinimumWidth(30)
        self.binStepEdit.setMaximumWidth(50)
        self.binStepEdit.setText(str(isiWidget.binStep))
        self.binStepMinusBtn = QtGui.QPushButton("-")
        self.binStepMinusBtn.setMinimumWidth(30)
        self.binStepMinusBtn.setMaximumWidth(50)
        self.histStyleCheckbox = QtGui.QCheckBox()
        self.histStyleCheckbox.setText("Step Mode")
        self.histStyleCheckbox.setCheckState(QtCore.Qt.Unchecked)
        
        self.ghl1.addWidget(self.binMaxMinusBtn)
        self.ghl1.addWidget(self.binMaxEdit)
        self.ghl1.addWidget(self.binMaxPlusBtn)
        self.ghl2.addWidget(self.binStepMinusBtn)       
        self.ghl2.addWidget(self.binStepEdit)
        self.ghl2.addWidget(self.binStepPlusBtn)        
        
        self.ggl.addWidget(l1, 0, 0, 1, 2)
        self.ggl.addWidget(w, 0, 2, 1, 2)
        self.ggl.addWidget(l2, 1, 0, 1, 2)
        self.ggl.addWidget(y, 1, 2, 1, 2)
        self.ggl.addWidget(self.histStyleCheckbox, 0, 4, 1, 2)
        self.ggl.addWidget(self.errorLabel, 1, 4, 1, 2)
        
        isiWidget.toolbar.optionsLayout.addWidget(self)
        
        self.binMaxPlusBtn.clicked.connect(isiWidget.onMaxPlus)
        self.binMaxMinusBtn.clicked.connect(isiWidget.onMaxMinus)
        self.binStepPlusBtn.clicked.connect(isiWidget.onStepPlus)
        self.binStepMinusBtn.clicked.connect(isiWidget.onStepMinus)
        self.histStyleCheckbox.stateChanged.connect(isiWidget.stepModeChanged)
        
        self.binMaxEdit.textChanged.connect(isiWidget.binMaxChanged)
        self.binStepEdit.textChanged.connect(isiWidget.binStepChanged)
        self.binMaxEdit.returnPressed.connect(isiWidget.onEnter)
        self.binStepEdit.returnPressed.connect(isiWidget.onEnter)
        
        self.ggl.setContentsMargins(0, 0, 0, 0)
        self.ggl.setSpacing(0)
        
        isiWidget.toolbar.colWidg.setContentLayout(isiWidget.toolbar.gridLayout)
        isiWidget.toolbar.mainGridLayout.setContentsMargins(0, 0, 0, 0)
        isiWidget.toolbar.mainGridLayout.setSpacing(0)