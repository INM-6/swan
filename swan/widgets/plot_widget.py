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


class MyPlotWidget(QtWidgets.QWidget):
    """
    Pyqtgraph's PlotWidget extended to have a fast and simple one 
    for using with this application.
    
    The *args* and *kwargs* are passed to :class:`pyqtgraph.PlotWidget`.

    
    """

    select_plot = QtCore.pyqtSignal("PyQt_PyObject", bool)
    colour_strip_toggle = QtCore.pyqtSignal(object, int)
    visibility_toggle = QtCore.pyqtSignal(int, int, bool)
    """
    Signal to emit if this plot is selected by clicking on it.
    
    """

    def __init__(self, width=200, height=150, *args, **kwargs):

        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.central_layout = QtWidgets.QGridLayout()
        self.plot_widget = PlotWidget(*args, **kwargs)

        self.setup()

        # attributes and properties
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.disableAutoRange()

        self.selected = False
        self.in_focus = False
        self.disabled = False
        self.inhibited_by_row = False
        self.inhibited_by_col = False
        self.to_be_updated = True
        self.has_plot = False
        self.default_size = (width, height)
        self.pos = (0, 0)
        self.default_pens = []
        self.data_items = []

        # setting the palette
        self.default_pen_colour = None
        self.backgrounds = {"normal": mkColor('k'),
                            "selected": mkColor(0.2),
                            "disabled": mkColor(0.25),
                            "in_focus": mkColor(0.1)}
        self.background = self.backgrounds["normal"]
        self.disPen = mkColor('k')

        self.setFixedSize(self.default_size[0], self.default_size[1])

    def setup(self):

        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.central_layout)

        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setAntialiasing(False)
        self.plot_widget.hideButtons()
        self.plot_widget.setMouseEnabled(False, False)
        self.plot_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.plot_widget.setMouseTracking(True)
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.hideAxis("left")

        self.central_layout.addWidget(self.plot_widget)

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
        plot = self.plot_item.plot(y, pen=mkPen(mkColor(color), width=2), antialias=False)
        self.default_pens.append(mkColor(color))
        self.data_items.append(plot)

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
        self.plot_item.addItem(lines)

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
        neww = int(oldw + oldw * (width / 100.0))
        newh = int((3. / 4.) * neww)
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
            self.background = self.backgrounds["selected"]
            self.plot_widget.setBackground(self.backgrounds["selected"])
        else:
            self.background = self.backgrounds["normal"]
            self.plot_widget.setBackground(self.backgrounds["normal"])

    def clear_(self):
        """
        Clears the :class:`pyqtgraph.PlotItem`.
        
        """
        self.plot_item.clear()
        self.data_items.clear()
        self.default_pens.clear()
        self.has_plot = False

    def set_tooltip(self, tooltip):
        """
        Sets a tool tip for this widget.
        
        **Arguments**
        
            tooltip (string):
                The tool tip to set.
        
        """
        self.setToolTip(tooltip)
        QtWidgets.QToolTip.setFont(QtGui.QFont('Arial', 9))

    def toggle_colour_strip(self, col):
        colour = mkColor(col)
        self.colour_strip_toggle.emit(colour, self.pos[1])

    def set_for_update(self):
        self.to_be_updated = True

    def set_as_updated(self):
        self.to_be_updated = False

    def disable(self):
        if self.selected:
            self.select_plot.emit(self, not self.selected)
        self.disabled = True
        self.visibility_toggle.emit(self.pos[0], self.pos[1], False)
        self.plot_widget.setBackground(self.backgrounds["disabled"])
        for data_item in self.data_items:
            data_item.setPen(self.disPen)

    def enable(self, which):
        if which == "row":
            self.inhibited_by_row = False
        elif which == "col":
            self.inhibited_by_col = False
        elif which == "all":
            self.inhibited_by_row = False
            self.inhibited_by_col = False

        if not self.inhibited_by_row and not self.inhibited_by_col:
            self.disabled = False
            self.visibility_toggle.emit(self.pos[0], self.pos[1], True)
            self.plot_widget.setBackground(self.backgrounds["normal"])
            for dataItem in self.data_items:
                dataItem.setPen(mkColor(self.default_pen_colour), width=2)

    def close(self):
        self.plot_widget.close()
        self.setParent(None)

    def mousePressEvent(self, event):
        """
        This method is called you click on this widget.
        
        The event will be accepted if you click with the
        left mouse button.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton and not self.disabled:
            self.select_plot.emit(self, not self.selected)
            PlotWidget.mousePressEvent(self.plot_widget, event)
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        # super(PlotWidget, self).mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        # super(PlotWidget, self).mouseReleaseEvent(event)
        event.accept()

    def enterEvent(self, event):
        """
        This method is called the mouse enters this widget.
        
        Sets this widget in focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if not self.disabled:
            self.in_focus = True
            self.plot_widget.setBackground(self.backgrounds["in_focus"])
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
            self.in_focus = False
            self.plot_widget.setBackground(self.background)
            event.accept()
        else:
            event.ignore()


class MultiLine(QtWidgets.QGraphicsPathItem):
    def __init__(self, data, color):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        connect = np.ones(data.shape, dtype=bool)
        connect[:, -1] = 0  # don't draw the segment between each trace
        x = np.tile([i for i in range(data.shape[1])], data.shape[0]).reshape(data.shape)
        self.path = arrayToQPath(x.flatten(), data.flatten(), connect.flatten())
        super(MultiLine, self).__init__(self.path)
        self.setPen(mkPen(color))

    def shape(self):  # override because QGraphicsPathItem.shape is too expensive.
        return QtWidgets.QGraphicsItem.shape(self)

    def boundingRect(self):
        return self.path.boundingRect()
