#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 23:08:03 2017

@author: sridhar
"""

from PyQt5 import QtGui, QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from numpy import array

class PyQtWidget3d(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
        
        QtGui.QWidget.__init__(self, parent=parent)
        
        layout = QtGui.QGridLayout()
        self.layout = layout
        
        self.pgCanvas = gl.GLViewWidget()
        self.pgCanvas.setBackgroundColor(0.75)
        
        self.layout.addWidget(self.pgCanvas, 0, 0)
        self.setLayout(self.layout)
        
        self._axesGLOptions = 'translucent'
        
    def setup_axes(self, size = None, spacing = None, glOptions = 'translucent', axes = 'xyz'):
        
        if size is None:
            size = 3000
        if spacing is None:
            spacing = 100
            
        if 'x' in axes:
            xg = gl.GLGridItem(size = QtGui.QVector3D(size, size, size), glOptions=self._axesGLOptions)
            xg.setSpacing(spacing = QtGui.QVector3D(spacing, spacing, spacing))
            self.pgCanvas.addItem(xg)
        
        if 'y' in axes:
            yg = gl.GLGridItem(size = QtGui.QVector3D(size, size, size), glOptions=self._axesGLOptions)
            yg.setSpacing(spacing = QtGui.QVector3D(spacing, spacing, spacing))
            yg.rotate(90, 0, 1, 0)
            self.pgCanvas.addItem(yg)
            
        if 'z' in axes:
            zg = gl.GLGridItem(size = QtGui.QVector3D(size, size, size), glOptions=self._axesGLOptions)
            zg.setSpacing(spacing = QtGui.QVector3D(spacing, spacing, spacing))
            zg.rotate(90, 1, 0, 0)
            self.pgCanvas.addItem(zg)
        
        self.cameraPosition(distance=2*size, elevation = None, azimuth = None)
    
    def addScatterPlotItem(self, plotItem = None, setGLOptions = 'translucent'):
        if plotItem is None:
            self.pgCanvas.addItem(gl.GLScatterPlotItem(pos = array([0, 0, 0]), size = 1, color = (0.5, 0.5, 0.5, 0.5), pxMode = True))
        else:
            plotItem.setGLOptions(setGLOptions)
            self.pgCanvas.addItem(plotItem)
    
    def addSurfacePlotItem(self, surfaceItem):
        self.pgCanvas.addItem(surfaceItem)
    
    def createScatterPlotItem(self, pos, size, color, pxMode = True):
        return gl.GLScatterPlotItem(pos = pos, size = size, color = color, pxMode = pxMode)
    
    def createSurfacePlotItem(self, x, y, z, color, shader = 'shaded'):
        if x is not None and y is not None:
            return gl.GLSurfacePlotItem(x = x, y = y, z = z, color = color, shader = shader)
        elif x is None and y is None:
            return gl.GLSurfacePlotItem(z = z, color = color, shader = shader)
        else:
            raise ValueError("x and y must both be None or be 1D arrays of shape (z.shape[0], z.shape[1])")
    
    def cameraPosition(self, distance = None, elevation = None, azimuth = None):
        self.pgCanvas.setCameraPosition(self, distance = distance, elevation = elevation, azimuth = azimuth)
    
    def reset_plot(self):
        self.pgCanvas.items = []
        self.setup_axes(glOptions=self._axesGLOptions)
        
    def show_plot(self):
        self.pgCanvas.show()
        
    def setDark(self):
        self.pgCanvas.setBackgroundColor('k')

class PyQtWidget2d(QtWidgets.QWidget):
    
    sigClicked = QtCore.Signal(object)
    
    def __init__(self, parent = None):
        
        QtGui.QWidget.__init__(self, parent=parent)
        
        self.layout = QtGui.QGridLayout()
        
        self.pgCanvas = pg.PlotWidget(background='w')
        
        self.layout.addWidget(self.pgCanvas, 0, 0)
        self.setLayout(self.layout)
        
        self.selectedCurves = []
        
        self._home = None
        
    def showGrid(self):
        self.pgCanvas.plotItem.showGrid(x = True, y = True)
    
    def saveHome(self):
        self._home = self.pgCanvas.saveState()
        
    def restoreHome(self):
        self.pgCanvas.restoreState(self._home)
    
    def makePlot(self, *args, **kwargs):
        
        color = kwargs.get('color', 'w')
        width = kwargs.get('width', 2)
        style = kwargs.get('style', None)
        dash = kwargs.get('dash', None)
        cosmetic = kwargs.get('cosmetic', True)
        hsv = kwargs.get('hsv', None)
        name = kwargs.get('name', None)
        
        dataItem = pg.PlotDataItem(pen = pg.mkPen(color = color,
                                                          width = width,
                                                          style = style,
                                                          dash = dash,
                                                          cosmetic = cosmetic,
                                                          hsv = hsv
                                                          ),
                                        *args, **kwargs)
        
        dataItem.opts['name'] = name
        
        self.pgCanvas.plotItem.addItem(dataItem)
        
        self.saveHome()
        
        return dataItem
    
    def createCurveItem(self, y, color, name, clickable):
        return pg.PlotCurveItem(y = y, pen = pg.mkPen(color = color), name = name, clickable = clickable)
    
    @QtCore.pyqtSlot(object)   
    def getItem(self, item):
        self.sigClicked.emit(item)
    
    @QtCore.pyqtSlot(object, bool)
    def highlightCurveFromPlot(self, plot, select):
        plotPosStr = "".join(reversed([str(i) for i in plot.pos]))
        
        curve = next((x for x in self.pgCanvas.plotItem.curves if x.name() == plotPosStr), None)
        
        if curve is not None:
            if select:
                curve.setShadowPen('w', width = 3)
                if curve not in self.selectedCurves:
                    self.selectedCurves.append(curve)
            
            elif not select:
                curve.setShadowPen('k', width = 1)
                if curve in self.selectedCurves:
                    self.selectedCurves.remove(curve)
        else:
            print("Curve not found! Something's wrong!")
    
    def createFilledCurveItem(self, y1, y2, color):
        return pg.FillBetweenItem(curve1 = y1, curve2 = y2, brush = pg.mkBrush(color))
    
    def clearAll(self):
        self.pgCanvas.plotItem.clear()
        self.selectedCurves = []
        self.showGrid()
    
    def setDark(self):
        self.pgCanvas.setBackground('k')