"""
Created on Nov 17, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.widgets.mypgwidget import PyQtWidget2d
import numpy as np
from swan.gui.isi_options_ui import IsiOptionsUi


class PgWidgetISI(PyQtWidget2d):
    """
    A class with only one plot that shows simple 2d data.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
        
        """
        PyQtWidget2d.__init__(self, *args, **kwargs)

        layers = ["individual", "pooled"]
        self.toolbar.setup_radio_buttons(layers)
        self.toolbar.doLayer.connect(self.trigger_refresh)

        self.plot_item = self.pg_canvas.getPlotItem()
        self.plot_item.enableAutoRange()
        self.histograms = []
        self.datas = {}

        self.bin_max = 500
        self.bin_step = 2
        self.step_mode = False

        self.bm_max = 5000
        self.bm_min = 0

        self.bs_max = 100
        self.bs_min = 0

        self.isi_options = IsiOptionsUi(self)

        self.show_grid()

    def on_enter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.
        
        Redraws everything.
        
        """
        bin_max = self.isi_options.binMaxEdit.text()
        bin_step = self.isi_options.binStepEdit.text()

        try:
            bin_max = int(bin_max)
            bin_step = float(bin_step)

            if self.bm_min < bin_max <= self.bm_max and self.bs_min < bin_step <= self.bs_max:
                self.bin_max = bin_max
                self.bin_step = bin_step

                self.update()
                self.isi_options.error_label.setText("")
            else:
                self.isi_options.error_label.setText("Values outside acceptable limits")
        except Exception as e:
            print(e)
            self.isi_options.error_label.setText("Invalid inputs!")

    def on_max_plus(self):
        """
        This method is called if you click on the plus button
        for the bin max optio8n.
        
        Increments the bin max option.
        
        """
        bin_max = self.bin_max

        if (bin_max + 1) <= self.bm_max:
            self.bin_max += 1
            self.isi_options.binMaxEdit.setText(str(self.bin_max))
            self.update()

    def on_max_minus(self):
        """
        This method is called if you click on the minus button
        for the bin max option.
        
        Decrements the bin max option.
        
        """
        bin_max = self.bin_max
        if (bin_max - 1) > self.bm_min and (bin_max - 1) > self.bin_step:
            self.bin_max -= 1
            self.isi_options.binMaxEdit.setText(str(self.bin_max))
            self.update()

    def on_step_plus(self):
        """
        This method is called if you click on the plus button
        for the bin step option.
        
        Increments the bin step option.
        
        """
        bin_step = self.bin_step
        if (bin_step + 1) <= self.bs_max:
            self.bin_step += 1
            self.isi_options.binStepEdit.setText(str(self.bin_step))
            self.update()

    def on_step_minus(self):
        """
        This method is called if you click on the minus button
        for the bin step option.
        
        Decrements the bin step option.
        
        """
        bin_step = self.bin_step
        if (bin_step - 1) > self.bs_min:
            self.bin_step -= 1
            self.isi_options.binStepEdit.setText(str(self.bin_step))
            self.update()

    def bin_max_changed(self, value):
        """
        This method is called if you edit the bin max option.
        
        Checks if the bin max is correct.
        
        """
        bin_max = value
        try:
            bin_max = float(bin_max)
            if self.bm_min < bin_max <= self.bm_max:
                self.bin_max = bin_max
                self.isi_options.error_label.setText("")
            else:
                self.isi_options.error_label.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.isi_options.error_label.setText("Invalid input!")

    def bin_step_changed(self, value):
        """
        This method is called if you edit the bin step option.
        
        Checks if the bin step is correct.
        
        """
        bin_step = value
        try:
            bin_step = float(bin_step)
            if self.bs_min < bin_step <= self.bs_max:
                self.bin_step = bin_step
                self.isi_options.error_label.setText("")
            else:
                self.isi_options.error_label.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.isi_options.error_label.setText("Invalid input!")

    def step_mode_changed(self):

        current_step_mode = self.step_mode
        new_step_mode = self.isi_options.histStyleCheckbox.isChecked()

        if current_step_mode != new_step_mode:
            self.step_mode = new_step_mode
            self.update()

    def plot_histogram(self, x, y, color, unit_id, session, clickable=False):
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
        self.histograms.append(self.make_plot(x=x, y=y, color=color, unit_id=unit_id, session=session,
                                              clickable=clickable, stepMode=self.step_mode))

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
        self.clear_()
        self.datas = {}
        if self.toolbar.activate_button.current_state:

            layer = self.toolbar.get_checked_layers()[0]

            active = vum.get_active()

            if layer == "pooled":
                clickable = False
                intervals = {}
                for session in range(len(active)):
                    for unit_id in range(len(active[session])):
                        if unit_id not in intervals:
                            intervals[unit_id] = []
                        if active[session][unit_id]:
                            runit = vum.get_realunit(session, unit_id, data)
                            d = data.get_data("sessions", runit)
                            intervals[unit_id].extend(d)
                            col = vum.get_colour(unit_id)
                            self.datas[unit_id] = [np.sort(intervals[unit_id]), col, unit_id, session, clickable]

                if intervals:
                    for key in self.datas.keys():
                        y = np.histogram(self.datas[key][0],
                                         bins=np.arange(0., self.bin_max / 1000., self.bin_step / 1000.))
                        tmp = y[1]
                        if self.step_mode:
                            tmp = tmp[:]
                        else:
                            tmp = tmp[:-1]
                        self.plot_histogram(x=tmp, y=y[0] / (1.0 * len(self.datas[key][0])), color=self.datas[key][1],
                                            unit_id=self.datas[key][2], session=self.datas[key][3],
                                            clickable=self.datas[key][4])
                self.set_x_label("Inter-spike Interval", "s")
                self.set_y_label("Normalized Percentage of Interval Counts")
                self.set_plot_title("Inter-spike Interval Histograms")
            elif layer == "individual":
                for session in range(len(active)):
                    for unit_id in range(len(active[session])):
                        if active[session][unit_id]:
                            runit = vum.get_realunit(session, unit_id, data)
                            datas = data.get_data("units", runit)
                            col = vum.get_colour(unit_id)
                            clickable = True
                            self.datas["{}{}".format(session, unit_id)] = [datas, col, unit_id, session, clickable]
                            for d in datas:
                                y = np.histogram(d, bins=np.arange(0., self.bin_max / 1000., self.bin_step / 1000.))
                                tmp = y[1]
                                if self.step_mode:
                                    tmp = tmp[:]
                                else:
                                    tmp = tmp[:-1]
                                self.plot_histogram(x=tmp, y=y[0] / (1.0 * len(d)), color=col, unit_id=unit_id,
                                                    session=session, clickable=clickable)
                self.set_x_label("Inter-spike Interval", "s")
                self.set_y_label("Normalized Percentage of Interval Counts")
                self.set_plot_title("Inter-spike Interval Histograms")
            self.connect_plots()

    def update(self):
        self.clear_()
        for key in self.datas:
            datas = self.datas[key]
            data = datas[0]
            col = datas[1]
            unit_id = datas[2]
            session = datas[3]
            clickable = datas[4]
            for d in data:
                y = np.histogram(d, bins=np.arange(0., self.bin_max / 1000., self.bin_step / 1000.))
                tmp = y[1]
                if self.step_mode:
                    tmp = tmp[:]
                else:
                    tmp = tmp[:-1]
                self.plot_histogram(x=tmp, y=y[0] / (1.0 * len(d)), color=col,
                                    unit_id=unit_id, session=session, clickable=clickable)
                self.set_x_label("Inter-spike Interval", "s")
                self.set_y_label("Normalized Percentage of Interval Counts")
                self.set_plot_title("Inter-spike Interval Histograms")
        self.connect_plots()

    def connect_plots(self):
        for item in self.histograms:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.get_item)

    def clear_(self):
        self.histograms = []
        self.clear_all()

    def increment_bins(self, step=1):
        self.bins += step
        self.update()

    def decrement_bins(self, step=1):
        self.bins -= step
        self.update()
