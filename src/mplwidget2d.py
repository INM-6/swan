"""
Created on Dec 5, 2013

@author: Christoph Gollan

In this module you can find the :class:`MplWidget2d` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 2d plot and the plotting methods.
"""
from src.matplotlibwidget import MatplotlibWidget


class MplWidget2d(MatplotlibWidget):
    """
    A class with only one plot that shows simple 2d data.    
    
    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
        
        """
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._axes = None
        #}
        self.setup()
        
        self._axes = self.get_axes()[0]
        self.clear_and_reset_axes()
        
    
    #### general methods ####    

    def plot(self, y, color):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
        
        """
        self._axes.plot(y, color=color)

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
        self.clear_and_reset_axes()
        for i in xrange(len(data.blocks)):
            for j in xrange(vum.n_):
                for layer in layers:
                    if vum.mapping[i][j] != None and vum.visible[j]:
                        runit = vum.get_realunit(i, j, data)
                        datas = data.get_data(layer, runit)
                        col = vum.get_color(j, True, layer)
                        for d in datas:
                            self.plot(d, col)
        self.draw()
                