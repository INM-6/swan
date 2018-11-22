"""
Created on Nov 16, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.src.widgets.mypgwidget import PyQtWidget2d
from numpy import arange
from quantities import V


class pgWidget2d(PyQtWidget2d):
    """
    A class with only one plot that shows simple 2d data.
    
    """

    def __init__(self):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
        
        """
        PyQtWidget2d.__init__(self)

        layers = ["average", "standard deviation"]
        self.toolbar.setupCheckboxes(layers)
        self.toolbar.doLayer.connect(self.triggerRefresh)
        self.toolbar.colWidg.setContentLayout(self.toolbar.gridLayout)
        self.toolbar.mainGridLayout.setContentsMargins(0, 0, 0, 0)

        self._plotItem = self.pgCanvas.getPlotItem()
        self._plotItem.enableAutoRange()
        self._means = []
        self._stds = []

        self._fillbetweenAlpha = 50

        self.showGrid()

    #### general methods ####

    def createCurve(self, x, y, color, clickable=True):
        return self.createCurveItem(x=x, y=y, color=color, name=None, clickable=clickable)

    def createFilledCurve(self, y1, y2, color):
        colorWithAlpha = color + (self._fillbetweenAlpha,)
        return self.createFilledCurveItem(y1=y1, y2=y2, color=colorWithAlpha)

    def plotMean(self, x, y, color, unit_id, session, clickable=False):
        """
        Plot mean waveforms to the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
            *name* (string):
                The name of the curve. Of the form "ij",
                where i is the session and j is the unit.
                Useful in recognizing the plot.
            *clickable* (bool):
                Whether the item should respond to mouseclicks.
        
        """
        self._means.append(self.makePlot(x=x, y=y, color=color, unit_id=unit_id, session=session, clickable=clickable))

    def plotStd(self, xs, ys, color):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
        
        """
        curve1 = self.createCurve(x=xs, y=ys[0], color=color, clickable=False)
        curve2 = self.createCurve(x=xs, y=ys[1], color=color, clickable=False)
        self._stds.append(self.createFilledCurve(y1=curve1, y2=curve2, color=color))

    def do_plot(self, vum, data):
        """
        Plots data for every layer and every visible unit.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed to get the unit indexes.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get the units.
            *layers* (list of string):
                The layers that are visible.
        
        """
        self.clear_plots()
        if self.toolbar.layers.isChecked():

            layers = self.toolbar.getCheckedLayers()
            active = vum.get_active()

            for session in range(len(active)):
                for unit_id in range(len(active[session])):
                    if active[session][unit_id]:
                        for layer in layers:
                            if layer == "standard deviation":
                                runit = vum.get_realunit(session, unit_id, data)
                                datas = data.get_data(layer, runit)
                                col = vum.get_color(unit_id, False, layer, False)
                                xs = arange(data.get_wave_length()) * 1 / data.sampling_rate.magnitude
                                ys = datas.rescale(V)
                                self.plotStd(xs=xs, ys=ys, color=col)

                            elif layer == "average":
                                runit = vum.get_realunit(session, unit_id, data)
                                datas = data.get_data(layer, runit)
                                col = vum.get_color(unit_id, False, layer, False)
                                x = arange(data.get_wave_length()) * 1 / data.sampling_rate.magnitude
                                y = datas.rescale(V)
                                self.plotMean(x=x, y=y, color=col, unit_id=unit_id, session=session, clickable=True)

                            else:
                                raise Exception("Invalid layer requested!")

            self.setXLabel("Time", "s")
            self.setYLabel("Voltage", "V")
            self.setPlotTitle("Mean Spike Waveforms")

            if self._stds:
                for std in self._stds:
                    self._plotItem.addItem(std)
            self.connectPlots()

    def connectPlots(self):
        for item in self._means:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.getItem)

    def clear_plots(self):
        self._means = []
        for item in self._stds:
            self.pgCanvas.removeItem(item)
        self._stds = []
        self.clearAll()
