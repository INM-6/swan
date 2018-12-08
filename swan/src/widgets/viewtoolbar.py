#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 12:20:53 2017

@author: Shashwat Sridhar
"""

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

class ViewToolbar(QtWidgets.QWidget):
    
    doLayer = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        
        QtWidgets.QWidget.__init__(self, parent = parent)
        
        self.mainGridLayout = QtGui.QGridLayout(self)
        self.colWidg = collapsibleWidget(parent = self, title = "Tools", animationDuration=300)
        self.mainGridLayout.addWidget(self.colWidg, 0, 0)
        
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("viewToolbarGridLayout")
        
        self.layers = QtGui.QGroupBox("Active")
        self.layers.setObjectName("Layers")
        self.layersLayout = QtGui.QGridLayout()
        self.layersLayout.setContentsMargins(0, 0, 0, 0)
        self.layersLayout.setSpacing(0)
        self.layers.setLayout(self.layersLayout)
        self.layers.setCheckable(True)
        self.layers.setChecked(False)
        self.layers.toggled.connect(self.refreshLayers)
        self.gridLayout.addWidget(self.layers, 0, 0)
        
        self.options = QtGui.QGroupBox("Options")
        self.optionsLayout = QtGui.QGridLayout()
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setSpacing(0)
        self.options.setLayout(self.optionsLayout)
        self.gridLayout.addWidget(self.options, 0, 1)
        
        self.gridLayout.setColumnStretch(1, 2)
        
        self.mainGridLayout.setContentsMargins(0, 0, 0, 0)
        self.mainGridLayout.setSpacing(0)
        
        self.layerItems = []
    
    def setupRadioButtons(self, layers):
        for layer in layers:
            rButton = QtGui.QRadioButton(layer)
            rButton.toggled.connect(self.refreshLayers)
            self.layerItems.append(rButton)
            
            self.layersLayout.addWidget(rButton)
            if len(self.layerItems) == 1:
                rButton.setChecked(True)
    
    def setupCheckboxes(self, layers):
        for l, layer in enumerate(layers):
            cBox = QtGui.QCheckBox(layer)
            cBox.toggled.connect(self.refreshLayers)
            self.layerItems.append(cBox)
            
            self.layersLayout.addWidget(cBox)
            if l == 0:
                cBox.setChecked(True)
    
    def getCheckedLayers(self):
        checkedLayers = []
        if self.layerItems:
            for item in self.layerItems:
                if item.isChecked():
                    checkedLayers.append(str(item.text()))
        return checkedLayers
    
    def refreshLayers(self):
        self.doLayer.emit()


class collapsibleWidget(QtGui.QWidget):
    def __init__(self, parent=None, title='', animationDuration=300):
        """
        References:
            # Adapted from the StackOverflow answer
            https://stackoverflow.com/a/37927256/7126611
            
            # which adapted it from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(collapsibleWidget, self).__init__(parent=parent)

        self.animationDuration = animationDuration
        self.toggleAnimation = QtCore.QParallelAnimationGroup()
        self.contentArea = QtGui.QScrollArea()
        self.headerLine = QtGui.QFrame()
        self.toggleButton = QtGui.QToolButton()
        self.mainLayout = QtGui.QGridLayout()

        toggleButton = self.toggleButton
        toggleButton.setStyleSheet("QToolButton { border: none; }")
        toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggleButton.setArrowType(QtCore.Qt.RightArrow)
        toggleButton.setText(str(title))
        toggleButton.setCheckable(True)
        toggleButton.setChecked(False)

        headerLine = self.headerLine
        headerLine.setFrameShape(QtGui.QFrame.HLine)
        headerLine.setFrameShadow(QtGui.QFrame.Sunken)
        headerLine.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea {border: none; }")
        self.contentArea.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggleAnimation = self.toggleAnimation
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight", self))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight", self))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self.contentArea, b"minimumHeight", self.contentArea))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self.contentArea, b"maximumHeight", self.contentArea))
        # don't waste space
        mainLayout = self.mainLayout
        #mainLayout.setVerticalSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
            direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
            toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)

    def setContentLayout(self, contentLayout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight() + 1
        contentHeight = contentLayout.sizeHint().height()
        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)
    