#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 15:48:48 2018

@author: sridhar
"""
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph import ComboBox

class Ui_rpOptions(QtWidgets.QWidget):
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent = parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.setupUi(parent)
        
    def setupUi(self, rpWidget):
        
        #self.ggl = QtGui.QGridLayout(self)
        self.ggl = rpWidget.toolbar.optionsLayout
        l1 = QtGui.QLabel("Choose trigger event:")
        l2 = QtGui.QLabel("T-pre (ms): ")
        l3 = QtGui.QLabel("T-post (ms): ")
        l4 = QtGui.QLabel("Sampling Period (ms): ")
        l5 = QtGui.QLabel("Kernel Width (ms): ")
        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
        
        self.eventDropDown = ComboBox()
        self.eventDropDown.activated[str].connect(rpWidget.changeTriggerEvent)
        
        self.timePre = QtGui.QLineEdit()
        self.timePre.setMinimumWidth(30)
        self.timePre.setText(str(rpWidget.tPre))
        self.timePost = QtGui.QLineEdit()
        self.timePost.setMinimumWidth(30)
        self.timePost.setText(str(rpWidget.tPost))
        self.samplingPeriod = QtGui.QLineEdit()
        self.samplingPeriod.setMinimumWidth(50)
        self.samplingPeriod.setText(str(rpWidget.samplingPeriod))
        self.kernelWidth = QtGui.QLineEdit()
        self.kernelWidth.setMinimumWidth(50)
        self.kernelWidth.setText(str(rpWidget.kernelWidth))
        
        self.ggl.addWidget(l1, 0, 0, 1, 3)
        self.ggl.addWidget(self.eventDropDown, 0, 3, 1, 1)
        self.ggl.addWidget(l2, 0, 5, 1, 2)
        self.ggl.addWidget(self.timePre, 1, 5, 1, 2)
        self.ggl.addWidget(l3, 2, 5, 1, 2)
        self.ggl.addWidget(self.timePost, 3, 5, 1, 2)
        self.ggl.addWidget(l4, 0, 7, 1, 3)
        self.ggl.addWidget(self.samplingPeriod, 1, 7, 1, 3)
        self.ggl.addWidget(l5, 2, 7, 1, 3)
        self.ggl.addWidget(self.kernelWidth, 3, 7, 1, 3)
        self.ggl.addWidget(self.errorLabel, 1, 0, 1, 3)
        
        rpWidget.toolbar.optionsLayout.addWidget(self)
        
        self.timePre.textChanged.connect(rpWidget.onTPreChanged)
        self.timePost.textChanged.connect(rpWidget.onTPostChanged)
        self.samplingPeriod.textChanged.connect(rpWidget.onSamplingPeriodChanged)
        self.kernelWidth.textChanged.connect(rpWidget.onKernelWidthChanged)
        self.timePre.returnPressed.connect(rpWidget.onEnter)
        self.timePost.returnPressed.connect(rpWidget.onEnter)
        self.samplingPeriod.returnPressed.connect(rpWidget.onEnter)
        self.kernelWidth.returnPressed.connect(rpWidget.onEnter)
        
        self.ggl.setContentsMargins(0, 0, 0, 0)
        self.ggl.setHorizontalSpacing(20)
        
        rpWidget.toolbar.colWidg.setContentLayout(rpWidget.toolbar.gridLayout)
        rpWidget.toolbar.mainGridLayout.setContentsMargins(0, 0, 0, 0)
        rpWidget.toolbar.mainGridLayout.setSpacing(0)