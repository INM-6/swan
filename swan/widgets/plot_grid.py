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
from swan.widgets.plot_widget import MyPlotWidget
from swan.widgets.indicator_cell import IndicatorWidget
from numpy.random import choice


class MyPlotGrid(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.main_grid_layout = QtWidgets.QGridLayout()

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.child = MyPlotContent(self)
        self.scroll_area.setWidget(self.child)
        self.main_grid_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_grid_layout)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(600, 400)


class MyPlotContent(QtWidgets.QWidget):
    """
    A class that manages :class:`src.myplotwidget.MyPlotWidget` 
    objects in a grid.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QWidget`.
    
    """

    plot_selected = QtCore.pyqtSignal(object, bool)
    indicator_toggle = QtCore.pyqtSignal()
    visibility_toggle = QtCore.pyqtSignal(int, int, bool)

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
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.grid_layout = QtWidgets.QGridLayout(self)

        self._shape = None
        self._plots = []
        self._indicators = []
        self._selected = []
        self._rows = {}
        self._cols = {}
        self._yrange = (-0.001, 0.0006)
        self._xrange = (0, 0)
        self._second_select = None
        self._width = 60
        self._height = 45
        self._constant_dimension = 75

        self._plot_gray = QtGui.QColor(180, 180, 180, 85)

        self.sample_waveform_number = 500

        self.grid_layout.setColumnStretch(1000, 1000)
        self.grid_layout.setRowStretch(1000, 1000)

        self.grid_layout.setHorizontalSpacing(1)
        self.grid_layout.setVerticalSpacing(1)

    def make_plots(self, rows, cols, dates=None):
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

        pivot_indicator = IndicatorWidget("Sessions (dd.mm.yy)\n\u2192\n\n\u2193 Units",
                                          indicator_type='pivot', position=None,
                                          width=self._width, height=self._height,
                                          const_dim=self._constant_dimension)
        pivot_indicator.responsive = False
        self.grid_layout.addWidget(pivot_indicator, 0, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        for global_unit_id in range(rows):
            iw = IndicatorWidget(
                str(global_unit_id + 1), indicator_type='unit', position=global_unit_id,
                width=self._width, height=self._height, const_dim=self._constant_dimension
            )
            self._indicators.append(iw)
            iw.select_indicator.connect(self.indicator_toggled)
            self.grid_layout.addWidget(iw, global_unit_id + 1, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        for session_id in range(cols):
            if dates is not None:
                iw = IndicatorWidget(
                    str(session_id + 1) + " (" + str(dates[session_id].strftime("%d.%m.%y")) + ")",
                    indicator_type='session', position=session_id,
                    width=self._width, height=self._height, const_dim=self._constant_dimension
                )
            else:
                iw = IndicatorWidget(
                    str(session_id), indicator_type='session', position=session_id,
                    width=self._width, height=self._height, const_dim=self._constant_dimension
                )
            self._indicators.append(iw)
            iw.select_indicator.connect(self.indicator_toggled)
            self.grid_layout.addWidget(iw, 0, session_id + 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        for unit_id in range(rows):
            self._rows[unit_id] = []
            for session_id in range(cols):
                if session_id not in self._cols:
                    self._cols[session_id] = []
                plot_widget = MyPlotWidget(width=self._width, height=self._height)
                self._plots.append(plot_widget)

                plot_widget.pos = (session_id, unit_id)

                self._rows[unit_id].append(plot_widget)
                self._cols[session_id].append(plot_widget)

                plot_widget.select_plot.connect(self.select_plot)
                plot_widget.colour_strip_toggle.connect(self.toggle_indicator_colour)
                plot_widget.visibility_toggle.connect(self.toggle_plot_visibility)

                self.grid_layout.addWidget(plot_widget, unit_id + 1, session_id + 1,
                                           QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        return self._plots

    @QtCore.pyqtSlot(object, int)
    def toggle_indicator_colour(self, colour, i):
        iw = next((x for x in self._indicators if x.row == i))
        if any(plot.has_plot for plot in self._rows[i]):
            iw.toggle_colour_strip(colour)
        else:
            iw.toggle_colour_strip(None)

    @QtCore.pyqtSlot(object)
    def indicator_toggled(self, indicator):
        row = indicator.row
        col = indicator.col
        indicator_type = indicator.indicator_type
        if indicator_type == 'unit':
            plot_widgets = [pw for pw in self._plots if pw.pos[1] == row]
        elif indicator_type == 'session':
            plot_widgets = [pw for pw in self._plots if pw.pos[0] == col]
        else:
            plot_widgets = []

        for pw in plot_widgets:
            if not indicator.selected:
                if indicator_type == 'session':
                    pw.enable("col")
                elif indicator_type == 'unit':
                    pw.enable("row")
            else:
                pw.disable()
                if indicator_type == 'session':
                    pw.inhibited_by_col = True
                elif indicator_type == 'unit':
                    pw.inhibited_by_row = True
        self.indicator_toggle.emit()

    def toggle_plot_visibility(self, session_id, unit_id, visible):
        self.visibility_toggle.emit(session_id, unit_id, visible)

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
                i.set_background(i._bg)
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
        active = vum.get_active()
        for session in range(len(active)):
            for global_unit_id in range(len(active[session])):
                plot_widget = self.find_plot(global_unit_id, session)
                if plot_widget.to_be_updated:
                    plot_widget.clear_()
                    pen_colour = vum.get_colour(global_unit_id)
                    plot_widget.default_pen_colour = pen_colour
                    if active[session][global_unit_id]:
                        unit = vum.get_realunit(session, global_unit_id, data)
                        mean_waveform = data.get_data("average", unit)
                        # all_waveforms = data.get_data("all", unit)
                        # try:
                        #     plot_widget.plot_many(all_waveforms[choice(all_waveforms.shape[0],
                        #                                                size=self.sample_waveform_number,
                        #                                                replace=False)],
                        #                           self._plot_gray)
                        # except ValueError:
                        #     plot_widget.plot_many(all_waveforms, self._plot_gray)
                        plot_widget.plot(mean_waveform.magnitude, pen_colour)
                        plot_widget.hasPlot = True
                        plot_widget.toggle_colour_strip(pen_colour)
                        plot_widget.plot_widget.setXRange(0., data.get_wave_length(), padding=None, update=True)
                    else:
                        plot_widget.toggle_colour_strip(pen_colour)
                    plot_widget.to_be_updated = False

    def set_all_for_update(self):
        for plot in self._plots:
            plot.to_be_updated = True

    def find_plot(self, global_unit_id, session_id):
        """
        Finds a plot at a given position.
        
        **Arguments**
        
            *global_unit_id* (integer):
                The row index.
            *session_id* (integer):
                The column index.
        
            **Returns**: :class:`src.myplotwidget.MyPlotWidget`
                The plot at position (global_unit_id, session_id).
        
        """
        return self._rows[global_unit_id][session_id]

    @QtCore.pyqtSlot(object)
    def highlight_plot(self, item):
        if item.opts['clickable']:
            unit_id = item.opts['unit_id']
            session = item.opts['session']

            p = self.find_plot(unit_id, session)
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
            if len(self._selected) == 1 and self._selected[0].pos[0] == plot.pos[0]:
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self._second_select = plot
                self.plot_selected.emit(plot, select)

            elif not self._selected:
                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self._second_select = None
                self.plot_selected.emit(plot, select)

            elif self._second_select is not None and self._selected[0].pos[0] == plot.pos[0]:
                self._selected.remove(self._second_select)
                self._second_select.change_background(not select)
                self._second_select.selected = not select
                self.plot_selected.emit(self._second_select, not select)
                self._second_select = plot

                self._selected.append(plot)
                plot.change_background(select)
                plot.selected = select
                self.plot_selected.emit(plot, select)

        elif plot in self._selected:
            self._selected.remove(plot)
            plot.change_background(select)
            plot.selected = select
            self.plot_selected.emit(plot, select)

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
        self.set_yranges(self._yrange[0] - step, self._yrange[1] + step)

    def collapse(self, step=150):
        """
        Decreases the y range of the plots.
        
        **Arguments**
        
            *step* (integer):
                The collapse step.
                Default: 150 pixels.        
        
        """
        self.set_yranges(self._yrange[0] + step, self._yrange[1] - step)

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
            plot.plot_widget.setYRange(min0, max0, padding=None, update=True)

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
            plot.plot_widget.setXRange(min0, max0, padding=None, update=True)

    def set_tooltips(self, tooltips):
        """
        Sets tool tips for all plots.
        
        **Arguments**
        
            *tooltips* (dictionary):
                A dictionary containing for each column of the grid
                a list of string containing the tool tips for that column.
        
        """
        for col in self._cols.keys():
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
