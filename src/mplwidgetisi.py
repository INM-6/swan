"""
Created on Oct 8, 2014

@author: Christoph Gollan

In this module you can find the :class:`MplWidgetIsi` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 2d plot and the plotting methods.
"""
import numpy as np
from PyQt5 import QtGui, QtCore
from src.matplotlibwidget import MatplotlibWidget


class MplWidgetIsi(MatplotlibWidget):
    """
    A class with one plot to show inter-spike-interval plots.
    
    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.
    
    Bin options:

    ====================  ====================  ====================
    Options name          Dictionary key        Valid value(s)
    ====================  ====================  ====================
    bin max               binMax                1 - 500 (> bin step)
    bin step              binStep               1 - 10
    ====================  ====================  ====================
    
    """
    
    redraw = QtCore.pyqtSignal()
    """
    Plot signal to let the parent widget know
    that it should redraw everything.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
            *_kwargs* (dictionary):
                Plot parameters given as (key, value) pares.  
            *_settings* (dictionary):
                Settings for the plot given as (key, value) pares.
        
        """
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._axes = None
        self._kwargs = {"set_xlabel":"time",
                        "set_ylabel":"fraction of spikes"}
        self._settings = {"binMax":100,
                          "binStep":1}
        #}
        self.setup(naviBar=True)
        
        #setting up the bin options GUI
        self.group = QtGui.QGroupBox("Bin options", self)
        self.group.setMinimumWidth(100)
        self.ggl = QtGui.QGridLayout(self.group)
        w = QtGui.QWidget()
        y = QtGui.QWidget()
        l1 = QtGui.QLabel("bin max:")
        l2 = QtGui.QLabel("bin step:")
        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
        self.ghl1 = QtGui.QHBoxLayout(w)
        self.ghl2 = QtGui.QHBoxLayout(y)
        
        self.binMaxPlusBtn = QtGui.QPushButton("+")
        self.binMaxEdit = QtGui.QLineEdit()
        self.binMaxMinusBtn = QtGui.QPushButton("-")
        self.binStepPlusBtn = QtGui.QPushButton("+")
        self.binStepEdit = QtGui.QLineEdit()
        self.binStepMinusBtn = QtGui.QPushButton("-")
        
        self.ghl1.addWidget(self.binMaxMinusBtn)
        self.ghl1.addWidget(self.binMaxEdit)
        self.ghl1.addWidget(self.binMaxPlusBtn)
        self.ghl2.addWidget(self.binStepMinusBtn)       
        self.ghl2.addWidget(self.binStepEdit)
        self.ghl2.addWidget(self.binStepPlusBtn)        
        
        self.ggl.addWidget(l1)
        self.ggl.addWidget(w)
        self.ggl.addWidget(l2)
        self.ggl.addWidget(y)
        self.ggl.addWidget(self.errorLabel)
        
        #adding the bin options group box to the widget
        self.vgl.addWidget(self.group, 0, 1, 1, 1)
        
        #connect the plus and minus buttons
        self.binMaxPlusBtn.clicked.connect(self.onMaxPlus)
        self.binMaxMinusBtn.clicked.connect(self.onMaxMinus)
        self.binStepPlusBtn.clicked.connect(self.onStepPlus)
        self.binStepMinusBtn.clicked.connect(self.onStepMinus)
        #connect the line edits
        self.binMaxEdit.textChanged.connect(self.binMaxChanged)
        self.binStepEdit.textChanged.connect(self.binStepChanged)
        self.binMaxEdit.returnPressed.connect(self.onEnter)
        self.binStepEdit.returnPressed.connect(self.onEnter)
        
        self._axes = self.get_axes()[0]
        self.clear_and_reset_axes(**self._kwargs)
        self.init_settings()

    
    #### signal handler ####
    
    def onEnter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.
        
        Redraws everything.
        
        """
        if not self.errorLabel.text():
            self.redraw.emit()

    def onMaxPlus(self):
        """
        This method is called if you click on the plus button
        for the bin max option.
        
        Increments the bin max option.
        
        """
        binMax = self._settings["binMax"]
        if (binMax + 1) <= 500:
            self._settings["binMax"] += 1
            self.binMaxEdit.setText(str(self._settings["binMax"]))
            self.redraw.emit()
        
    def onMaxMinus(self):
        """
        This method is called if you click on the minus button
        for the bin max option.
        
        Decrements the bin max option.
        
        """
        binMax = self._settings["binMax"]
        if (binMax - 1) > 0 and (binMax - 1) > self._settings["binStep"]:
            self._settings["binMax"] -= 1
            self.binMaxEdit.setText(str(self._settings["binMax"]))
            self.redraw.emit()
            
    def onStepPlus(self):
        """
        This method is called if you click on the plus button
        for the bin step option.
        
        Increments the bin step option.
        
        """
        binStep = self._settings["binStep"]
        if (binStep + 1) <= 10:
            self._settings["binStep"] += 1
            self.binStepEdit.setText(str(self._settings["binStep"]))
            self.redraw.emit()
            
    def onStepMinus(self):
        """
        This method is called if you click on the minus button
        for the bin step option.
        
        Decrements the bin step option.
        
        """
        binStep = self._settings["binStep"]
        if (binStep - 1) > 0:
            self._settings["binStep"] -= 1
            self.binStepEdit.setText(str(self._settings["binStep"]))
            self.redraw.emit()
                
    def binMaxChanged(self, value):
        """
        This method is called if you edit the bin max option.
        
        Checks if the bin max is correct.
        
        """
        setbak = self._settings.copy()
        self._settings["binMax"] = str(value)
        if self.checkSettings():
            self._settings["binMax"] = int(self._settings["binMax"])
        else:
            self._settings = setbak
    
    def binStepChanged(self, value):
        """
        This method is called if you edit the bin step option.
        
        Checks if the bin step is correct.
        
        """
        setbak = self._settings.copy()
        self._settings["binStep"] = str(value)
        if self.checkSettings():
            self._settings["binStep"] = int(self._settings["binStep"])
        else:
            self._settings = setbak
    

    #### general methods ####
    
    def plot(self, y, color):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *y* (tuple of iterable objects):
                The data that should be plotted.
            *color* (tuple of integer):
                The color of the line.
        
        """
        self._axes.plot(y[0], y[1], linewidth = 1, color=color)
        
    def do_plot(self, vum, data, layers):
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
        self.clear_and_reset_axes(**self._kwargs)
        for layer in layers:
            if layer == "sessions":
                for j in range(vum.n_):
                    values = []
                    for i in range(len(data.blocks)):
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, True, layer)
                            for d in datas:
                                values.extend(d)
                    if values:
                        y = np.histogram(values, bins=range(1, self._settings["binMax"] + 1, self._settings["binStep"]))
                        tmp = y[1]
                        tmp = tmp[:len(tmp)-1]
                        self.plot((tmp, y[0]/(1.0*len(values))), col)
            else:
                for i in range(len(data.blocks)):
                    for j in range(vum.n_):
                        if vum.mapping[i][j] != 0 and vum.visible[j]:
                            runit = vum.get_realunit(i, j, data)
                            datas = data.get_data(layer, runit)
                            col = vum.get_color(j, True, layer)
                            for d in datas:
                                y = np.histogram(d, bins=range(1, self._settings["binMax"] + 1, self._settings["binStep"]))
                                tmp = y[1]
                                tmp = tmp[:len(tmp)-1]
                                self.plot((tmp, y[0]/(1.0*len(d))), col)
        self.draw()
        
    def init_settings(self):
        """
        Initializes the settings.
        
        """
        self.binMaxEdit.setText(str(self._settings["binMax"]))
        self.binStepEdit.setText(str(self._settings["binStep"]))

    def checkSettings(self):
        """
        Checks the settings for correctness.
        
            **Returns**: boolean
                Whether or not everything is correct.
        
        """
        try:
            binMax = int(self._settings["binMax"])
            binStep = int(self._settings["binStep"])
        except:
            self.errorLabel.setText("Wrong input")
            return False
        if binStep < 1 or binStep > 10:
            self.errorLabel.setText("Wrong input")
            return False
        else:
            self.errorLabel.setText("")
        if binMax <= binStep or binMax > 500:
            self.errorLabel.setText("Wrong input")
            return False
        else:
            self.errorLabel.setText("")
        return True
        
        