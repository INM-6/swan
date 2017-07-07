"""
Created on Apr 28, 2014

@author: Christoph Gollan

In this module you can find the :class:`MplWidgetMovie` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is possible to slide through the waveforms of one unit either
manually by using a slider or like a movie by pressing *play*.

The movie is done by the :class:`MovieTask` and the data loading
by :class:`DataTask`. Both are threads.
"""
import time
from operator import itemgetter
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from src.matplotlibwidget import MatplotlibWidget
from src.movie_settings import MovieSettings


class DataTask(QtCore.QThread):
    """
    Loads the data for the movie widget.
    
    **Arguments**
        
            *data* (list of tuple of different objects):
                A list containing the data. The elements are tuple.
            *titles* (dictionary):
                Contains the plot titles as values.
                Keys are the session ranges.
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed for getting the data.
            *neodata* (:class:`src.neodata.NeoData`):
                Is needed for getting the data.
    
    """
    
    progress = pyqtSignal(int)
    """
    Progress signal to let the parent widget know how far 
    the loading progress is.
    
    """
    
    def __init__(self, data, titles, vum, neodata):
        """
        **Properties**
        
            *_data* (list of tuple of different objects):
                A list containing the data. The elements are tuple.
            *_titles* (dictionary):
                Contains the plot titles as values.
                Keys are the session ranges.
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed for getting the data.
            *neodata* (:class:`src.neodata.NeoData`):
                Is needed for getting the data.
        
        """
        QtCore.QThread.__init__(self)
        
        self._data = data
        self._titles = titles
        self.vum = vum
        self.neodata = neodata
        
    def run(self):
        """
        Loads the waveforms of all sessions and sorts them.
        
        """
        blockLen = len(self.neodata.blocks)
        step = int(100/blockLen)
        
        self.progress.emit(0)
        
        for i in xrange(blockLen):
            spiketrains = []
            waveforms = []
            units = []
            for j in xrange(self.vum.n_):
                if self.vum.mapping[i][j] is not None and self.vum.visible[j]:
                    runit = self.vum.get_realunit(i, j, self.neodata)
                    spiketrain = list(self.neodata.get_data("spiketrain", runit))[0]
                    waveform = list(self.neodata.get_data("all", runit))
                    unit = [j for k in xrange(len(spiketrain))]
                    spiketrains.extend(spiketrain)
                    waveforms.extend(waveform)
                    units.extend(unit)
            if len(spiketrains) > 0:
                #sorting the data of one session
                s, w, u = [list(x) for x in zip(*sorted(zip(spiketrains, waveforms, units), key=itemgetter(0)))]
                l1 = len(self._data)
                self._data.extend(zip(s, w, u))
                l2 = len(self._data)
                self._titles[(l1, l2)] = str((i+1))
                
                #emits a signal with the current progress
                self.progress.emit((i+1) * step)


class MovieTask(QtCore.QThread):
    """
    Shows the waveforms as movie.
    
    **Arguments**
    
            *current* (integer):
                The current slide position.
            *maxslide* (integer):
                The maximum slide number.
            *slide_method* (function):
                The function that should be call to slide.
            *abort* (boolean):
                Whether or not the movie should be aborted.
            *step* (integer):
                How many times per second the slide
                method should be called.
            *skip* (integer):
                How many slides should be skipped till the next step.
                
    """
    
    def __init__(self, current, maxslide, slide_method, step, skip):
        """
        **Properties**
        
            *current* (integer):
                The current slide position.
            *maxslide* (integer):
                The maximum slide number.
            *slide_method* (function):
                The function that should be call to slide.
            *abort* (boolean):
                Whether or not the movie should be aborted.
            *step* (integer):
                How many times per second the slide
                method should be called.
            *period* (float):
                How long the thread should wait until calling the 
                slide method again.
            *skip* (integer):
                How many slides should be skipped till the next step.
        
        """
        QtCore.QThread.__init__(self)
        
        self.current = current
        self.maxslide = maxslide
        self.slide = slide_method
        self.abort = False
        self.step = step
        self.period = 1.0/self.step
        self.skip = skip
        
    def run(self):
        """
        Slides several times per minute until the maxslide is reached
        or the task is aborted.
        
        """
        start = time.time()
        while (self.current)<= self.maxslide and not self.abort:
            self.slide(self.current)
            self.current += (1 + self.skip)
            QtGui.QApplication.processEvents()
            time.sleep(self.period - ((time.time() - start) % self.period))


class MplWidgetMovie(MatplotlibWidget):
    """
    A class to show 2d plot data extended with a slider and a *play* button.
    
    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.
    
    """
    
    progressBar = pyqtSignal(bool)
    """
    Progress signal to let the parent widget know that a
    progress bar should be shown or hidden.
    
    """
    
    progress = pyqtSignal(int)
    """
    Progress signal to let the parent widget know how far 
    the loading progress is.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The plot.
            *_data* (list of tuple of different objects):
                A list containing the data. The elements are tuple.
            *_current* (integer):
                The current slide position.
            *_movietask* (:class:`MovieTask`):
                The movie thread or None.
            *_datatask* (:class:`DataTask`):
                The data thread or None.
            *_titles* (dictionary):
                A dictionary containing the titles for the plot.
            *shouldLoad* (boolean):
                Whether or not data should be loaded.
            *isLoading* (boolean):
                Whether or not data is currently loading.
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed for getting the data.
            *neodata* (:class:`src.neodata.NeoData`):
                Is needed for getting the data.
            *_settings* (dictionary):
                Contains parameters which change the view.
            *_ylims* (tuple of integer):
                The y-Axes range.
        
        """
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._axes = None
        self._data = None
        self._current = 0
        self._movietask = None
        self._datatask = None
        self._titles = {}
        self.shouldLoad = False
        self.isLoading = False
        self.vum = None
        self.neodata = None
        
        self._settings = {"avRange":0,
                          "skip":0,
                          "sps":1,
                          "time":"original"}
        self._ylims = (-150, 150)
        #}
        
        self.setup((1, 1), False)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.playBtn = QtGui.QPushButton("play", self)
        self.loadBtn = QtGui.QPushButton("off", self)
        self.settingsBtn = QtGui.QPushButton("settings", self)
        w = QtGui.QWidget()
        
        self.vgl.addWidget(self.slider, 2, 0, 1, 1)
        self.vgl.addWidget(self.playBtn, 2, 1, 1, 1)
        self.vgl.addWidget(w, 0, 1, 1, 1)
        
        self.vl = QtGui.QVBoxLayout(w)
        self.vl.addWidget(self.settingsBtn)
        self.vl.addWidget(self.loadBtn)
        
        self.slider.valueChanged.connect(self.slide)
        self._axes = self.get_axes()[0]
        self.playBtn.clicked.connect(self.onPlay)
        self.settingsBtn.clicked.connect(self.onSettings)
        self.loadBtn.clicked.connect(self.onLoad)
        
        self.slider.setRange(0, 0)
        self.dia = None
        
        self.clear_and_reset_axes()
        
    
    #### general methods ####    

    def _load_data(self):
        """
        Starts a thread which loads the data.
        
            **Returns**: integer
                The number of data entries.
        
        """
        self._data = []
        self._titles = {}
        
        #show a progress bar
        self.progressBar.emit(True)
        
        task = DataTask(self._data, self._titles, self.vum, self.neodata)
        self._datatask = task
        self._datatask.progress.connect(self.setProgress)
        task.start()
        
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        while task.isRunning():
            self.isLoading = True
            QtGui.QApplication.processEvents()
        self.isLoading = False
        #hide the progress bar
        self.progressBar.emit(False)
        QtGui.QApplication.restoreOverrideCursor()
        
        return len(self._data)

    def set_data(self, vum, data):
        """
        Setter for the *vum* and *neodata* properties.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                To set the *vum* property.
            *data* (:class:`src.neodata.NeoData`):
                To set the *neodata* property.
        
        """
        self.vum = vum
        self.neodata = data

    def reset(self):
        """
        Resets the widget.
        
        """
        if self._movietask is not None:
            self._movietask.abort = True
        self.clear_and_reset_axes()
        self.draw()
        self._data = None
        self._titles = {}
        self.slider.setRange(0, 0)
        self.loadBtn.setText("off")

    def plot(self, y, color, ls='-', title=""):
        """
        Plots data on the plot.
        
        **Arguments**
        
            *y* (iterable object):
                The y data.
            *color* (mpl color):
                The color of the plot line.
            *ls* (string):
                The line style.
                Default: -
            *title* (string):
                The plot title.
                Default: Empty
        
        """
        self._axes.plot(y, ls, color=color)
        self._axes.set_title(title)

    def do_plot(self):
        """
        Loads the data and plots it or resets the plot.
        
        """
        vum = self.vum
        data = self.neodata
        if self.shouldLoad and vum is not None and data is not None:
            l = self._load_data()
            self.slider.setRange(0, l-1)
            self.slide(self.slider.value())
        else:
            self.reset()
            
    def clear_and_reset_axes(self):
        """
        Clears the plot axes.
        
        """
        self._axes.cla()
        self._axes.set_ylim(*self._ylims)

    def _get_data(self, i):
        """
        Getter for plot data.
        
        **Arguments**

            *i* (integer):
                Index for the data.
            **Returns**: tuple of different objects
                Contains the y data, the color and other y data.
        
        """
        if self._data is not None:
            data = self._data[i]
            datas = []
            found = []
            if i < len(self._data):
                for d in self._data[i:]:
                    if d[2] != data[2] and d[2] not in found:
                        y2 = d[1]
                        color2 = self.vum.get_color(d[2], mpl=True)
                        datas.append((y2, color2))
                        found.append(d[2])
            y = data[1]
            color = self.vum.get_color(data[2], mpl=True)
            return (y, color, datas)
        else:
            return ([], 'w', [])
    
    def _get_time(self, i):
        """
        Getter for the spike time.
        
        **Arguments**

            *i* (integer):
                Index for the data.
            **Returns**: string
                The spike time.
        
        """
        if self._data is not None:
            t = self._data[i][0]
            if not self._settings["time"] == "original":
                t.units = self._settings["time"]
            return str(t)
        else:
            return ""
    
    def set_range(self, min0, max0):
        """
        Setter for the y range.
        
        **Arguments**
        
            *min0* (integer):
                The minimal value.
            *max0* (integer):
                The maximal value.
        
        """
        self._ylims = (min0, max0)
    

    #### signal handler ####

    def slide(self, i):
        """
        Slides to the given position.
        
        **Arguments**
        
            *i* (integer):
                Current slide position.
        
        """
        self._current = i
        self.slider.setValue(i)
        #try:
        title = ""
        self.clear_and_reset_axes()
        for k in self._titles:
            if i >= k[0] and i < k[1]:
                title = self._titles[k]
        t = self._get_time(i)
        title = "Session: {} | Time: {}".format(title, t)
        
        avRange = self._settings["avRange"]
        
        (y, color, datas) = self._get_data(i)
        ys = [y]
        k = 1
        r1 = avRange
        r2 = avRange
        
        while r1 > 0 or r2 > 0:
            if (i - k) >= 0:
                (y1, color1, tmp) = self._get_data(i - k)
                if color == color1:
                    ys.append(y1)
                    r1 -= 1
            else:
                r1 = 0
            if (i + k) <= self.slider.maximum():
                (y2, color2, tmp) = self._get_data(i + k)
                if color == color2:
                    ys.append(y2)
                    r2 -= 1
            else:
                r2 = 0
            k += 1
        
        try:
            y = np.average(ys, axis=0)
        except ZeroDivisionError:
            y = []
        self.plot(y, color, title=title)
        
        for d in datas:
            y = d[0]
            color = d[1]
            k = 1
            r1 = avRange
            r2 = avRange
            ys = [y]
            
            while r1 > 0 or r2 > 0:
                if (i - k) >= 0:
                    (y1, color1, tmp) = self._get_data(i - k)
                    if color == color1:
                        ys.append(y1)
                        r1 -= 1
                else:
                    r1 = 0
                if (i + k) <= self.slider.maximum():
                    (y2, color2, tmp) = self._get_data(i + k)
                    if color == color2:
                        ys.append(y2)
                        r2 -= 1
                else:
                    r2 = 0
                k += 1
            
            try:
                y = np.average(ys, axis=0)
            except ZeroDivisionError:
                y = []
            self.plot(y, color, '--', title=title)
            
        self.draw()
        #except IndexError:
        #    pass
        
    def onPlay(self):
        """
        This method is called if you click on *play*.
        
        Starts or pauses the movie.
        
        """
        if str(self.playBtn.text()) == "pause":
            self.playBtn.setText("play")
            self._movietask.abort = True
            self.slider.blockSignals(False)
        else:
            self.playBtn.setText("pause")
            self.slider.blockSignals(True)
            self._movietask = MovieTask(self._current, self.slider.maximum(), self.slide, self._settings["sps"], self._settings["skip"])
            self._movietask.finished.connect(self.taskFinished)
            self._movietask.start()
            
    def onLoad(self):
        """
        This method is called if you click on *on* or *off*.
        
        Loads or deletes the movie data.
        
        """
        if str(self.loadBtn.text()) == "off":
            self.shouldLoad = True
            self.loadBtn.setText("on")
        else:
            if self._movietask is not None:
                self._movietask.abort = True
            if self._datatask is not None and self._datatask.isRunning():
                return
            self.shouldLoad = False
            self.loadBtn.setText("off")
        self.do_plot()
        
    def onSettings(self):
        """
        This method is called if you click on *settings*.
        
        Shows the :class:`src.movie_settings.MovieSettings`.
        
        """
        if self.dia is None:
            self.dia = MovieSettings(self._settings)
        self.dia.show()
    
    def taskFinished(self):
        """
        Is called after this task is finished to clean up.
        
        """
        self.playBtn.setText("play")
        self.slider.blockSignals(False)
        
    def setProgress(self, i):
        """
        Emits a signal to the parent widget (the main program) 
        containing the loading progress.
        
        **Arguments**
        
            *i* (integer):
                The loading progress.
        
        """
        self.progress.emit(i)
        
        
        
