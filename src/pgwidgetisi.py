"""
Created on Nov 17, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget2d
from numpy import histogram

class pgWidgetISI(PyQtWidget2d):
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
        self._hists = []
        
        self.showGrid()
    
    #### general methods ####
        
    def plotHist(self, x, y, color, name, clickable = False):
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
        self._hists.append(self.makePlot(y = y, color = color, name = name, clickable = clickable))

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
        
        for layer in layers:
            if layer == "sessions":
                for j in range(vum.n_):
                    values = []
                    for i in range(len(data.blocks)):
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            for d in datas:
                                values.extend(d)
                    if values:
                        y = histogram(values, bins = 25)
                        tmp = y[1]
                        tmp = tmp[:len(tmp)-1]
                        self.plot((tmp, y[0]/(1.0*len(values))), col)
            else:
                for i in range(len(data.blocks)):
                    for j in range(vum.n_):
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            for d in datas:
                                y = histogram(d, bins=25)
                                tmp = y[1]
                                tmp = tmp[:len(tmp)-1]
                                self.plotHist(x = tmp, y = y[0]/(1.0*len(d)), color = col, name = "{}{}".format(i, j))
            
            self.connectPlots()
            
    def connectPlots(self):
        for item in self._hists:
            item.curve.setClickable(True, width = 10)
            item.sigClicked.connect(self.getItem)
    
    def clear_plots(self):
        self._hists = []
        self._plotItem.clearPlots()