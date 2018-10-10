"""
Created on Nov 17, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget2d
from numpy import histogram, sort, arange
from gui.isiOptions_ui import Ui_isiOptions

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
        
        layers = ["units", "sessions"]
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
            if binStep > 0 and binStep <=500:
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
        
    def plotHist(self, x, y, color, name, clickable = False):
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
        self._hists.append(self.makePlot(x = x, y = y, color = color, name = name, clickable = clickable, stepMode = self.stepMode))

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
            
            if layer == "sessions":
                values = []
                for i in range(len(active)):
                    values.append([])
                    for j in range(len(active[i])):
                        if active[i][j]:
                            runit = vum.get_realunit(i, j, data)
                            d = data.get_data(layer, runit)
                            values[i].extend(d)
                            col = vum.get_color(j, False, layer, False)
                            clickable = False
                            self.datas["{}".format(j)] = [sort(values[i]), col, clickable]
            
                if values:
                    for key in self.datas.keys():
                        y = histogram(self.datas[key][0], bins = arange(0., self.binMax/1000., self.binStep/1000.))
                        tmp = y[1]
                        if self.stepMode:
                            tmp = tmp[:]
                        else:
                            tmp = tmp[:-1]
                        self.plotHist(x = tmp, y = y[0]/(1.0*len(self.datas[key][0])), color = self.datas[key][1], name = key, clickable = self.datas[key][2])
                self.setXLabel("Inter-spike Interval", "s")
                self.setYLabel("Normalized Percentage of Interval Counts")
                self.setPlotTitle("Inter-spike Interval Histograms")
            elif layer == "units":
                for i in range(len(active)):
                    for j in range(len(active[i])):
                        if active[i][j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, False, layer, False)
                            clickable = True
                            self.datas["{}{}".format(i,j)] = [datas, col, clickable]
                            for d in datas:
                                y = histogram(d, bins = arange(0., self.binMax/1000., self.binStep/1000.))
                                tmp = y[1]
                                if self.stepMode:
                                    tmp = tmp[:]
                                else:
                                    tmp = tmp[:-1]
                                self.plotHist(x = tmp, y = y[0]/(1.0*len(d)), color = col, name = "{}{}".format(i, j), clickable = clickable)
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
            clickable = datas[2]
            for d in data:
                y = histogram(d, bins = arange(0., self.binMax/1000., self.binStep/1000.))
                tmp = y[1]
                if self.stepMode:
                    tmp = tmp[:]
                else:
                    tmp = tmp[:-1]
                self.plotHist(x = tmp, y = y[0]/(1.0*len(d)), color = col, name = key, clickable = clickable)
                self.setXLabel("Inter-spike Interval", "s")
                self.setYLabel("Normalized Percentage of Interval Counts")
                self.setPlotTitle("Inter-spike Interval Histograms")
        self.connectPlots()
            
    def connectPlots(self):
        for item in self._hists:
            item.curve.setClickable(True, width = 5)
            item.sigClicked.connect(self.getItem)
    
    def clear_(self):
        self._hists = []
        self.clearAll()
    
    def incrementBins(self, step = 1):
        self.bins+=step
        self.update()
    
    def decrementBins(self, step = 1):
        self.bins-=step
        self.update()