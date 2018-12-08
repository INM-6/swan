"""
Created on Nov 17, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.src.widgets.mypgwidget import PyQtWidget2d
import numpy as np
from swan.gui.isiOptions_ui import Ui_isiOptions


class pgWidgetISI(PyQtWidget2d):
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
        self._hists = []
        self.datas = {}

        self.binMax = 100
        self.binStep = 5
        self.stepMode = False

        self.isiOptions = Ui_isiOptions(self)

        self.showGrid()

    #### general methods ####

    def onEnter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.
        
        Redraws everything.
        
        """
        binMax = self.isiOptions.binMaxEdit.text()
        binStep = self.isiOptions.binStepEdit.text()

        try:
            binMax = int(binMax)
            binStep = float(binStep)

            if binMax > 0 and binMax <= 500 and binStep > 0 and binStep <= 500:
                self.binMax = binMax
                self.binStep = binStep

                self.update()
                self.isiOptions.errorLabel.setText("")
            else:
                self.isiOptions.errorLabel.setText("Values outside acceptable limits")
        except:
            self.isiOptions.errorLabel.setText("Invalid inputs!")

    def onMaxPlus(self):
        """
        This method is called if you click on the plus button
        for the bin max optio8n.
        
        Increments the bin max option.
        
        """
        binMax = self.binMax

        if (binMax + 1) <= 500:
            self.binMax += 1
            self.isiOptions.binMaxEdit.setText(str(self.binMax))
            self.update()

    def onMaxMinus(self):
        """
        This method is called if you click on the minus button
        for the bin max option.
        
        Decrements the bin max option.
        
        """
        binMax = self.binMax
        if (binMax - 1) > 0 and (binMax - 1) > self.binStep:
            self.binMax -= 1
            self.isiOptions.binMaxEdit.setText(str(self.binMax))
            self.update()

    def onStepPlus(self):
        """
        This method is called if you click on the plus button
        for the bin step option.
        
        Increments the bin step option.
        
        """
        binStep = self.binStep
        if (binStep + 1) <= 500:
            self.binStep += 1
            self.isiOptions.binStepEdit.setText(str(self.binStep))
            self.update()

    def onStepMinus(self):
        """
        This method is called if you click on the minus button
        for the bin step option.
        
        Decrements the bin step option.
        
        """
        binStep = self.binStep
        if (binStep - 1) > 0:
            self.binStep -= 1
            self.isiOptions.binStepEdit.setText(str(self.binStep))
            self.update()

    def binMaxChanged(self, value):
        """
        This method is called if you edit the bin max option.
        
        Checks if the bin max is correct.
        
        """
        binMax = value
        try:
            binMax = float(binMax)
            if binMax > 0 and binMax <= 500:
                self.binMax = binMax
                self.isiOptions.errorLabel.setText("")
            else:
                self.isiOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.isiOptions.errorLabel.setText("Invalid input!")

    def binStepChanged(self, value):
        """
        This method is called if you edit the bin step option.
        
        Checks if the bin step is correct.
        
        """
        binStep = value
        try:
            binStep = float(binStep)
            if binStep > 0 and binStep <= 500:
                self.binStep = binStep
                self.isiOptions.errorLabel.setText("")
            else:
                self.isiOptions.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.isiOptions.errorLabel.setText("Invalid input!")

    def stepModeChanged(self):

        currentStepMode = self.stepMode
        newStepMode = self.isiOptions.histStyleCheckbox.isChecked()

        if currentStepMode != newStepMode:
            self.stepMode = newStepMode
            self.update()

    def plotHist(self, x, y, color, unit_id, session, clickable=False):
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
        self._hists.append(self.makePlot(x=x, y=y, color=color, unit_id=unit_id, session=session, clickable=clickable,
                                         stepMode=self.stepMode))

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
                            col = vum.get_color(unit_id, False, layer, False)
                            self.datas[unit_id] = [np.sort(intervals[unit_id]), col, unit_id, session, clickable]

                if intervals:
                    for key in self.datas.keys():
                        y = np.histogram(self.datas[key][0], bins=np.arange(0., self.binMax / 1000., self.binStep / 1000.))
                        tmp = y[1]
                        if self.stepMode:
                            tmp = tmp[:]
                        else:
                            tmp = tmp[:-1]
                        self.plotHist(x=tmp, y=y[0] / (1.0 * len(self.datas[key][0])), color=self.datas[key][1],
                                      unit_id=self.datas[key][2], session=self.datas[key][3],
                                      clickable=self.datas[key][4])
                self.setXLabel("Inter-spike Interval", "s")
                self.setYLabel("Normalized Percentage of Interval Counts")
                self.setPlotTitle("Inter-spike Interval Histograms")
            elif layer == "individual":
                for session in range(len(active)):
                    for unit_id in range(len(active[session])):
                        if active[session][unit_id]:
                            runit = vum.get_realunit(session, unit_id, data)
                            datas = data.get_data("units", runit)
                            col = vum.get_color(unit_id, False, layer, False)
                            clickable = True
                            self.datas["{}{}".format(session, unit_id)] = [datas, col, unit_id, session, clickable]
                            for d in datas:
                                y = np.histogram(d, bins=np.arange(0., self.binMax / 1000., self.binStep / 1000.))
                                tmp = y[1]
                                if self.stepMode:
                                    tmp = tmp[:]
                                else:
                                    tmp = tmp[:-1]
                                self.plotHist(x=tmp, y=y[0] / (1.0 * len(d)), color=col, unit_id=unit_id,
                                              session=session, clickable=clickable)
                self.setXLabel("Inter-spike Interval", "s")
                self.setYLabel("Normalized Percentage of Interval Counts")
                self.setPlotTitle("Inter-spike Interval Histograms")
            self.connectPlots()

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
                y = np.histogram(d, bins=np.arange(0., self.binMax / 1000., self.binStep / 1000.))
                tmp = y[1]
                if self.stepMode:
                    tmp = tmp[:]
                else:
                    tmp = tmp[:-1]
                self.plotHist(x=tmp, y=y[0] / (1.0 * len(d)), color=col, unit_id=unit_id, session=session, clickable=clickable)
                self.setXLabel("Inter-spike Interval", "s")
                self.setYLabel("Normalized Percentage of Interval Counts")
                self.setPlotTitle("Inter-spike Interval Histograms")
        self.connectPlots()

    def connectPlots(self):
        for item in self._hists:
            item.curve.setClickable(True, width=5)
            item.sigClicked.connect(self.getItem)

    def clear_(self):
        self._hists = []
        self.clearAll()

    def incrementBins(self, step=1):
        self.bins += step
        self.update()

    def decrementBins(self, step=1):
        self.bins -= step
        self.update()
