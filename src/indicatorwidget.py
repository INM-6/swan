#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:27:23 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph import mkColor

class IndicatorWidget(QtGui.QWidget):
    """
    A class based on QWidget used to indicate the row/column.
    """
    
    selectIndicator = QtCore.pyqtSignal(object)
    
    def __init__(self, text, row = 0, col = 0, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        self._defSize = (200, 150)
        self._constDim = 60
        self._row = row
        self._col = col
        self._pos = (self._row, self._col)
        self.selected = True
        
        gridLayout = QtGui.QGridLayout(self)
        gridLayout.setObjectName("indicatorGridLayout")
        self.setLayout(gridLayout)
        
        self.dispText = QtWidgets.QLabel()
        self.dispText.setObjectName("dispText")
        self.dispText.setText(text)
        self.dispText.setIndent(0)
        self.dispText.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.dispText.setScaledContents(False)
        self.dispText.setWordWrap(True)
        
        gridLayout.addWidget(self.dispText, 0, 0)
        
        self.colourStrip = QtGui.QLabel()
        self.colourStrip.setObjectName("colourStrip")
        self.colourStrip.setAutoFillBackground(True)
        self.colourStrip.setIndent(0)
        self.colourStrip.setMargin(0)
        self.colourStrip.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        gridLayout.addWidget(self.colourStrip, 0, 1)
        self.colourStrip.hide()
        
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 0)
        gridLayout.setSpacing(0)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        
        self.setSize()
        
        self.dispFont = self.dispText.font()
        self.setFontSize()
        
        self.bgs = {"selected":mkColor('w'), "deselected":mkColor(0.8), "inFocus":mkColor(0.9)}
        self._bg = self.bgs["selected"]
        
        self.setAutoFillBackground(True)
        
        self.setBackground(self._bg)
    
    def change_size(self, width, height):
        """
        Resizes the plot by the given steps.
        
        **Arguments**
        
            *width* (float):
                The change step percentage for the width.
            *height* (float):
                The change step percentage for the height.
        
        """
        oldw = float(self.size().width())
        oldh = float(self.size().height())
        
        if self._row == 0 and self._col > 0:
            neww = int(oldw + oldw*(width/100.0))
            if neww > 0:
                self.setFixedSize(neww, oldh)
        elif self._col == 0 and self._row > 0:
            newh = int(oldh + oldh*(height/100.0))
            if newh > 0:
                self.setFixedSize(oldw, newh)
        
        self.setFontSize()
    
    def setSize(self):
        if self._row == 0 and self._col == 0:
            self.setFixedSize(self._constDim, self._constDim)
        elif self._row == 0 and self._col > 0:
            self.setFixedSize(self._defSize[0], self._constDim)
        elif self._col == 0 and self._row > 0:
            self.setFixedSize(self._constDim, self._defSize[1])
    
    def setBackground(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
    
    def setFontSize(self):
        if self._row == 0 and self._col == 0:
            self.dispFont.setPointSize(0.13 * min(self.size().height(), self.size().width()))
            self.dispFont.setBold(True)
        elif self._row > 0:
            self.dispFont.setPointSize(0.19 * min(self.size().height(), self.size().width()))
        elif self._col > 0:
            self.dispFont.setPointSize(0.18 * min(self.size().height(), self.size().width()))
        self.dispText.setFont(self.dispFont)
        
    def toggleColourStrip(self, colour):
        palette = self.colourStrip.palette()
        palette.setColor(self.backgroundRole(), colour)
        self.colourStrip.setPalette(palette)
        self.colourStrip.show()
    
    def darkTheme(self):
        self.bgs = {"deselected":mkColor(0.3), "selected":mkColor('k'), "inFocus":mkColor(0.1)}
        self._bg = self.bgs["selected"]
        self.setBackground(self._bg)
    
    ### Mouse Interactions ###
    
    def mousePressEvent(self, event):
        """
        This method is called you click on this widget.
        
        The event will be accepted if you click with the
        left mouse button.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.selectIndicator.emit(self)
            self.selected = not self.selected
            if self.selected:
                self._bg  = self.bgs["selected"]
            elif not self.selected:
                self._bg = self.bgs["deselected"]
            
            self.setBackground(self._bg)
            event.accept()
        else:
            event.ignore()
        
    def mouseMoveEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        #super(PlotWidget, self).mouseMoveEvent(event)
        event.accept()
     
    def mouseReleaseEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        #super(PlotWidget, self).mouseReleaseEvent(event)
        event.accept()
        
    def enterEvent(self, event):
        """
        This method is called the mouse enters this widget.
        
        Sets this widget in focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        self.inFocus = True
        self.setBackground(self.bgs["inFocus"])
        event.accept()
    
    def leaveEvent(self, event):
        """
        This method is called the mouse leaves this widget.
        
        Sets this widget out of focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        self.inFocus = False
        self.setBackground(self._bg)
        event.accept()