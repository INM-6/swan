"""
Created on Nov 21, 2013

@author: Christoph Gollan

In this module you can find the :class:`MyPlotGrid` which is just
a :class:`PyQt5.QtGui.QScrollArea` with some additions.

More important is the :class:`MyPlotContent`.
It shows an overview of many :class:`src.myplotwidget.MyPlotWidget`
and manages them.
"""
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from gui.myplotgrid_ui import Ui_Form
from src.myplotwidget import MyPlotWidget
from src.indicatorwidget import IndicatorWidget
from numpy.random import choice
from quantities import uV, mV, V, s, ms

class MyPlotGrid(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        
        self.mainGridLayout = QtGui.QGridLayout()
        
        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        
        self.child = MyPlotContent(self)
        self.scrollArea.setWidget(self.child)
        self.mainGridLayout.addWidget(self.scrollArea, 0, 0)
        
        self.setLayout(self.mainGridLayout)
    
    def setDark(self):
        self.child.setDark()
    
class MyPlotContent(QtWidgets.QWidget):
    """
    A class that manages :class:`src.myplotwidget.MyPlotWidget` 
    objects in a grid.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QWidget`.
    
    """
    #makePlots = QtCore.pyqtSignal(int, int)
    #doPlot = QtCore.pyqtSignal("PyQt_PyObject")
    
    plotSelected = QtCore.pyqtSignal(object, bool)
    indicatorToggle = QtCore.pyqtSignal()
    visibilityToggle = QtCore.pyqtSignal(int, int, bool)

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_shape* (tuple of integer):
                The shape of the plot grid.
                Format: (rows, cols)
            *_plots* (list of :class:`src.myplotwidget.MyPlotWidget`):
                The plots in a list for iterating over them.
            *_selected* (list of :class:`MyPlotWidget`):
                A list containing the selected plots.
            *_rows* (dictionary):
                A dictionary containing the row as key and a list
                of plots as value for the plots in that row.
            *_cols* (dictionary):
                A dictionary containing the column as key and a list
                of plots as value for the plots in that column.
            *_yrange* (tuple of float):
                The y range all plots should have. 
        
        """
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        #properties{
        self._shape = None
        self._plots = []
        self._indicators = []
        self._selected = []
        self._rows = {}
        self._cols = {}
        self._yrange = (-0.001, 0.0006)
        self._xrange = (0, 0)
        self._second_select = None
        self._dark = False
        self._width = 120
        self._height = 90
        self._constDim = 60
        
        self._plotGray = QtGui.QColor(180, 180, 180, 170)
        self._plotGrayDark = QtGui.QColor(180, 180, 180, 85)
        
        self._sampleWaveformNumber = 500
        #}
        
        self.ui.gridLayout.setColumnStretch(1000, 1000)
        self.ui.gridLayout.setRowStretch(1000, 1000)
        
        #self.makePlots.connect(self.make_plots)
        #self.doPlot.connect(self.do_plot)


    #### general methods ####
        
    def make_plots(self, rows, cols, dates = None):
        """
        Creates a plot grid of the given shape.
        
        **Arguments**
        
            *rows* (integer):
                The number of rows of the grid.
            *cols* (integer):
                The number of columns of the grid.
        
        """
        self.delete_plots()
        self._shape = (rows, cols)
        self._plots = []
        self._indicators = []
        self._rows = {}
        self._cols = {}
        
        for i in range(rows+1):
            if i == 0:
                for j in range(cols + 1):
                    if j == 0:
                        iw = IndicatorWidget("Sessions (dd.mm.yy)\n\u2192\n\n\u2193 Units", i, j, width = self._width, height = self._height, const_dim = self._constDim)
                        iw.responsive = False
                        if self._dark is True:
                            iw.darkTheme()
                        self._indicators.append(iw)
                        self.ui.gridLayout.addWidget(iw, i, j, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
                    else:
                        if dates is not None:    
                            iw = IndicatorWidget(str(j) + " (" + str(dates[j-1].strftime("%d.%m.%y")) + ")", i, j, width = self._width, height = self._height, const_dim = self._constDim)
                        else:
                            iw = IndicatorWidget(str(j), i, j, width = self._width, height = self._height, const_dim = self._constDim)
                        if self._dark is True:
                            iw.darkTheme()
                        self._indicators.append(iw)
                        iw.selectIndicator.connect(self.indicatorToggled)
                        self.ui.gridLayout.addWidget(iw, i, j, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            else:
                iw = IndicatorWidget(str(i), i, 0, width = self._width, height = self._height, const_dim = self._constDim)
                if self._dark is True:
                    iw.darkTheme()
                self._indicators.append(iw)
                iw.selectIndicator.connect(self.indicatorToggled)
                self.ui.gridLayout.addWidget(iw, i, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)                
        
        for i in range(rows):
            self._rows[i] = []
            for j in range(cols):
                if j not in self._cols:
                    self._cols[j] = []
                mpw = MyPlotWidget(width = self._width, height = self._height, parent = self)
                if self._dark is True:
                    mpw.darkTheme()
                self._plots.append(mpw)
                mpw.pos = (i, j)
                mpw.selectPlot.connect(self.select_plot)
                mpw.colourStripToggle.connect(self.toggleIndicatorColour)
                mpw.visibilityToggle.connect(self.togglePlotVisibility)
                self._rows[i].append(mpw)
                self._cols[j].append(mpw)
                self.ui.gridLayout.addWidget(mpw, i+1, j+1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        return self._plots
    
    @QtCore.pyqtSlot(object, int)
    def toggleIndicatorColour(self, colour, i):
        iw = next((x for x in self._indicators if x._pos[0] == i+1))
        if any(plot.hasPlot == True for plot in self._rows[i]):
            iw.toggleColourStrip(colour)
        else:
            iw.toggleColourStrip(None)
    
    @QtCore.pyqtSlot(object)
    def indicatorToggled(self, indicator):
        row = indicator._row
        col = indicator._col
        if col == 0:
            mpwList = [pw for pw in self._plots if pw.pos[0] == row - 1]
        elif row == 0:
            mpwList = [pw for pw in self._plots if pw.pos[1] == col - 1]
        
        for pw in mpwList:
            if not indicator.selected:
                if row == 0:
                    pw.enable("col")
                    #self.indicatorToggle.emit(None, None)
                elif col == 0:
                    pw.enable("row")
            else:
                pw.disable()
                if row == 0:
                    pw.colInhibited = True
                elif col == 0:
                    pw.rowInhibited = True
        self.indicatorToggle.emit()
                    
    def togglePlotVisibility(self, i, j, visible):
        self.visibilityToggle.emit(i, j, visible)
    
    def delete_plots(self):
        """
        Deletes all plots.
        
        """
        for p in self._plots:
            p.close()
        for i in self._indicators:
            i.close()
            
    def clear_plots(self):
        """
        Clears all plots.
        
        """
        for p in self._plots:
            p.clear_()
            p.enable("all")
        for i in self._indicators:
            i.colourStrip.hide()
            if not i.selected:
                i._bg = i.bgs["selected"]
                i.setBackground(i._bg)
                i.selected = True
            
    def do_plot(self, vum, data):
        """
        Plots data on all plots.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed to get the mapping.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get the data.
        
        """
        for i in range(len(vum.mapping)):
            for j in range(len(vum.mapping[i])):
                p = self.find_plot(j, i)
                if p.toBeUpdated:
                    p.clear_()
                    col = vum.get_color(j, False, "average", False)
                    p._defPenColour = col
                    p.plotWidget.setXRange(0., data.wave_length, padding = None, update = True)
                    if vum.mapping[i][j] != 0:
                        runit = vum.get_realunit(i, j, data)
                        d = (data.get_data("average", runit) * V).rescale(mV)
                        d_all = (data.get_data('all', runit) * uV).rescale(mV)
                        p.plot_many(d_all[choice(d_all.shape[0], size = self._sampleWaveformNumber, replace = False)], self._plotGray)
                        p.plot(d, col)
                        p.hasPlot = True
                        p.toggleColourStrip(col)
                    else:
                        p.clear_()
                        p.toggleColourStrip(col)
                    p.toBeUpdated = False
    
    def setAllForUpdate(self):
        for plot in self._plots:
            plot.toBeUpdated = True
                
    def find_plot(self, i, j):
        """
        Finds a plot at a given position.
        
        **Arguments**
        
            *i* (integer):
                The row index.
            *j* (integer):
                The column index.
        
            **Returns**: :class:`src.myplotwidget.MyPlotWidget`
                The plot at position (i, j).
        
        """
        return self._rows[i][j]
    
    @QtCore.pyqtSlot(object)
    def highlightPlot(self, item):
        if item.opts['clickable']:
            name = item.opts['name']
            nameList = list(name)
            unit = int(nameList[0])
            session = int(nameList[1])
            
            p = self.find_plot(session, unit)
            self.select_plot(p, not p.selected)
            
    def select_plot(self, plot, select):
        """
        Selects or deselects a plot on the grid.
        
        If nothing is selected, the plot will be selected.
        Second selection is only allowed if the plot is in the same column 
        as the other one and if not two are already selected.
        
        **Arguments**
        
            *plot* (:class:`src.myplotwidget.MyPlotWidget`):
                The plot to (de)select.
            *select* (boolean):
                Whether or not the plot should be selected.
        
        """
        if select:
            if len(self._selected) == 1 and self._selected[0].pos[1] == plot.pos[1]:
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self._second_select = plot
                self.plotSelected.emit(plot, select)
                
            elif not self._selected:
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self._second_select = None
                self.plotSelected.emit(plot, select)
                
            elif self._second_select is not None and self._selected[0].pos[1] == plot.pos[1]:
                self._selected.remove(self._second_select)
                self._second_select.change_background(not select)
                self._second_select.selected = not select
                self.plotSelected.emit(self._second_select, not select)
                self._second_select = plot
                
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self.plotSelected.emit(plot, select)
                
        elif plot in self._selected:
            self._selected.remove(plot)
            plot.change_background(select)
            plot.selected = select
            self.plotSelected.emit(plot, select)
        
    def reset_selection(self):
        """
        Resets the selection.
        
        """
        for p in self._selected:
            p.selected = False
            p.change_background(False)
        self._selected = []
    
    def get_selection(self):
        """
            **Returns**: list of :class:`src.myplotwidget.MyPlotWidget`
                The selected plots.
        
        """
        return self._selected
    
    def zoom_in(self, step=25.0):
        """
        Zooms in the plots.
        
        **Arguments**
        
            *step* (float):
                The zoom step percentage.
                Default: 25.0 percent.
        
        """
        for plot in self._plots:
            plot.change_size(width=step, height=step)
        for indicator in self._indicators:
            indicator.change_size(width=step, height=step)
            
    def zoom_out(self, step=25.0):
        """
        Zooms out the plots.

        **Arguments**
        
            *step* (float):
                The zoom step percentage.
                Default: 25.0 percent.
        
        """
        for plot in self._plots:
            plot.change_size(width=-step, height=-step)
        for indicator in self._indicators:
            indicator.change_size(width=-step, height=-step)
            
    def expand(self, step=150):
        """
        Increases the y range of the plots.

        **Arguments**
        
            *step* (integer):
                The expand step.
                Default: 150 pixels.
        
        """
        self.set_yranges(self._yrange[0]-step, self._yrange[1]+step)
    
    def collapse(self, step=150):
        """
        Decreases the y range of the plots.
        
        **Arguments**
        
            *step* (integer):
                The collapse step.
                Default: 150 pixels.        
        
        """
        self.set_yranges(self._yrange[0]+step, self._yrange[1]-step)
        
    def set_yranges(self, min0, max0):
        """
        Sets the y ranges of all plots.
        
        **Arguments**
        
            *min0* (float):
                The minimal y.
            *max0* (float):
                The maximal y.
        
        """
        self._yrange = (min0, max0)
        for plot in self._plots:
            plot.plotWidget.setYRange(min0, max0, padding = None, update=True)
            
    def set_xranges(self, min0, max0):
        """
        Sets the y ranges of all plots.
        
        **Arguments**
        
            *min0* (float):
                The minimal y.
            *max0* (float):
                The maximal y.
        
        """
        self._xrange = (min0, max0)
        for plot in self._plots:
            plot.plotWidget.setXRange(min0, max0, padding = None, update=True)
            
    def set_tooltips(self, tooltips):
        """
        Sets tool tips for all plots.
        
        **Arguments**
        
            *tooltips* (dictionary):
                A dictionary containing for each column of the grid
                a list of string containing the tool tips for that column.
        
        """
        for col in self._cols:
            tips = tooltips[col]
            plots = self._cols[col]
            for t, plot in zip(tips, plots):
                plot.set_tooltip(t)
    
    def swap_tooltips(self, p1, p2):
        """
        Swaps the tooltips for two plots that have been swapped.
        """
        tip1 = p1.toolTip()
        tip2 = p2.toolTip()
        
        p1.set_tooltip(tip2)
        p2.set_tooltip(tip1)
        
    def setDark(self):
        self._dark = True
        self._plotGray = self._plotGrayDark