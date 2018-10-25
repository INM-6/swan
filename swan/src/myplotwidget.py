"""
Created on Oct 22, 2013

@author: Christoph Gollan

In this module you can find the :class:`MyPlotWidget`. It inherits
from :class:`pyqtgraph.PlotWidget`.

This widget is used by :class:`src.myplotgrid.MyPlotContent` to show
many of these widgets in a nice overview.
"""
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget, mkColor, mkPen, arrayToQPath
import numpy as np
from copy import deepcopy

class MyPlotWidget(QtWidgets.QWidget):
    """
    Pyqtgraph's PlotWidget extended to have a fast and simple one 
    for using with this application.
    
    The *args* and *kwargs* are passed to :class:`pyqtgraph.PlotWidget`.

    
    """
    
    selectPlot = QtCore.pyqtSignal("PyQt_PyObject", bool)
    colourStripToggle = QtCore.pyqtSignal(object, int)
    visibilityToggle = QtCore.pyqtSignal(int, int, bool)
    """
    Signal to emit if this plot is selected by clicking on it.
    
    """
    
    def __init__(self, width = 200, height = 150, *args, **kwargs):
        """
        **Properties**
        
            *_plotitem* (:class:`pyqtgraph.PlotItem`):
                Just a shortcut to the PlotItem.
            *selected* (boolean):
                Whether or not this widget is selected.
            *inFocus* (boolean):
                Whether or not this widget has a mouse hovering it.
            *_std* (tuple of integer):
                The default size of this widget.
            *bgs* (dictionary):
                A dictionary containing the different backgrounds 
                this widget can have.
            *_bg* (:class:`PyQt5.QtGui.QColor`):
                The current background color of this widget.
        
        """
        QtWidgets.QWidget.__init__(self)
        self.centralLayout = QtGui.QGridLayout()
        self.centralLayout.setSpacing(0)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.centralLayout)
        
        self.plotWidget = PlotWidget(*args, **kwargs)
        
        self.plotWidget.setMenuEnabled(False)
        self.plotWidget.setAntialiasing(False)
        self.plotWidget.hideButtons()
        self.plotWidget.setMouseEnabled(False, False)
        self.plotWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.plotWidget.setMouseTracking(True)
        self.plotWidget.hideAxis("bottom")
        self.plotWidget.hideAxis("left")
        
        self.centralLayout.addWidget(self.plotWidget)
        
        #properties{
        self._plotitem = self.plotWidget.getPlotItem()
        self._plotitem.disableAutoRange()
        self.selected = False
        self.inFocus = False
        self.disabled = False
        self.rowInhibited = False
        self.colInhibited = False
        self.toBeUpdated = True
        self.hasPlot = False
        self._std = (width, height)
        self._defPenColour = None
        self.bgs = {"normal":mkColor('w'), "selected":mkColor(0.8), "disabled":mkColor(0.7), "inFocus":mkColor(0.9)}
        self._bg = self.bgs["normal"]
        self.pos = (0, 0)
        self.defPens = []
        self.disPen = mkColor('w')
        self._dataItems = []
        #}
        self.setFixedSize(self._std[0], self._std[1])
        
        
    #### general methods ####
        
    def plot(self, y, color='w'):
        """
        Plots data on the PlotItem.
        
        **Arguments**
        
            *y* (iterable object):
                The data to plot.
            *color* (Color argument for :func:`pyqtgraph.mkPen`):
                The color the data should have.
                Default: w for white.
        
        """
        plot = self._plotitem.plot(y, pen=mkPen(mkColor(color), width = 2), antialias=False)
        self.defPens.append(mkColor(color))
        self._dataItems.append(plot)
    
    def plot_many(self, ys, color='w'):
        """
        Plots data on the PlotItem.
        
        **Arguments**
        
            *y* (iterable object):
                The data to plot.
            *color* (Color argument for :func:`pyqtgraph.mkPen`):
                The color the data should have.
                Default: w for white.
        
        """
        lines = MultiLine(ys, color)
        self._plotitem.addItem(lines)
            
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
        neww = int(oldw + oldw*(width/100.0))
        newh = int((3./4.)*neww)
        if neww > 0 and newh > 0:
            self.setFixedSize(neww, newh)
        
    def change_background(self, change):
        """
        Changes the background of the widget.
        
        **Arguments**
        
            *change* (boolean):
                Whether or not the widget's bg should be changed to
                a selected state.
        
        """
        if change:
            self._bg = self.bgs["selected"]
            self.plotWidget.setBackground(self.bgs["selected"])   
        else:
            self._bg = self.bgs["normal"]
            self.plotWidget.setBackground(self.bgs["normal"])
    
    def clear_(self):
        """
        Clears the :class:`pyqtgraph.PlotItem`.
        
        """
        self._plotitem.clear()
        self._dataItems.clear()
        self.defPens.clear()
        self.hasPlot = False

    def set_tooltip(self, tooltip):
        """
        Sets a tool tip for this widget.
        
        **Arguments**
        
            tooltip (string):
                The tool tip to set.
        
        """
        self.setToolTip(tooltip)
        QtGui.QToolTip.setFont(QtGui.QFont('Arial', 9))
    
    def toggleColourStrip(self, col):
        colour = mkColor(col)
        self.colourStripToggle.emit(colour, self.pos[0])
    
    def disable(self):
        if self.selected:
            self.selectPlot.emit(self, not self.selected)
        self.disabled = True
        self.visibilityToggle.emit(self.pos[0], self.pos[1], False)
        self.plotWidget.setBackground(self.bgs["disabled"])
        for dataItem in self._dataItems:
            dataItem.setPen(self.disPen)
        
    def enable(self, which):
        if which == "row":
            self.rowInhibited = False
        elif which == "col":
            self.colInhibited = False
        elif which == "all":
            self.rowInhibited = False
            self.colInhibited = False
        
        if not self.rowInhibited and not self.colInhibited:
            self.disabled = False
            self.visibilityToggle.emit(self.pos[0], self.pos[1], True)
            self.plotWidget.setBackground(self.bgs["normal"])
            for dataItem in self._dataItems:
                dataItem.setPen(mkColor(self._defPenColour), width = 2)
        
    def close(self):
        self.plotWidget.close()
        self.setParent(None)
        
    def darkTheme(self):
        self.bgs = {"normal":mkColor('k'), "selected":mkColor(0.2), "disabled":mkColor(0.25), "inFocus":mkColor(0.1)}
        self._bg = self.bgs["normal"]
        self.disPen = mkColor('k')
        
    #### mouse interaction ####
        
    def mousePressEvent(self, event):
        """
        This method is called you click on this widget.
        
        The event will be accepted if you click with the
        left mouse button.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton and not self.disabled:
            self.selectPlot.emit(self, not self.selected)
            super(PlotWidget, self.plotWidget).mousePressEvent(event)
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
        if not self.disabled:
            self.inFocus = True
            self.plotWidget.setBackground(self.bgs["inFocus"])
            event.accept()
        else:
            event.ignore()
    
    def leaveEvent(self, event):
        """
        This method is called the mouse leaves this widget.
        
        Sets this widget out of focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if not self.disabled:
            self.inFocus = False
            self.plotWidget.setBackground(self._bg)
            event.accept()
        else:
            event.ignore()

class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, data, color):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        connect = np.ones(data.shape, dtype=bool)
        connect[:,-1] = 0 # don't draw the segment between each trace
        x = np.tile([i for i in range(data.shape[1])], data.shape[0]).reshape(data.shape)
        self.path = arrayToQPath(x.flatten(), data.flatten(), connect.flatten())
        QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(mkPen(color))
    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return QtGui.QGraphicsItem.shape(self)
    def boundingRect(self):
        return self.path.boundingRect()
        
        
        
