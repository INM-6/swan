"""
Created on Feb 23, 2018

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
# system imports
import numpy as np
import quantities as pq
from neo import SpikeTrain
from elephant.statistics import instantaneous_rate
from elephant.kernels import GaussianKernel
from pyqtgraph.Qt import QtWidgets, QtCore

# swan-specific imports
from swan.widgets.mypgwidget import PyQtWidget2d
from swan.gui.rate_profile_options_ui import RpOptionsUi


class PgWidgetRateProfile(PyQtWidget2d):
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
        self.rate_profiles = []
        self.datas = {}

        self.time_pre = -1000
        self.time_post = 1500
        self.sampling_period = 5
        self.kernel_width = 60.0
        self.trigger_event = ""
        self.border_correction_multiplier = 1

        self.time_pre_min, self.time_pre_max = -5000.0, -1.0
        self.time_post_min, self.time_post_max = 1.0, 5000.0
        self.sampling_period_min, self.sampling_period_max = 1.0, 5000.0
        self.kernel_width_min, self.kernel_width_max = 1.0, 500.0

        self.events = {}

        self.rate_profile_settings = RpOptionsUi(self)

        self.show_grid()

    def on_enter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.
        
        Redraws everything.
        
        """
        time_pre = self.rate_profile_settings.timePre.text()
        time_post = self.rate_profile_settings.timePost.text()
        sampling_period = self.rate_profile_settings.samplingPeriod.text()
        kernel_width = self.rate_profile_settings.kernelWidth.text()

        try:
            time_pre = float(time_pre)
            time_post = float(time_post)
            sampling_period = float(sampling_period)
            kernel_width = float(kernel_width)

            if self.time_pre_max > time_pre > self.time_pre_min \
                    and self.time_post_min < time_post < self.time_post_max \
                    and self.sampling_period_min < sampling_period < self.sampling_period_max \
                    and self.kernel_width_min < kernel_width < self.kernel_width_max:

                self.time_pre = time_pre
                self.time_post = time_post
                self.sampling_period = sampling_period
                self.kernel_width = kernel_width
                self.update_plot()
                self.rate_profile_settings.errorLabel.setText("")
            else:
                self.rate_profile_settings.errorLabel.setText("Values outside acceptable limits!")
        except Exception as e:
            print(e)
            self.rate_profile_settings.errorLabel.setText("Invalid inputs!")

    def on_time_pre_changed(self, value):
        """
        This method is called if you edit the T-Pre option.
        
        Checks if the T-Pre is correct.
        
        """
        time_pre = value
        try:
            time_pre = float(time_pre)
            if self.time_pre_max > time_pre > self.time_pre_min:
                self.time_pre = time_pre
                self.rate_profile_settings.errorLabel.setText("")
            else:
                self.rate_profile_settings.errorLabel.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.rate_profile_settings.errorLabel.setText("Invalid input!")

    def on_time_post_changed(self, value):
        """
        This method is called if you edit the T-Post option.
        
        Checks if the T-Post is correct.
        
        """
        t_post = value
        try:
            t_post = float(t_post)
            if self.time_post_min < t_post < self.time_post_max:
                self.time_post = t_post
                self.rate_profile_settings.errorLabel.setText("")
            else:
                self.rate_profile_settings.errorLabel.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.rate_profile_settings.errorLabel.setText("Invalid input!")

    def on_sampling_period_changed(self, value):
        """
        This method is called if you edit the sampling period option.
        
        Checks if the sampling period is correct.
        
        """
        sampling_period = value
        try:
            sampling_period = float(sampling_period)
            if self.sampling_period_min < sampling_period < self.sampling_period_max:
                self.sampling_period = sampling_period
                self.rate_profile_settings.errorLabel.setText("")
            else:
                self.rate_profile_settings.errorLabel.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.rate_profile_settings.errorLabel.setText("Invalid input!")

    def on_kernel_width_changed(self, value):
        """
        This method is called if you edit the kernel width option.
        
        Checks if the sampling period is correct.
        
        """
        kernel_width = value
        try:
            kernel_width = float(kernel_width)
            if self.kernel_width_min < kernel_width < self.kernel_width_max:
                self.kernel_width = kernel_width
                self.rate_profile_settings.errorLabel.setText("")
            else:
                self.rate_profile_settings.errorLabel.setText("Value outside acceptable limits!")

        except Exception as e:
            print(e)
            self.rate_profile_settings.errorLabel.setText("Invalid input!")

    @staticmethod
    def create_raster_psth(spiketrain, trigger, timerange, border_correction=0.0):
        """
        It calculates a list of concatenated spikes around stimulus onset and offset, for a later PSTH analysis.

        :param spiketrain: list with spike times
        :param trigger:    list with timings of the trigger
        :param timerange:  time range for the PSTHs
        :param border_correction: time window around edges to use for border correction

        :return: raster_trig
        """

        if len(spiketrain) < 2:
            # raise(ValueError, "The spiketrain contains fewer than 2 spikes.")
            print("The spiketrain contains fewer than 2 spikes. Returning empty list.")
            return []

        border_correction = border_correction * pq.ms

        spiketrain = spiketrain * pq.ms

        # find period of activity (poa)
        poa_start = spiketrain[0]
        poa_stop = spiketrain[-1]

        trig_unit = trigger[(trigger >= poa_start) & (trigger <= poa_stop)]

        if len(trig_unit) < 1:
            print('-- No neural activity during this block for this neuronID')
            return []

        # extract spike times around saccade and fixation
        raster_trig = []  # spikes around trig
        for i_trig, t_trig in enumerate(trig_unit):
            mask_trig = (spiketrain >= (t_trig + timerange[0] * pq.ms - border_correction)) & \
                        (spiketrain <= (t_trig + timerange[1] * pq.ms + border_correction))
            spikes = spiketrain[mask_trig] - t_trig
            raster_trig.append(spikes.magnitude)

        return raster_trig

    def compute_psth_from_raster(self, array_raster_trig, timerange, minimum_spikes=10, border_correction=0.0):
        """

        :param array_raster_trig:
        :param timerange:
        :param minimum_spikes:
        :param border_correction:
        :return:
        """

        out = dict()
        if len(array_raster_trig) < 1:
            print('PSTH not computed due to lack of spikes.')
            out["values"] = np.array([])
            out["times"] = []
            return out

        raster_trig = np.sort(np.hstack(array_raster_trig))
        if len(raster_trig) <= minimum_spikes:
            print('PSTH not computed due to lack of spikes.')
            out["values"] = np.array([])
            out["times"] = []
            return out

        rate_estimate, psth_times = self.calc_rate_estimate(raster_trig, timerange,
                                                            sampling_period=self.sampling_period,
                                                            kernel_width=self.kernel_width,
                                                            border_correction=border_correction)
        psth_trig = rate_estimate / float(len(array_raster_trig))
        psth_trig = np.array(psth_trig)[:, 0]

        return psth_times, psth_trig

    @staticmethod
    def calc_rate_estimate(spike_times, timerange, sampling_period,
                           kernel_width, border_correction):
        """
        :param spike_times: array of spike times
        :param timerange: tuple or list of times between which to calculate PSTH
        :param sampling_period: sampling period for calculating PSTH
        :param kernel_width: width of kernel (in ms) used for PSTH
        :param border_correction: time window around edges to use to negate border effects in PSTH

        :return rate_estimate: array containing the time scale of the rate estimate
        :return kernel_width: array containing the values of the rate estimate
        """
        t_start = timerange[0] - border_correction
        t_stop = timerange[1] + border_correction
        mask = (spike_times >= t_start) & (spike_times <= t_stop)
        spiketrain = spike_times[mask].copy()
        if len(spiketrain) < 2:
            times = np.linspace(t_start, t_stop, int((t_stop - t_start) * 1000 / sampling_period),
                                endpoint=False)
            rate = np.zeros_like(times)
            return rate, times

        spike_train = SpikeTrain(spiketrain * pq.ms, t_start=t_start * pq.ms, t_stop=t_stop * pq.ms)
        rate_estimate = instantaneous_rate(spike_train, sampling_period=sampling_period * pq.ms,
                                           kernel=GaussianKernel(kernel_width * pq.ms))
        rate_estimate = rate_estimate.time_slice(t_start=timerange[0] * pq.ms, t_stop=timerange[1] * pq.ms)
        return rate_estimate.rescale('Hz').magnitude, rate_estimate.times.rescale('s').magnitude

    def compute_psth(self, spiketrain, trigger, timerange, minimum_spikes, border_correction):
        """
        Calculates the peri-stimulus time histogram for the given spiketrain around the given event time stamps.

        :param spiketrain: Array of spike times in units of milliseconds
        :param trigger: Array of event timestamps in units of milliseconds
        :param timerange: List or tuple containing tPre and tPost values with which to calculate the PSTH
        :param minimum_spikes: Minimum spikes required in spiketrain (and around trigger) to calculate PSTH
        :param border_correction: Time (in milliseconds) to be used to correct for edge effects in PSTH

        :return psth_times: Array of times (in seconds)
        :return psth_trig: Array of values corresponding to psth_times (in Herz)
        """

        if len(spiketrain) < minimum_spikes:
            # raise(ValueError, "The spiketrain contains fewer than 2 spikes.")
            # print("The spiketrain contains fewer than 2 spikes. Returning empty list.")
            return [], []

        # choose saccades within the period of activity
        trig_unit = trigger[(trigger >= spiketrain[0]) & (trigger <= spiketrain[-1])]

        if len(trig_unit) < 1:
            # print('-- No neural activity during this block for this neuronID')
            return [], []

        # extract spike times around saccade and fixation
        raster_trig_list = []  # spikes around trig
        for i_trig, t_trig in enumerate(trig_unit):
            mask_trig = (spiketrain >= (t_trig + timerange[0] - border_correction)) & \
                        (spiketrain <= (t_trig + timerange[1] + border_correction))
            spikes = spiketrain[mask_trig] - t_trig
            raster_trig_list.append(spikes)

        if len(raster_trig_list) < 1:
            return [], []

        raster_trig = np.sort(np.hstack(raster_trig_list))

        if len(raster_trig) <= minimum_spikes:
            return [], []

        rate_estimate, psth_times = self.calc_rate_estimate(raster_trig, timerange,
                                                            sampling_period=self.sampling_period,
                                                            kernel_width=self.kernel_width,
                                                            border_correction=border_correction)
        if rate_estimate.size == psth_times.size == 0:
            return [], []
        else:
            psth_trig = rate_estimate / float(len(raster_trig_list))
            psth_trig = np.array(psth_trig)[:, 0]

            return psth_times, psth_trig

    def plot_profile(self, x, y, color, unit_id, session, clickable=False):
        """
        Plot the rate profile onto the plot widget and also append it to self._profiles.

        :param x: x values of data to be plotted
        :param y: y values of data to be plotted
        :param color: color of the plotted line
        :param unit_id: global unit id (row number)
        :param session: session id (column number)
        :param clickable: toggle response to left mouse-clicks.
        :return:
        """
        self.rate_profiles.append(self.make_plot(x=x, y=y, color=color,
                                                 unit_id=unit_id, session=session,
                                                 clickable=clickable))

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
        self.datas = {}

        if self.toolbar.activate_button.current_state:

            layer = self.toolbar.get_checked_layers()[0]
            active = vum.get_active()
            self.events = data.get_events_dict()

            self.populate_event_list()

            for session in range(len(active)):
                for global_unit_id in range(len(active[session])):
                    if active[session][global_unit_id]:
                        unit = vum.get_realunit(session, global_unit_id, data)
                        spiketrain = data.get_data("spiketrain", unit)
                        col = vum.get_colour(global_unit_id)
                        self.datas[(session, global_unit_id)] = [spiketrain, col, True]

            if self.trigger_event in self.events.keys():
                paramaters = {
                    'trigger_event': self.trigger_event,
                    'bcm': self.border_correction_multiplier,
                    'kernel_width': self.kernel_width,
                    't_pre': self.time_pre,
                    't_post': self.time_post
                }
                profiles = dict()

                worker = RateProfileWorker(self.datas, profiles, self.events, paramaters, self.compute_psth)
                worker.start()
                while worker.isRunning():
                    self._processing = worker.isRunning()
                    self.rate_profile_settings.errorLabel.setText('Processing...')
                    QtWidgets.QApplication.processEvents()
                self._processing = worker.isRunning()
                self.rate_profile_settings.errorLabel.setText('')

                self.clear_()
                if layer == "individual":
                    for key in profiles:
                        self.plot_profile(x=profiles[key][0], y=profiles[key][1],
                                          color=self.datas[key][1],
                                          unit_id=key[1],
                                          session=key[0],
                                          clickable=self.datas[key][2])

                elif layer == "pooled":
                    pooled_profiles = {}
                    for key in profiles:
                        session, global_unit_id = key
                        if len(profiles[key][0]) > 0 and len(profiles[key][1]) > 0:
                            if pooled_profiles.get(global_unit_id, None) is None:
                                pooled_profiles[global_unit_id] = profiles[key] + [self.datas[key][1]]
                            else:
                                pooled_profiles[global_unit_id][1] += profiles[key][1]

                    for key in pooled_profiles:
                        self.plot_profile(x=pooled_profiles[key][0], y=pooled_profiles[key][1],
                                          color=pooled_profiles[key][2],
                                          unit_id=key,
                                          session=-1,
                                          clickable=False)

                self.create_vertical_line(xval=0)
                self.set_x_label("Time", "s")
                self.set_y_label("Frequency", "Hz")
                self.set_plot_title("Rate Profiles around trigger {}".format(self.trigger_event))
                self.connect_plots()

        else:
            self.clear_()

    def update_plot(self):
        layer = self.toolbar.get_checked_layers()[0]

        paramaters = {
            'trigger_event': self.trigger_event,
            'bcm': self.border_correction_multiplier,
            'kernel_width': self.kernel_width,
            't_pre': self.time_pre,
            't_post': self.time_post
        }
        profiles = dict()

        worker = RateProfileWorker(self.datas, profiles, self.events, paramaters, self.compute_psth)
        worker.start()
        while worker.isRunning():
            self._processing = worker.isRunning()
            self.rate_profile_settings.errorLabel.setText('Processing...')
            QtWidgets.QApplication.processEvents()
        self._processing = worker.isRunning()
        self.rate_profile_settings.errorLabel.setText('')

        self.clear_()
        if layer == "individual":
            for key in profiles:
                self.plot_profile(x=profiles[key][0], y=profiles[key][1],
                                  color=self.datas[key][1],
                                  unit_id=key[1],
                                  session=key[0],
                                  clickable=self.datas[key][2])

        elif layer == "pooled":
            pooled_profiles = {}
            for key in profiles:
                session, global_unit_id = key
                if len(profiles[key][0]) > 0 and len(profiles[key][1]) > 0:
                    if pooled_profiles.get(global_unit_id, None) is None:
                        pooled_profiles[global_unit_id] = profiles[key] + [self.datas[key][1]]  # set y-values for gid
                    else:
                        pooled_profiles[global_unit_id][1] += profiles[key][1]  # increment y-values for gid

            for key in pooled_profiles:
                self.plot_profile(x=pooled_profiles[key][0], y=pooled_profiles[key][1],
                                  color=pooled_profiles[key][2],
                                  unit_id=key,
                                  session=-1,
                                  clickable=False)

        self.create_vertical_line(xval=0)
        self.set_x_label("Time", "s")
        self.set_y_label("Frequency", "Hz")
        self.set_plot_title("Rate Profiles around trigger {}".format(self.trigger_event))
        self.connect_plots()

    def connect_plots(self):
        for item in self.rate_profiles:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.get_item)

    def clear_(self):

        self.rate_profiles = []
        self.clear_all()

    def change_trigger_event(self, text):

        if text == "":
            self.clear_()
        else:
            self.trigger_event = text
            self.update_plot()

    def populate_event_list(self):

        event_dict = self.events
        self.rate_profile_settings.eventDropDown.clear()
        self.rate_profile_settings.eventDropDown.addItems([""] + sorted(event_dict.keys()))


class RateProfileWorker(QtCore.QThread):

    def __init__(self, data_dictionary, output_dictionary, event_dictionary, param_dictionary, compute_function):

        QtCore.QThread.__init__(self)
        self.data_dictionary = data_dictionary
        self.output_dictionary = output_dictionary
        self.event_dictionary = event_dictionary
        self.parameters = param_dictionary
        self.compute_function = compute_function

    def run(self):
        for key in self.data_dictionary.keys():
            session, global_unit_id = key[0], key[1]
            try:
                event_times = self.event_dictionary[self.parameters['trigger_event']][session][0][0]
            except IndexError:
                event_times = np.array([]) * pq.ms
            unit_data = self.data_dictionary[key]
            spiketrain, color, clickable = unit_data

            times, values = self.compute_function(
                spiketrain=spiketrain.rescale(pq.ms).magnitude, trigger=event_times.rescale(pq.ms).magnitude,
                timerange=[self.parameters['t_pre'], self.parameters['t_post']], minimum_spikes=10,
                border_correction=self.parameters['bcm'] * self.parameters['kernel_width']
            )

            self.output_dictionary[key] = [times, values]
