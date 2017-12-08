"""
Created on Nov 16, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget2d

class pgWidget2d(PyQtWidget2d):
    """
    A class with only one plot that shows simple 2d data.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
        
        """
        PyQtWidget2d.__init__(self)
        
        self._plotItem = self.pgCanvas.getPlotItem()
        self._plotItem.enableAutoRange()
        self._means = []
        self._stds = []
        
        self._fillbetweenAlpha = 50
        
        self.showGrid()
    
    #### general methods ####

    def createCurve(self, y, color, name, clickable = True):
        return self.createCurveItem(y = y, color = color, name = name, clickable = clickable)
    
    def createFilledCurve(self, y1, y2, color):
        colorWithAlpha = color + (self._fillbetweenAlpha,)
        return self.createFilledCurveItem(y1 = y1, y2 = y2, color = colorWithAlpha)
        
    def plotMean(self, y, color, name, clickable = False):
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
        self._means.append(self.makePlot(y = y, color = color, name = name, clickable = clickable))
    
    def plotStd(self, ys, color):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
        
        """
        curve1 = self.createCurve(y = ys[0], color = color, name = None, clickable = False)
        curve2 = self.createCurve(y = ys[1], color = color, name = None, clickable = False)
        self._stds.append(self.createFilledCurve(y1 = curve1, y2 = curve2, color = color))

    def do_plot(self, vum, data, layers):
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
        for i in range(len(data.blocks)):
            for j in range(vum.n_):
                for layer in layers:
                    if layer == "standard deviation":                        
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            self.plotStd(ys = datas, color = col)
                            
                    elif layer == "average":
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            self.plotMean(y = datas, color = col, name = "{}{}".format(i, j))
                    
                    else:
                        raise Exception("Invalid layer requested!")
                        
        if self._stds:
            for std in self._stds:
                self._plotItem.addItem(std)
        self.connectPlots()
    
    def connectPlots(self):
        for item in self._means:
            item.curve.setClickable(True, width = 10)
            item.sigClicked.connect(self.getItem)
        
    def clear_plots(self):
        self._means = []
        for item in self._stds:
            self.pgCanvas.removeItem(item)
        self._stds = []
        self.clearAll()