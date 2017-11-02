"""
Created on Nov 21, 2013

@author: Christoph Gollan

In this module you can find the :class:`MyPlotGrid` which is just
a :class:`PyQt5.QtGui.QScrollArea` with some additions.

More important is the :class:`MyPlotContent`.
It shows an overview of many :class:`src.myplotwidget.MyPlotWidget`
and manages them.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.myplotgrid_ui import Ui_Form
from src.myplotwidget import MyPlotWidget


class MyPlotGrid(QtGui.QScrollArea):
    """
    A :class:`PyQt5.QtGui.QScrollArea` which is extended to be better 
    usable with the :class:`MyPlotContent`.

    The *args* and *kwargs* are passed to :class:`PyQt5.QtGui.QScrollArea`.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *child* (:class:`MyPlotContent`):
                Used for an easier access to it's child widget.
        
        """
        QtGui.QScrollArea.__init__(self, *args, **kwargs)
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        
        m = MyPlotContent(self)
        self.setWidget(m)
        
        #properties{
        self.child = m
        #}

        
class MyPlotContent(QtWidgets.QWidget):
    """
    A class that manages :class:`src.myplotwidget.MyPlotWidget` 
    objects in a grid.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QWidget`.
    
    """
    #makePlots = QtCore.pyqtSignal(int, int)
    #doPlot = QtCore.pyqtSignal("PyQt_PyObject")

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
        self._selected = []
        self._rows = {}
        self._cols = {}
        self._yrange = (0, 0)
        self._second_select = None
        #}
        
        self.ui.gridLayout.setColumnStretch(1000, 1000)
        self.ui.gridLayout.setRowStretch(1000, 1000)
        
        #self.makePlots.connect(self.make_plots)
        #self.doPlot.connect(self.do_plot)


    #### general methods ####
        
    def make_plots(self, rows, cols):
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
        self._rows = {}
        self._cols = {}
        for i in range(rows):
            self._rows[i] = []
            for j in range(cols):
                if j not in self._cols:
                    self._cols[j] = []
                mpw = MyPlotWidget(self)
                self._plots.append(mpw)
                mpw.pos = (i, j)
                mpw.selectPlot.connect(self.select_plot)
                self._rows[i].append(mpw)
                self._cols[j].append(mpw)
                self.ui.gridLayout.addWidget(mpw, i, j, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        return self._plots
    
    def delete_plots(self):
        """
        Deletes all plots.
        
        """
        for p in self._plots:
            p.close()
            
    def clear_plots(self):
        """
        Clears all plots.
        
        """
        for p in self._plots:
            p.clear_()
            
    def do_plot(self, vum, data):
        """
        Plots data on all plots.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed to get the mapping.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get the data.
        
        """
        self.clear_plots()
        for i in range(len(vum.mapping)):
            #print(vum.mapping[i])
            for j in range(len(vum.mapping[i])):
                if vum.mapping[i][j] != 0:
                    p = self.find_plot(j, i)
                    runit = vum.get_realunit(i, j, data)
                    #print("Executing this at {}, {}".format(i, j))
                    d = data.get_data("average", runit)
                    col = vum.get_color(j)
                    p.plot(d, col)
    
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
                
            elif not self._selected:
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self._second_select = None
                
            elif self._second_select is not None and self._selected[0].pos[1] == plot.pos[1]:
                self._selected.remove(self._second_select)
                self._second_select.change_background(not select)
                self._second_select.selected = not select
                self._second_select = plot
                
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                
        elif plot in self._selected:
            self._selected.remove(plot)
            plot.change_background(select)
            plot.selected = select
        
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
            
    def zoom_out(self, step=24):
        """
        Zooms out the plots.

        **Arguments**
        
            *step* (float):
                The zoom step percentage.
                Default: 25.0 percent.
        
        """
        for plot in self._plots:
            plot.change_size(width=-step, height=-step)
            
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
            plot.setYRange(min0, max0, padding = None, update=True)
            
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





