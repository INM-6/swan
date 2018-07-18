"""
Created on Feb 23, 2018

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget2d
import numpy as np
import quantities as pq
from neo import SpikeTrain
from elephant.statistics import instantaneous_rate
from elephant.statistics import sskernel
from elephant.kernels import GaussianKernel
from gui.rpOptions_ui import Ui_rpOptions

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
        
        layers = ["session wise", "unit wise"]
        self.toolbar.setupRadioButtons(layers)
        self.toolbar.doLayer.connect(self.triggerRefresh)
        
        self._plotItem = self.pgCanvas.getPlotItem()
        self._plotItem.enableAutoRange()
        self._profiles = []
        self.datas = {}
        
        self.tPre = -0.15
        self.tPost = 0.35
        self.samplingPeriod = 2.0
        self.triggerEvent = ""
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
        
        try:
            tPre = float(tPre)
            tPost = float(tPost)
            samplingPeriod = float(samplingPeriod)
            
            if tPre < -0.01 and tPre > -5.0 and tPost > 0.01 and tPost < 5.0 and samplingPeriod > 1.0 and samplingPeriod < 1000.0:
                self.tPre = tPre
                self.tPost = tPost
                self.samplingPeriod = samplingPeriod
                
                self.update()
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Values outside acceptable limits")
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
            if tPre < -0.01 and tPre > -5.0:
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
            if tPost > 0.01 and tPost < 5.0:
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
            if samplingPeriod > 1.0 and samplingPeriod < 1000.0:
                self.samplingPeriod = samplingPeriod
                self.rpOptions.errorLabel.setText("")
            else:
                self.rpOptions.errorLabel.setText("Value outside acceptable limits!")
        
        except:
            self.rpOptions.errorLabel.setText("Invalid input!")
    
    def create_raster_psth(self, spiketrain, trigger, timerange=[-0.15, 0.35]):
        '''
        It calculates a list of concatenates spikes around stimulus onset and offset, for a later PSTH analysis.
    
        :param spiketrain: list with spike times
        :param trigger:    list with timings of the trigger
        :param timerange:  time range for the PSTHs
    
        :return: raster_trig
        '''
    
        if len(spiketrain) < 2:
            # raise(ValueError, "The spiketrain contains fewer than 2 spikes.")
            print("The spiketrain contains fewer than 2 spikes. Returning empty list.")
            return []
    
        spiketrain = spiketrain * pq.s
    
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
            mask_trig = (spiketrain >= (t_trig + timerange[0] * pq.s)) & (spiketrain <= (t_trig + timerange[1] * pq.s))
            spikes = spiketrain[mask_trig] - t_trig
            raster_trig.append(spikes.magnitude)
    
        # convert to arrays and calculate the rate estimate
        raster_trig = np.array(raster_trig)
        # raster_trig = np.sort(raster_trig)
    
        return raster_trig
    
    def compute_psth_from_raster(self, array_raster_trig, minimum_spikes=10, timerange=[-0.15, 0.35]):
    
        out = dict()
        if len(array_raster_trig) < 1:
            print('PSTH not computed due to lack of spikes. PSTH_check is 0')
            out["values"] = np.array([])
            out["times"] = []
            return out
    
        raster_trig = np.sort(np.hstack(array_raster_trig))
        if len(raster_trig) <= minimum_spikes:
            print('PSTH not computed due to lack of spikes. PSTH_check is 0')
            out["values"] = np.array([])
            out["times"] = []
            return out
    
        rate_estimate, PSTH_times, kw = self.calc_rate_estimate(raster_trig, timerange, sampling_period=self.samplingPeriod)
        PSTH_trig = rate_estimate / float(len(array_raster_trig))
        PSTH_trig = np.array(PSTH_trig)[:, 0]
        
        out['values'] = PSTH_trig
        out['times'] = PSTH_times
        return out
    
    def calc_rate_estimate(self, spike_times, timerange, kfactor=1.0 / (1.0), sampling_period = 2.0, kw_min = 0.01):  # version=v2 => kfactor = 1.0/2.0/2.7
        """
        :param spike_times: array of spike times
        :return rate_estimate: neo object containing rate estimate and time scale
        :return kernel_width: optimized kernel width for the calculation of the rate estimate
        """
        mask = (spike_times >= timerange[0]) & (spike_times <= timerange[1])
        spiketrain = np.copy(spike_times[mask].copy())
        t_start = timerange[0]
        t_stop = timerange[1]
        if len(spiketrain) < 2:
            times = np.linspace(timerange[0], timerange[1], int(np.diff(timerange)*1000/sampling_period), endpoint=False)
            rate = np.zeros_like(times)
            kw = 0
            return rate, times, kw
    
        kernel_width = sskernel(spiketrain, tin=None, bootstrap=False)['optw']
        if kernel_width < kw_min:
            kernel_width = kw_min
        spike_train = SpikeTrain(spiketrain * pq.s, t_start=t_start * pq.s, t_stop=t_stop * pq.s)
        rate_estimate = instantaneous_rate(spike_train, sampling_period=sampling_period * pq.ms,
                                                    kernel=GaussianKernel(kfactor * kernel_width * pq.s))
        return rate_estimate.rescale('Hz').magnitude, rate_estimate.times.rescale('s').magnitude, kernel_width * pq.s
        
    def plotProfile(self, x, y, color, name, clickable = False):
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
        self._profiles.append(self.makePlot(x = x, y = y, color = color, name = name, clickable = clickable))

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
            
            event_dict = data.events
            self.events = event_dict
            
            self.populateEventList()
            
            triggerEvent = self.triggerEvent
            if layer == "session wise":
                for i in range(len(active)):
                    for j in range(len(active[i])):
                        if active[i][j]:
                            runit = vum.get_realunit(i, j, data)
                            spiketrain = data.get_data("spiketrain", runit)
                            col = vum.get_color(j, False, layer, False)
                            clickable = True
                            self.datas["{}{}".format(i, j)] = [spiketrain, col, clickable]
                
                if triggerEvent in event_dict.keys():
                    for key in self.datas.keys():
                        pos = list(key)
                        column, row = int(pos[0]), int(pos[1])
                        if active[column][row]:
                            event_times = event_dict[triggerEvent][column][0][0]
                            plotData = self.datas[key]
                            spiketrain, color, clickable = plotData
                            raster = self.create_raster_psth(spiketrain=spiketrain.rescale(pq.s).magnitude,
                                                             trigger=event_times.rescale(pq.s),
                                                             timerange=[self.tPre, self.tPost])
                            result = self.compute_psth_from_raster(array_raster_trig=raster, minimum_spikes=10, timerange=[self.tPre, self.tPost])
                            self.plotProfile(x = result['times'], y = result['values'], color = color, name = key, clickable = clickable)                    
                    self.createVerticalLine(xval = 0)
                    self.setXLabel("Time", "s")
                    self.setYLabel("Frequency", "Hz")
                    self.setPlotTitle("Rate Profiles around trigger {}".format(triggerEvent))
                    self.connectPlots()
                
            elif layer == "unit wise":
                for i in range(len(active)):
                    for j in range(len(active[i])):
                        if active[i][j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            clickable = True
                            self.datas["{}{}".format(i,j)] = [datas, col, clickable]
                            for d in datas:
                                y = histogram(d, bins = range(1, self.binMax + 1, self.binStep))
                                tmp = y[1]
                                tmp = tmp[:-1]
                                self.plotHist(x = tmp, y = y[0]/(1.0*len(d)), color = col, name = "{}{}".format(i, j), clickable = clickable)
                    
    
    def update(self):
        self.clear_()
        triggerEvent = self.triggerEvent
        event_dict = self.events
        for key in self.datas.keys():
            pos = list(key)
            column = int(pos[0])
            event_times = event_dict[triggerEvent][column][0][0]
            plotData = self.datas[key]
            spiketrain, color, clickable = plotData
            raster = self.create_raster_psth(spiketrain=spiketrain.rescale(pq.s).magnitude,
                                             trigger=event_times.rescale(pq.s),
                                             timerange=[self.tPre, self.tPost])
            result = self.compute_psth_from_raster(array_raster_trig=raster, minimum_spikes=10, timerange=[self.tPre, self.tPost])
            self.plotProfile(x = result['times'], y = result['values'], color = color, name = key, clickable = clickable)            
        self.createVerticalLine(xval = 0)
        self.setXLabel("Time", "s")
        self.setYLabel("Frequency", "Hz")
        self.setPlotTitle("Rate Profiles around trigger {}".format(triggerEvent))
        self.connectPlots()
            
    def connectPlots(self):
        for item in self._profiles:
            item.curve.setClickable(True, width = 5)
            item.sigClicked.connect(self.getItem)
    
    def clear_(self):
        self._profiles = []
        self.clearAll()
    
    def changeTriggerEvent(self, text):
        
        self.triggerEvent = text
        self.update()
    
    def populateEventList(self):
        
        eventDict = self.events
        self.rpOptions.eventDropDown.clear()
        self.rpOptions.eventDropDown.addItems([""] + sorted(eventDict.keys()))