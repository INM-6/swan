#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 23:08:03 2017

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from numpy import array
from swan.src.widgets.viewtoolbar import ViewToolbar
from swan.src.widgets.myglwidget import myGLWidget

pg.setConfigOptions(useOpenGL=True)


class PyQtWidget3d(QtWidgets.QWidget):
    refreshPlots = QtCore.pyqtSignal()
    sigClicked = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent=parent)

        layout = QtGui.QGridLayout()
        self.layout = layout

        self.pgCanvas = myGLWidget()
        self.pgCanvas.setBackgroundColor('k')
        self.pgCanvas.unitClicked.connect(self.getItem)

        self.layout.addWidget(self.pgCanvas, 0, 0)

        self.toolbar = ViewToolbar(self)
        self.layout.addWidget(self.toolbar, 1, 0)

        self.layout.setRowStretch(0, 10)

        self.setLayout(self.layout)

        self.cameraPosition = None
        self._axesGLOptions = 'translucent'
        self._grid_size = 3000
        self._grid_spacing = 100
        self.means = []
        self.positions = []
        self.selectedPlots = []
        self.suggestedPlots = []
        self.shadowPenColor = (0.9, 0.9, 0.9, 0.5)

    def setup_axes(self, size=None, spacing=None, glOptions=None, axes='xyz', setCamera=True, **kwargs):

        if size is None:
            size = self._grid_size
        if spacing is None:
            spacing = self._grid_spacing
        if glOptions is None:
            glOptions=self._axesGLOptions

        if 'x' in axes:
            xg = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=glOptions)
            xg.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            self.pgCanvas.addItem(xg)

        if 'y' in axes:
            yg = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=glOptions)
            yg.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            yg.rotate(90, 0, 1, 0)
            self.pgCanvas.addItem(yg)

        if 'z' in axes:
            zg = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=glOptions)
            zg.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            zg.rotate(90, 1, 0, 0)
            self.pgCanvas.addItem(zg)

        if setCamera:
            distance = kwargs.get("distance", 2 * size)
            elevation = kwargs.get("elevation", None)
            azimuth = kwargs.get("azimuth", None)
            self.setCameraPosition(distance=distance, elevation=elevation, azimuth=azimuth)

    def addScatterPlotItem(self, plotItem=None, gl_options='translucent'):
        if plotItem is None:
            self.pgCanvas.addItem(
                myScatterPlotItem(pos=array([0, 0, 0]), size=1, color=(0.5, 0.5, 0.5, 0.5), pxMode=True))
        else:
            plotItem.setGLOptions(gl_options)
            self.pgCanvas.addItem(plotItem)

    def addSurfacePlotItem(self, surfaceItem):
        self.pgCanvas.addItem(surfaceItem)

    def createScatterPlotItem(self, pos, size, color, unit_id=None, session=None, pxMode=True, clickable=False):
        item = myScatterPlotItem(pos=pos, size=size, color=color, pxMode=pxMode)
        item.opts["clickable"] = clickable
        item.opts["unit_id"] = unit_id
        item.opts["session"] = session
        return item

    def createSurfacePlotItem(self, x, y, z, color, shader='shaded'):
        if x is not None and y is not None:
            return gl.GLSurfacePlotItem(x=x, y=y, z=z, color=color, shader=shader)
        elif x is None and y is None:
            return gl.GLSurfacePlotItem(z=z, color=color, shader=shader)
        else:
            raise ValueError("x and y must both be None or be 1D arrays of shape (z.shape[0], z.shape[1])")

    def setCameraPosition(self, distance=None, elevation=None, azimuth=None):
        self.pgCanvas.setCameraPosition(self, distance=distance, elevation=elevation, azimuth=azimuth)

    def saveCameraPosition(self):
        distance = self.pgCanvas.opts['distance']
        elevation = self.pgCanvas.opts['elevation']
        azimuth = self.pgCanvas.opts['azimuth']

        self.cameraPosition = (distance, elevation, azimuth)

    def restoreCameraPosition(self):
        distance = self.cameraPosition[0]
        elevation = self.cameraPosition[1]
        azimuth = self.cameraPosition[2]

        self.setCameraPosition(distance=distance, elevation=elevation, azimuth=azimuth)

    def clear_suggests(self):
        for old_suggested_plot in self.suggestedPlots:
            old_suggested_plot.restorePen()
            self.suggestedPlots.remove(old_suggested_plot)

    def reset_plot(self):
        self.pgCanvas.items = []
        self.setup_axes(glOptions=self._axesGLOptions)

    def show_plot(self):
        self.pgCanvas.show()

    def triggerRefresh(self):
        self.refreshPlots.emit()

    @QtCore.pyqtSlot(object)
    def getItem(self, item):
        self.sigClicked.emit(item)

    @QtCore.pyqtSlot(object, bool)
    def highlightCurveFromPlot(self, plot, select):
        scatterPlotMean = next((x for x in self.means if (x.opts["session"], x.opts["unit_id"]) == plot.pos), None)
        scatterPlotPos = next((x for x in self.positions if (x.opts["session"], x.opts["unit_id"]) == plot.pos), None)
        suggestedPlots = [x for x in self.positions if
                          x.opts["session"] == plot.pos[0] and x not in self.selectedPlots]

        if scatterPlotMean is not None:
            if select:
                self.clear_suggests()
                for suggested_plot in suggestedPlots:
                    if suggested_plot not in self.suggestedPlots:
                        suggested_plot.setSuggestPen()
                        self.suggestedPlots.append(suggested_plot)
                if scatterPlotMean not in self.selectedPlots:
                    self.selectedPlots.append(scatterPlotMean)
                if scatterPlotPos not in self.selectedPlots:
                    self.selectedPlots.append(scatterPlotPos)
                if scatterPlotPos in self.suggestedPlots:
                    self.suggestedPlots.remove(scatterPlotPos)

                scatterPlotMean.setShadowPen(self.shadowPenColor)
                scatterPlotPos.setShadowPen(self.shadowPenColor)

            elif not select:
                if scatterPlotMean in self.selectedPlots:
                    scatterPlotMean.restorePen()
                    self.selectedPlots.remove(scatterPlotMean)
                if scatterPlotPos in self.selectedPlots:
                    scatterPlotPos.restorePen()
                    self.selectedPlots.remove(scatterPlotPos)
                if not self.selectedPlots:
                    self.clear_suggests()


class myScatterPlotItem(gl.GLScatterPlotItem, QtGui.QGraphicsItem):
    sigClicked = QtCore.pyqtSignal(object)

    def __init__(self, **kwargs):
        gl.GLScatterPlotItem.__init__(self, **kwargs)
        QtGui.QGraphicsItem.__init__(self)
        self.opts = {"clickable": kwargs.get("clickable", False),
                     "unit_id": None,
                     "session": None,
                     "defaultColor": self.color,
                     "defaultSize": self.size,
                     "highlightedSize": self.size + 1}

        self.highlighted = False

    def setName(self, name):
        self.opts["name"] = name

    def setClickable(self, choice=True):
        self.opts["clickable"] = choice

    def setSuggestPen(self):
        self.highlighted = True
        self.setData(size=self.opts["highlightedSize"])

    def setShadowPen(self, color):
        self.highlighted = True
        self.setData(color=color, size=self.opts["highlightedSize"])

    def restorePen(self, defaultSize=True):
        self.highlighted = False
        if defaultSize:
            self.setData(color=self.opts["defaultColor"], size=self.opts["defaultSize"])
        else:
            self.setData(color=self.opts["defaultColor"])


class PyQtWidget2d(QtWidgets.QWidget):
    sigClicked = QtCore.pyqtSignal(object)
    refreshPlots = QtCore.pyqtSignal()

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout = QtGui.QGridLayout()

        self.pgCanvas = pg.PlotWidget(background='k')
        self.layout.addWidget(self.pgCanvas, 0, 0)

        self.toolbar = ViewToolbar(self)
        self.layout.addWidget(self.toolbar, 1, 0)

        self.setLayout(self.layout)

        self.layout.setRowStretch(0, 10)

        self.selectedCurves = []

        self._home = None

    def showGrid(self):
        self.pgCanvas.plotItem.showGrid(x=True, y=True)

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
        unit_id = kwargs.get('unit_id', None)
        session = kwargs.get('session', None)
        clickable = kwargs.get('clickable', False)

        dataItem = pg.PlotDataItem(pen=pg.mkPen(color=color,
                                                width=width,
                                                style=style,
                                                dash=dash,
                                                cosmetic=cosmetic,
                                                hsv=hsv
                                                ),
                                   *args, **kwargs)

        dataItem.opts['unit_id'] = unit_id
        dataItem.opts['session'] = session
        dataItem.opts['clickable'] = clickable

        self.addPlot(dataItem)

        return dataItem

    def addPlot(self, dataItem):
        self.pgCanvas.plotItem.addItem(dataItem)
        self.saveHome()

    def createCurveItem(self, x, y, color, name, clickable):
        return pg.PlotCurveItem(x=x, y=y, pen=pg.mkPen(color=color), name=name, clickable=clickable)

    def createFilledCurveItem(self, y1, y2, color):
        return pg.FillBetweenItem(curve1=y1, curve2=y2, brush=pg.mkBrush(color))

    def createScatterPlotItem(self, *args, **kwargs):

        color = kwargs.get('color', 'w')
        size = kwargs.get('size', 2)
        name = kwargs.get('name', None)

        symbol = 's'
        symbolSize = size
        symbolBrush = pg.mkBrush(color=color)
        symbolPen = pg.mkPen(color=color)

        scatterPlotItem = pg.PlotDataItem(pen=None,
                                          symbol=symbol,
                                          symbolPen=symbolPen,
                                          symbolBrush=symbolBrush,
                                          symbolSize=symbolSize,
                                          *args, **kwargs)

        scatterPlotItem.opts['name'] = name

        self.pgCanvas.plotItem.addItem(scatterPlotItem)

        self.saveHome()

        return scatterPlotItem

    def createVerticalLine(self, xval, color='w', width=2):

        pen = pg.mkPen(color=color, width=width)

        self.pgCanvas.plotItem.addLine(x=xval, pen=pen)

    def setXLabel(self, text, units=None, *args):

        self.pgCanvas.plotItem.setLabel('bottom', text=text, units=units, *args)

    def setYLabel(self, text, units=None, *args):

        self.pgCanvas.plotItem.setLabel('left', text=text, units=units, *args)

    def setPlotTitle(self, text):

        self.pgCanvas.plotItem.setTitle(title=text)

    def connectLayersToFunction(self, function):
        for item in self.toolbar.layerItems:
            item.toggled.connect(function)

    @QtCore.pyqtSlot(object)
    def getItem(self, item):
        self.sigClicked.emit(item)

    @QtCore.pyqtSlot(object, bool)
    def highlightCurveFromPlot(self, plot, select):
        plot_position = plot.pos

        curve = next((x for x in self.pgCanvas.plotItem.curves
                      if x.opts["unit_id"] == plot_position[1]
                      and x.opts["session"] == plot_position[0]
                      and x.opts["clickable"]),
                     None)

        if curve is not None:
            if select:
                curve.setShadowPen('w', width=3)
                if curve not in self.selectedCurves:
                    self.selectedCurves.append(curve)

            elif not select:
                curve.setShadowPen('k', width=1)
                if curve in self.selectedCurves:
                    self.selectedCurves.remove(curve)

    def clearAll(self):
        self.pgCanvas.plotItem.clear()
        self.selectedCurves = []
        self.showGrid()

    def triggerRefresh(self):
        self.refreshPlots.emit()
