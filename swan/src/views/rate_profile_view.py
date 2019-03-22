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
from time import time
from PyQt5 import QtCore, QtGui

# swan-specific imports
from swan.src.widgets.mypgwidget import PyQtWidget2d
from swan.gui.rpOptions_ui import Ui_rpOptions


class pgWidgetRateProfile(PyQtWidget2d):
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

        layers = ["individual", "pooled"]
        self.toolbar.setupRadioButtons(layers)
        self.toolbar.doLayer.connect(self.triggerRefresh)

        self._plotItem = self.pgCanvas.getPlotItem()
        self._plotItem.enableAutoRange()
        self._profiles = []
        self.datas = {}

        self.tPre = -150
        self.tPost = 350
        self.samplingPeriod = 10
        self.kernelWidth = 60.0
        self.triggerEvent = ""
        self.border_correction_multiplier = 1

        self.events = {}

        self.rpOptions = Ui_rpOptions(self)

        self.showGrid()

    #### general methods ####

    def onEnter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.
        
        Redraws everything.
        
        """
        tPre = self.rpOptions.timePre.text()
        tPost = self.rpOptions.timePost.text()
        samplingPeriod = self.rpOptions.samplingPeriod.text()
        kernelWidth = self.rpOptions.kernelWidth.text()

        try:
            tPre = float(tPre)
            tPost = float(tPost)
            samplingPeriod = float(samplingPeriod)
            kernelWidth = float(kernelWidth)

            if -1 > tPre > -5000.0 \
                    and 1 < tPost < 5000.0 \
                    and 1.0 < samplingPeriod < 5000.0 \
                    and 10.0 < kernelWidth < 500.0:

                self.tPre = tPre
                self.tPost = tPost
                self.samplingPeriod = samplingPeriod
                self.kernelWidth = kernelWidth
                self.update_plot()
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Values outside acceptable limits!")
        except:
            self.rpOptions.errorLabel.setText("Invalid inputs!")

    def onTPreChanged(self, value):
        """
        This method is called if you edit the T-Pre option.
        
        Checks if the T-Pre is correct.
        
        """
        tPre = value
        try:
            tPre = float(tPre)
            if -1 > tPre > -5000.0:
                self.tPre = tPre
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.rpOptions.errorLabel.setText("Invalid input!")

    def onTPostChanged(self, value):
        """
        This method is called if you edit the T-Post option.
        
        Checks if the T-Post is correct.
        
        """
        tPost = value
        try:
            tPost = float(tPost)
            if tPost > 1 and tPost < 5000.0:
                self.tPost = tPost
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.rpOptions.errorLabel.setText("Invalid input!")

    def onSamplingPeriodChanged(self, value):
        """
        This method is called if you edit the sampling period option.
        
        Checks if the sampling period is correct.
        
        """
        samplingPeriod = value
        try:
            samplingPeriod = float(samplingPeriod)
            if samplingPeriod > 1.0 and samplingPeriod < 5000.0:
                self.samplingPeriod = samplingPeriod
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.rpOptions.errorLabel.setText("Invalid input!")

    def onKernelWidthChanged(self, value):
        """
        This method is called if you edit the kernel width option.
        
        Checks if the sampling period is correct.
        
        """
        kernelWidth = value
        try:
            kernelWidth = float(kernelWidth)
            if kernelWidth > 10.0 and kernelWidth < 500.0:
                self.kernelWidth = kernelWidth
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.rpOptions.errorLabel.setText("Invalid input!")

    def create_raster_psth(self, spiketrain, trigger, timerange, border_correction=0.0):
        '''
        It calculates a list of concatenated spikes around stimulus onset and offset, for a later PSTH analysis.

        :param spiketrain: list with spike times
        :param trigger:    list with timings of the trigger
        :param timerange:  time range for the PSTHs
        :param border_correction: time window around edges to use for border correction
    
        :return: raster_trig
        '''

        if len(spiketrain) < 2:
            # raise(ValueError, "The spiketrain contains fewer than 2 spikes.")
            print("The spiketrain contains fewer than 2 spikes. Returning empty list.")
            return []

        border_correction = border_correction * pq.ms

        spiketrain = spiketrain * pq.ms

        ## find period of activity (poa)
        poa_start = spiketrain[0]
        poa_stop = spiketrain[-1]

        ## choose saccades within the period of activity
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

        rate_estimate, PSTH_times = self.calc_rate_estimate(raster_trig, timerange, sampling_period=self.samplingPeriod,
                                                            kernel_width=self.kernelWidth,
                                                            border_correction=border_correction)
        PSTH_trig = rate_estimate / float(len(array_raster_trig))
        PSTH_trig = np.array(PSTH_trig)[:, 0]

        return PSTH_times, PSTH_trig

    def calc_rate_estimate(self, spike_times, timerange, sampling_period,
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

        :return PSTH_times: Array of times (in seconds)
        :return PSTH_trig: Array of values corresponding to PSTH_times (in Herz)
        """

        if len(spiketrain) < minimum_spikes:
            # raise(ValueError, "The spiketrain contains fewer than 2 spikes.")
            # print("The spiketrain contains fewer than 2 spikes. Returning empty list.")
            return [], []

        ## choose saccades within the period of activity
        trig_unit = trigger[(trigger >= spiketrain[0]) & (trigger <= spiketrain[-1])]

        if len(trig_unit) < 1:
            # print('-- No neural activity during this block for this neuronID')
            return [], []

        # extract spike times around saccade and fixation
        raster_trig = []  # spikes around trig
        for i_trig, t_trig in enumerate(trig_unit):
            mask_trig = (spiketrain >= (t_trig + timerange[0] - border_correction)) & \
                        (spiketrain <= (t_trig + timerange[1] + border_correction))
            spikes = spiketrain[mask_trig] - t_trig
            raster_trig.append(spikes)

        if len(raster_trig) < 1:
            return [], []

        raster_trig = np.sort(np.hstack(raster_trig))

        if len(raster_trig) <= minimum_spikes:
            return [], []

        rate_estimate, PSTH_times = self.calc_rate_estimate(raster_trig, timerange,
                                                            sampling_period=self.samplingPeriod,
                                                            kernel_width=self.kernelWidth,
                                                            border_correction=border_correction)
        if rate_estimate.size == PSTH_times.size == 0:
            return [], []
        else:
            PSTH_trig = rate_estimate / float(len(raster_trig))
            PSTH_trig = np.array(PSTH_trig)[:, 0]

            return PSTH_times, PSTH_trig

    def plotProfile(self, x, y, color, unit_id, session, clickable=False):
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
        self._profiles.append(self.makePlot(x=x, y=y, color=color,
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
        if self.toolbar.layers.isChecked():

            layer = self.toolbar.getCheckedLayers()[0]
            active = vum.get_active()
            self.events = data.get_events_dict()

            self.populateEventList()

            if layer == "individual":
                clickable = True
                for session in range(len(active)):
                    for global_unit_id in range(len(active[session])):
                        if active[session][global_unit_id]:
                            unit = vum.get_realunit(session, global_unit_id, data)
                            spiketrain = data.get_data("spiketrain", unit)
                            col = vum.get_color(global_unit_id, False, layer, False)
                            self.datas[(session, global_unit_id)] = [spiketrain, col, clickable]

                if self.triggerEvent in self.events.keys():
                    paramaters = {
                        'trigger_event': self.triggerEvent,
                        'bcm': self.border_correction_multiplier,
                        'kernel_width': self.kernelWidth,
                        't_pre': self.tPre,
                        't_post': self.tPost
                    }
                    profiles = dict()

                    worker = RateProfileWorker(self.datas, profiles, self.events, paramaters, self.compute_psth)
                    worker.start()
                    while worker.isRunning():
                        self._processing = worker.isRunning()
                        self.rpOptions.errorLabel.setText('Processing...')
                        QtGui.QApplication.processEvents()
                    self._processing = worker.isRunning()
                    self.rpOptions.errorLabel.setText('')

                    self.clear_()
                    for key in profiles:
                        self.plotProfile(x=profiles[key][0], y=profiles[key][1],
                                         color=self.datas[key][1],
                                         unit_id=key[1],
                                         session=key[0],
                                         clickable=self.datas[key][2])

                    self.createVerticalLine(xval=0)
                    self.setXLabel("Time", "s")
                    self.setYLabel("Frequency", "Hz")
                    self.setPlotTitle("Rate Profiles around trigger {}".format(self.triggerEvent))
                    self.connectPlots()

            elif layer == "pooled":
                raise ValueError("Layer not supported.")

    def update_plot(self):
        paramaters = {
            'trigger_event': self.triggerEvent,
            'bcm': self.border_correction_multiplier,
            'kernel_width': self.kernelWidth,
            't_pre': self.tPre,
            't_post': self.tPost
        }
        profiles = dict()

        worker = RateProfileWorker(self.datas, profiles, self.events, paramaters, self.compute_psth)
        worker.start()
        while worker.isRunning():
            self._processing = worker.isRunning()
            self.rpOptions.errorLabel.setText('Processing...')
            QtGui.QApplication.processEvents()
        self._processing = worker.isRunning()
        self.rpOptions.errorLabel.setText('')

        self.clear_()
        for key in profiles:
            self.plotProfile(x=profiles[key][0], y=profiles[key][1],
                             color=self.datas[key][1],
                             unit_id=key[1],
                             session=key[0],
                             clickable=self.datas[key][2])
        self.createVerticalLine(xval=0)
        self.setXLabel("Time", "s")
        self.setYLabel("Frequency", "Hz")
        self.setPlotTitle("Rate Profiles around trigger {}".format(self.triggerEvent))
        self.connectPlots()

    def connectPlots(self):
        for item in self._profiles:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.getItem)

    def clear_(self):

        self._profiles = []
        self.clearAll()

    def changeTriggerEvent(self, text):

        if text == "":
            self.clear_()
        else:
            self.triggerEvent = text
            self.update_plot()

    def populateEventList(self):

        eventDict = self.events
        self.rpOptions.eventDropDown.clear()
        self.rpOptions.eventDropDown.addItems([""] + sorted(eventDict.keys()))


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
