"""
Created on Aug 29, 2014

@author: Christoph Gollan

In this module you can find the :class:`MplWidget3d` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 3d plot and the plotting methods.
"""
from src.matplotlibwidget import MatplotlibWidget


class MplWidget3d(MatplotlibWidget):
    """
    A class with only one plot that shows 3d data.

    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`mpl_toolkits.mplot3d.Axes3d`):
                The 3d plot for this widget.
            *_kwargs* (dictionary):
                Plot parameters given as (key, value) pares.
        
        """
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._axes = None
        self._kwargs = {"grid":False, 
                        "xlabel":"time", 
                        "ylabel":"session", 
                        "zlabel":"voltage"}
        #}
        self.setup((1, 1), False, True)
        
        self._axes = self.get_axes()[0]
        self.clear_and_reset_axes(**self._kwargs)
        
    
    #### general methods ####    

    def plot(self, x, y, z, color):
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
        self._axes.plot_surface(x, y, z, color=color, shade=False)
#         self._axes.plot_surface(x, y, z, color=color, shade=False, cmap=plt.cm.get_cmap("jet"))

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
        self.clear_and_reset_axes(**self._kwargs)
        found = False
        for j in xrange(vum.n_):
            if vum.visible[j]:
                found = True
                break
        if found:
            for layer in layers:
                xs = []
                ys = []
                zs = []
                l = 0
                for i in xrange(len(data.blocks)):
                    if vum.mapping[i][j] is not None:
                        runit = vum.get_realunit(i, j, data)
                        datas = data.get_data(layer, runit)
                        col = vum.get_color(j, True, layer)
                        z = datas
                        l = len(datas)
                        x = range(len(z[0]))
                        y = [(i+1) for k in x]
                        zs.append(z)
                        xs.append(x)
                        ys.append(y)
                for k in xrange(l):
                    zi = [el[k] for el in zs]
                    self.plot(xs, ys, zi, col)
        self.draw()
        


