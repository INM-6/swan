"""
Created on Nov 16, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.widgets.mypgwidget import PyQtWidget2d
from numpy import arange
from quantities import V


class PgWidget2d(PyQtWidget2d):
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
        self.toolbar.setup_checkboxes(layers)
        self.toolbar.doLayer.connect(self.trigger_refresh)
        self.toolbar.collapsible_widget.set_content_layout(self.toolbar.grid_layout)
        self.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.plot_item = self.pg_canvas.getPlotItem()
        self.plot_item.enableAutoRange()
        self._means = []
        self._stds = []

        self.fill_alpha = 50

        self.show_grid()

    def create_curve(self, x, y, color, clickable=True):
        return self.create_curve_item(x=x, y=y, color=color, name=None, clickable=clickable)

    def create_filled_curve(self, y1, y2, color):
        color_with_alpha = color + (self.fill_alpha,)
        return self.create_filled_curve_item(y1=y1, y2=y2, color=color_with_alpha)

    def plot_mean(self, x, y, color, unit_id, session, clickable=False):
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
        self._means.append(self.make_plot(x=x, y=y, color=color, unit_id=unit_id, session=session, clickable=clickable))

    def plot_std(self, xs, ys, color):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
        
        """
        curve1 = self.create_curve(x=xs, y=ys[0], color=color, clickable=False)
        curve2 = self.create_curve(x=xs, y=ys[1], color=color, clickable=False)
        self._stds.append(self.create_filled_curve(y1=curve1, y2=curve2, color=color))

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
        if self.toolbar.activate_button.current_state:

            layers = self.toolbar.get_checked_layers()
            active = vum.get_active()

            for session in range(len(active)):
                for unit_id in range(len(active[session])):
                    if active[session][unit_id]:
                        for layer in layers:
                            if layer == "standard deviation":
                                runit = vum.get_realunit(session, unit_id, data)
                                datas = data.get_data(layer, runit)
                                col = vum.get_colour(unit_id)
                                xs = arange(data.get_wave_length()) * 1 / data.sampling_rate.magnitude
                                ys = datas.rescale(V)
                                self.plot_std(xs=xs, ys=ys, color=col)

                            elif layer == "average":
                                runit = vum.get_realunit(session, unit_id, data)
                                datas = data.get_data(layer, runit)
                                col = vum.get_colour(unit_id)
                                x = arange(data.get_wave_length()) * 1 / data.sampling_rate.magnitude
                                y = datas.rescale(V)
                                self.plot_mean(x=x, y=y, color=col, unit_id=unit_id, session=session, clickable=True)

                            else:
                                raise Exception("Invalid layer requested!")

            self.set_x_label("Time", "s")
            self.set_y_label("Voltage", "V")
            self.set_plot_title("Mean Spike Waveforms")

            if self._stds:
                for std in self._stds:
                    self.plot_item.addItem(std)
            self.connect_plots()

    def connect_plots(self):
        for item in self._means:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.get_item)

    def clear_plots(self):
        self._means = []
        for item in self._stds:
            self.pg_canvas.removeItem(item)
        self._stds = []
        self.clear_all()
