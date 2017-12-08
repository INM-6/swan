"""
Created on Oct 22, 2013

@author: Christoph Gollan

In this module you can find the :class:`MyPlotWidget`. It inherits
from :class:`pyqtgraph.PlotWidget`.

This widget is used by :class:`src.myplotgrid.MyPlotContent` to show
many of these widgets in a nice overview.
"""
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph import PlotWidget, mkColor, mkPen, arrayToQPath, TextItem
import numpy as np


class MyPlotWidget(PlotWidget):
    """
    Pyqtgraph's PlotWidget extended to have a fast and simple one 
    for using with this application.
    
    The *args* and *kwargs* are passed to :class:`pyqtgraph.PlotWidget`.

    
    """
    
    selectPlot = QtCore.pyqtSignal("PyQt_PyObject", bool)
    """
    Signal to emit if this plot is selected by clicking on it.
    
    """
    
    def __init__(self, *args, **kwargs):
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
        PlotWidget.__init__(self, *args, **kwargs)
        self.setMenuEnabled(False)
        self.setAntialiasing(False)
        self.hideButtons()
        self.setMouseEnabled(False, False)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setMouseTracking(True)
        self.hideAxis("bottom")
        self.hideAxis("left")
        
        #properties{
        self._plotitem = self.getPlotItem()
        self._plotitem.disableAutoRange()
        self.selected = False
        self.inFocus = False
        self._std = (200, 150)
        self.bgs = {"normal":mkColor('w'), "selected":mkColor(0.8), "inFocus":mkColor(0.9)}
        self._bg = self.bgs["normal"]
        self.pos = (0, 0)
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
        self._plotitem.plot(y, pen=mkPen(mkColor(color), width = 2), antialias=True)
    
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
    
    def placeText(self, i, j, color, font, anchor = (0, 0)):
        textItem = TextItem(text = "SESSION {}\nUNIT {}".format(i, j), color = color, anchor = anchor)
        textItem.setFont(font)
        
#        textItem = pg.LabelItem()
#        textItem.setText(text = "SESSION {}\nUNIT {}".format(i, j), color = 'bfbfbf', size = '15pt', bold = True)
        self._plotitem.addItem(textItem)
#        self.setCentralItem(textItem)
        
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
            self.setBackground(self.bgs["selected"])   
        else:
            self._bg = self.bgs["normal"]
            self.setBackground(self.bgs["normal"])
    
    def clear_(self):
        """
        Clears the :class:`pyqtgraph.PlotItem`.
        
        """
        self._plotitem.clear()

    def set_tooltip(self, tooltip):
        """
        Sets a tool tip for this widget.
        
        **Arguments**
        
            tooltip (string):
                The tool tip to set.
        
        """
        self.setToolTip(tooltip)
        QtGui.QToolTip.setFont(QtGui.QFont('Arial', 9))
        
    def darkTheme(self):
        self.bgs = {"normal":mkColor('k'), "selected":mkColor(0.2), "inFocus":mkColor(0.1)}
        self._bg = self.bgs["normal"]
        
    #### mouse interaction ####
        
    def mousePressEvent(self, event):
        """
        This method is called you click on this widget.
        
        The event will be accepted if you click with the
        left mouse button.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.selectPlot.emit(self, not self.selected)
            super(PlotWidget, self).mousePressEvent(event)
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
        
        
        
