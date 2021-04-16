"""
Created on Nov 8, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget3d` which inherits
from :class:`src.mypgwidget.PyQtWidget3d`.

It is extended by a 3d plot and the plotting methods.
"""
from swan.widgets.mypgwidget import PyQtWidget3d
import numpy as np


class PgWidget3d(PyQtWidget3d):
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
        self.toolbar.setup_checkboxes(layers)
        self.toolbar.doLayer.connect(self.trigger_refresh)
        self.toolbar.collapsible_widget.set_content_layout(self.toolbar.grid_layout)
        self.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.axes_size = 5000.
        self.axes_spacing = 100.
        self.x_scale_factor = 300.
        self.y_scale_factor = 20.
        self.z_scale_factor = 1.
        self.plot_spacing = 50.
        self.x_offset = -2000.
        self.y_offset = -3000.

    def reset_plot(self):
        self.pg_canvas.items = []
        self.setup_axes(size=self.axes_size, spacing=self.axes_spacing, axes='x', set_camera=True)

    def create_surface_plot(self, z, color, x=None, y=None, shader='shaded'):
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
        return self.create_surface_plot_item(x=x, y=y, z=z, color=color, shader=shader)

    def add_surface_plot(self, surface_item):
        surface_item.scale(self.x_scale_factor, self.y_scale_factor, self.z_scale_factor)
        surface_item.translate(self.x_offset, self.y_offset, 0., local=False)
        self.add_surface_plot_item(surface_item)

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
        self.save_camera_position()
        self.reset_plot()

        if self.toolbar.activate_button.current_state:

            layers = self.toolbar.get_checked_layers()

            plots = []

            active = vum.get_active().T
            # Transposing the active matrix so that i can loop over the units first

            for layer in layers:
                if layer == "average":
                    for unit_index in range(len(active)):
                        if any(active[unit_index]):
                            col = vum.get_colour(unit_index) + (self.fill_alpha,)
                            zs = []
                            for session_index in range(len(active[unit_index])):
                                if active[unit_index][session_index]:
                                    runit = vum.get_realunit(unit_index, session_index, data)
                                    datas = data.get_data(layer, runit).magnitude
                                    zs.append(datas)
                            zs = np.array(zs)
                            x = np.array(range(zs.shape[0]))
                            y = np.array(range(zs.shape[-1])) + self.plot_spacing * (unit_index + 1)
                            if len(zs) > 1:
                                plot = self.create_surface_plot(x=x, y=y, z=zs, color=col)
                                plots.append(plot)
                            else:
                                continue
                elif layer == "standard deviation":
                    for unit_index in range(len(active)):
                        if any(active[unit_index]):
                            col = vum.get_colour(unit_index) + (self.fill_alpha,)
                            zs = []
                            length = 0
                            for session_index in range(len(active[unit_index])):
                                if active[unit_index][session_index]:
                                    runit = vum.get_realunit(session_index, unit_index, data)
                                    datas = data.get_data(layer, runit).magnitude
                                    length = len(datas)
                                    zs.append(datas)
                            zs = np.array(zs)
                            x = np.array(range(zs.shape[0]))
                            y = np.array(range(zs.shape[-1])) + self.plot_spacing * (unit_index + 1)
                            if length > 1:
                                for k in range(length):
                                    plot = self.create_surface_plot(x=x, y=y, z=zs[:, k, :], color=col)
                                    plots.append(plot)
                            else:
                                continue

                else:
                    print("invalid layer requested")

            if plots:
                for plot in plots:
                    self.add_surface_plot(plot)

            self.restore_camera_position()
