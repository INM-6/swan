"""
Created on Nov 8, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget3d` which inherits
from :class:`src.mypgwidget.PyQtWidget3d`.

It is extended by a 3d plot and the plotting methods.
"""
from swan.src.widgets.mypgwidget import PyQtWidget3d
import numpy as np


class pgWidget3d(PyQtWidget3d):
    """
    A class with only one plot that shows 3d data.
    
    """

    def __init__(self, parent=None):
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
        PyQtWidget3d.__init__(self, parent=parent)

        layers = ["average", "standard deviation"]
        self.toolbar.setupCheckboxes(layers)
        self.toolbar.doLayer.connect(self.triggerRefresh)
        self.toolbar.colWidg.setContentLayout(self.toolbar.gridLayout)
        self.toolbar.mainGridLayout.setContentsMargins(0, 0, 0, 0)

        self._axesSize = 5000.
        self._axesSpacing = 100.
        self._xScaleFactor = 300.
        self._yScaleFactor = 20.
        self._zScaleFactor = 1.
        self._plotSpacing = 50.
        self._xOffset = -2000.
        self._yOffset = -3000.

    #### general methods ####    

    def reset_plot(self):
        self.pgCanvas.items = []
        self.setup_axes(size=self._axesSize, spacing=self._axesSpacing, axes='x', setCamera=True)

    def createSurfacePlot(self, z, color, x=None, y=None, shader='shaded'):
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
        return self.createSurfacePlotItem(x=x, y=y, z=z, color=color, shader=shader)

    def addSurfacePlot(self, surfaceItem):
        surfaceItem.scale(self._xScaleFactor, self._yScaleFactor, self._zScaleFactor)
        surfaceItem.translate(self._xOffset, self._yOffset, 0., local=False)
        self.addSurfacePlotItem(surfaceItem)

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
        self.saveCameraPosition()
        self.reset_plot()

        if self.toolbar.layers.isChecked():

            layers = self.toolbar.getCheckedLayers()

            plots = []

            active = vum.get_active().T
            # Transposing the active matrix so that i can loop over the units first

            for layer in layers:
                if layer == "average":
                    for unit_index in range(len(active)):
                        if any(active[unit_index]):
                            col = vum.get_color(unit_index, False, layer, True)
                            zs = []
                            for session_index in range(len(active[unit_index])):
                                if active[unit_index][session_index]:
                                    runit = vum.get_realunit(unit_index, session_index, data)
                                    datas = data.get_data(layer, runit).magnitude
                                    zs.append(datas)
                            zs = np.array(zs)
                            x = np.array(range(zs.shape[0]))
                            y = np.array(range(zs.shape[-1])) + self._plotSpacing * (unit_index + 1)
                            if len(zs) > 1:
                                plot = self.createSurfacePlot(x=x, y=y, z=zs, color=col)
                                plots.append(plot)
                            else:
                                continue
                elif layer == "standard deviation":
                    for unit_index in range(len(active)):
                        if any(active[unit_index]):
                            col = vum.get_color(unit_index, False, layer, True)
                            zs = []
                            l = 0
                            for session_index in range(len(active[unit_index])):
                                if active[unit_index][session_index]:
                                    runit = vum.get_realunit(session_index, unit_index, data)
                                    datas = data.get_data(layer, runit).magnitude
                                    l = len(datas)
                                    zs.append(datas)
                            zs = np.array(zs)
                            x = np.array(range(zs.shape[0]))
                            y = np.array(range(zs.shape[-1])) + self._plotSpacing * (unit_index + 1)
                            if l > 1:
                                for k in range(l):
                                    plot = self.createSurfacePlot(x=x, y=y, z=zs[:, k, :], color=col)
                                    plots.append(plot)
                            else:
                                continue

                else:
                    print("invalid layer requested")

            if plots:
                for plot in plots:
                    self.addSurfacePlot(plot)

            self.restoreCameraPosition()
