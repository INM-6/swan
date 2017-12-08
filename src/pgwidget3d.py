"""
Created on Nov 8, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget3d` which inherits
from :class:`src.mypgwidget.PyQtWidget3d`.

It is extended by a 3d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget3d
from numpy import array


class pgWidget3d(PyQtWidget3d):
    """
    A class with only one plot that shows 3d data.
    
    """

    def __init__(self, parent = None):
        """
        **Properties**
        
            *_axes* (:class:`mpl_toolkits.mplot3d.Axes3d`):
                The 3d plot for this widget.
            *_kwargs* (dictionary):
                Plot parameters given as (key, value) pares.
            
            *_axesSize* (float):
                Grid size for the axes.
            *_axesSpacing* (float):
                Grid spacing for the axes.
            
            *_xScaleFactor* (float):
                Scale factor for the x data of the 3d waveforms.
            *_yScaleFactor* (float):
                Scale factor for the y data of the 3d waveforms.
            *_zScaleFactor* (float):
                Scale factor for the z data of the 3d waveforms.
        
        """
        PyQtWidget3d.__init__(self, parent = parent)
        
        self._axesSize = 1000.
        self._axesSpacing = 100.
        self._xScaleFactor = 100.
        self._yScaleFactor = 10.
        self._zScaleFactor = 1/2.
        
        self.setup_axes(size = self._axesSize, spacing = self._axesSpacing, axes = 'x')
    
    #### general methods ####    
    
    def reset_plot(self):
        self.pgCanvas.items = []
        self.setup_axes(size = self._axesSize, spacing = self._axesSpacing, axes = 'x')
        
    def createSurfacePlot(self, z, color, x = None, y = None, shader = 'shaded'):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *x* (2d iterable object):
                The x data that should be plotted.
            *y* (2d iterable object):
                The y data that should be plotted.
            *z* (2d iterable object):
                The z data that should be plotted.
            *color* (tuple of integer):
                The color of the lines.
        
        """
        return self.createSurfacePlotItem(x = x, y = y, z = z, color = color, shader = shader)
    
    def addSurfacePlot(self, surfaceItem):
        surfaceItem.scale(self._xScaleFactor, self._yScaleFactor, self._zScaleFactor)
        self.addSurfacePlotItem(surfaceItem)

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
        self.reset_plot()
        
        plots = []
        
        found = False
        for j in range(vum.n_):
            if vum.visible[j]:
                found = True
                break
        if found:
            for layer in layers:
                if layer == "average":
                    zs = []
                    for i in range(len(data.blocks)):
                        runit = vum.get_realunit(i, j, data)
                        if vum.mapping[i][j] != 0 and "noise" not in runit.description.split() and "unclassified" not in runit.description.split():
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, True)
                            z = datas
                            zs.append(z)
                    zs = array(zs)
                    x = array(range(zs.shape[0]))
                    y = array(range(zs.shape[-1]))
                    if len(zs) > 1:
                        plot = self.createSurfacePlot(x = x, y = y, z = zs, color = col)
                        plots.append(plot)
                    else:
                        continue
                elif layer == "standard deviation":
                    
                    zs = []
                    l = 0
                    for i in range(len(data.blocks)):
                        runit = vum.get_realunit(i, j, data)
                        if vum.mapping[i][j] != 0 and "noise" not in runit.description.split() and "unclassified" not in runit.description.split():
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, True)
                            z = datas
                            l = len(z)
                            zs.append(z)
                    zs = array(zs)
                    x = array(range(zs.shape[0]))
                    y = array(range(zs.shape[-1]))
                    if l > 1:
                        for k in range(l):
                            plot = self.createSurfacePlot(x = x, y = y, z = zs[:, k, :], color = col)
                            plots.append(plot)
                    else:
                        continue
                    
                else:
                    print("invalid layer requested")
                    raise ValueError
                
        
        if plots:
            for plot in plots:
                self.addSurfacePlot(plot)
