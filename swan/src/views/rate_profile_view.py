"""
Created on Feb 23, 2018

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.src.widgets.mypgwidget import PyQtWidget2d
import numpy as np
import quantities as pq
from neo import SpikeTrain
from elephant.statistics import instantaneous_rate
from elephant.statistics import sskernel
from elephant.kernels import GaussianKernel
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
                self.update()
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

    def create_raster_psth(self, spiketrain, trigger, timerange, border_correction=0):
        '''
        It calculates a list of concatenated spikes around stimulus onset and offset, for a later PSTH analysis.
    
        :param spiketrain: list with spike times
        :param trigger:    list with timings of the trigger
        :param timerange:  time range for the PSTHs
    
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

    def compute_psth_from_raster(self, array_raster_trig, timerange, minimum_spikes=10, border_correction=0):

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

        out['values'] = PSTH_trig
        out['times'] = PSTH_times
        return out

    def calc_rate_estimate(self, spike_times, timerange, sampling_period=2.0,
                           kernel_width="auto", border_correction=0):  # version=v2 => kfactor = 1.0/2.0/2.7
        """
        :param spike_times: array of spike times
        :return rate_estimate: neo object containing rate estimate and time scale
        :return kernel_width: optimized kernel width for the calculation of the rate estimate
        """
        t_start = timerange[0] - border_correction
        t_stop = timerange[1] + border_correction
        mask = (spike_times >= t_start) & (spike_times <= t_stop)
        spiketrain = spike_times[mask].copy()
        if len(spiketrain) < 2:
            times = np.linspace(t_start, t_stop, int((t_stop - t_start) * 1000 / sampling_period),
                                endpoint=False)
            rate = np.zeros_like(times)
            kw = 0
            return rate, times, kw

        if kernel_width == "auto":
            kernel_width = sskernel(spiketrain, tin=None, bootstrap=False)['optw']

        spike_train = SpikeTrain(spiketrain * pq.ms, t_start=t_start * pq.ms, t_stop=t_stop * pq.ms)
        rate_estimate = instantaneous_rate(spike_train, sampling_period=sampling_period * pq.ms,
                                           kernel=GaussianKernel(kernel_width * pq.ms))
        rate_estimate = rate_estimate.time_slice(t_start=timerange[0] * pq.ms, t_stop=timerange[1] * pq.ms)
        return rate_estimate.rescale('Hz').magnitude, rate_estimate.times.rescale('s').magnitude

    def plotProfile(self, x, y, color, unit_id, session, clickable=False):
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
        self._profiles.append(self.makePlot(x=x, y=y, color=color, unit_id=unit_id, session=session, clickable=clickable))

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
        if self.toolbar.layers.isChecked():

            layer = self.toolbar.getCheckedLayers()[0]
            active = vum.get_active()
            event_dict = data.get_events_dict()
            self.events = event_dict
            triggerEvent = self.triggerEvent
            bcm = self.border_correction_multiplier

            self.populateEventList()

            if layer == "individual":
                clickable = True
                for session in range(len(active)):
                    for unit_id in range(len(active[session])):
                        if active[session][unit_id]:
                            runit = vum.get_realunit(session, unit_id, data)
                            spiketrain = data.get_data("spiketrain", runit)
                            col = vum.get_color(unit_id, False, layer, False)
                            self.datas["{}{}".format(session, unit_id)] = [spiketrain, col, clickable]

                if triggerEvent in event_dict.keys():
                    for key in self.datas.keys():
                        pos = list(key)
                        session, unit_id = int(pos[0]), int(pos[1])
                        if active[session][unit_id]:
                            event_times = event_dict[triggerEvent][session][0][0]
                            plotData = self.datas[key]
                            spiketrain, color, clickable = plotData
                            raster = self.create_raster_psth(spiketrain=spiketrain.rescale(pq.ms).magnitude,
                                                             trigger=event_times.rescale(pq.ms),
                                                             timerange=[self.tPre, self.tPost],
                                                             border_correction=bcm * self.kernelWidth)
                            result = self.compute_psth_from_raster(array_raster_trig=raster,
                                                                   timerange=[self.tPre, self.tPost],
                                                                   minimum_spikes=10,
                                                                   border_correction=bcm * self.kernelWidth)
                            self.plotProfile(x=result['times'], y=result['values'],
                                             color=color, unit_id=unit_id,
                                             session=session, clickable=clickable)
                    self.createVerticalLine(xval=0)
                    self.setXLabel("Time", "ms")
                    self.setYLabel("Frequency", "Hz")
                    self.setPlotTitle("Rate Profiles around trigger {}".format(triggerEvent))
                    self.connectPlots()

            elif layer == "pooled":
                raise ValueError("Layer not supported.")

    def update(self):
        self.clear_()
        triggerEvent = self.triggerEvent
        event_dict = self.events
        bcm = self.border_correction_multiplier
        for key in self.datas.keys():
            pos = list(key)
            session, unit_id = int(pos[0]), int(pos[1])
            event_times = event_dict[triggerEvent][session][0][0]
            plotData = self.datas[key]
            spiketrain, color, clickable = plotData
            raster = self.create_raster_psth(spiketrain=spiketrain.rescale(pq.ms).magnitude,
                                             trigger=event_times.rescale(pq.ms),
                                             timerange=[self.tPre, self.tPost],
                                             border_correction=bcm * self.kernelWidth)
            result = self.compute_psth_from_raster(array_raster_trig=raster,
                                                   timerange=[self.tPre, self.tPost],
                                                   minimum_spikes=10,
                                                   border_correction=bcm * self.kernelWidth)
            self.plotProfile(x=result['times'], y=result['values'], color=color,
                             unit_id=unit_id, session=session, clickable=clickable)
        self.createVerticalLine(xval=0)
        self.setXLabel("Time", "s")
        self.setYLabel("Frequency", "Hz")
        self.setPlotTitle("Rate Profiles around trigger {}".format(triggerEvent))
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
            self.clearAll()
        else:
            self.triggerEvent = text
            self.update()

    def populateEventList(self):

        eventDict = self.events
        self.rpOptions.eventDropDown.clear()
        self.rpOptions.eventDropDown.addItems([""] + sorted(eventDict.keys()))
