#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 23:08:03 2017

@author: sridhar
"""

from PyQt5 import QtGui, QtWidgets
import pyqtgraph.opengl as gl
from numpy import array

class PyQtWidget3d(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
        
        QtGui.QWidget.__init__(self, parent=parent)
        
        vgl = QtGui.QGridLayout(self)
        self.vgl = vgl
        
        self.pgCanvas = gl.GLViewWidget()
        self.pgCanvas.setBackgroundColor('k')
        
        self.vgl.addWidget(self.pgCanvas, 1, 1, 1, 1)
        self.setLayout(self.vgl)
        
        self.scatterPlot = None
        
        self.setup_axes(glOptions='translucent')
            
    def setup_axes(self, size = None, spacing = None, glOptions='additive'):
        
        if size is None:
            xg = gl.GLGridItem(size = QtGui.QVector3D(3000, 3000, 3000), glOptions=glOptions)
            
            yg = gl.GLGridItem(size = QtGui.QVector3D(3000, 3000, 3000), glOptions=glOptions)
            
            zg = gl.GLGridItem(size = QtGui.QVector3D(3000, 3000, 3000), glOptions=glOptions)
        
        else:
            xg = gl.GLGridItem(size = size, glOptions=glOptions)
            
            yg = gl.GLGridItem(size = size, glOptions=glOptions)
            
            zg = gl.GLGridItem(size = size, glOptions=glOptions)
            
        if spacing is None:
            xg.setSpacing(spacing = QtGui.QVector3D(100, 100, 100))
            
            yg.setSpacing(spacing = QtGui.QVector3D(100, 100, 100))
            
            zg.setSpacing(spacing = QtGui.QVector3D(100, 100, 100))
        
        else:
            xg.setSpacing(spacing = spacing)
            
            yg.setSpacing(spacing = spacing)
            
            zg.setSpacing(spacing = spacing)
            
        xg.rotate(90, 0, 1, 0)
        zg.rotate(90, 1, 0, 0)
        
        self.pgCanvas.addItem(xg)
        self.pgCanvas.addItem(yg)
        self.pgCanvas.addItem(zg)
    
    def addScatterPlotItem(self, plotItem = None, setGLOptions = 'additive'):
        if plotItem is None:
            self.scatterPlot = gl.GLScatterPlotItem(pos = array([0, 0, 0]), size = 1, color = (0.5, 0.5, 0.5, 0.5), pxMode = True)
        else:
            plotItem.setGLOptions(setGLOptions)
            self.pgCanvas.addItem(plotItem)
    
    def createScatterPlotItem(self, pos, size, color, pxMode = True):
        return gl.GLScatterPlotItem(pos = pos, size = size, color = color, pxMode = pxMode)
    
    def cameraPosition(self, distance = None, elevation = None, azimuth = None):
        self.pgCanvas.setCameraPosition(self, distance = distance, elevation = elevation, azimuth = azimuth)
    
    def reset_plot(self):
        self.pgCanvas.items = []
        self.setup_axes(glOptions='translucent')
        
    def show_plot(self):
        self.pgCanvas.show()