#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 23:08:03 2017

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from numpy import array
from swan.widgets.view_toolbar import ViewToolbar
from swan.widgets.gl_view_widget import MyGLwidget

pg.setConfigOptions(useOpenGL=True)


class PyQtWidget3d(QtWidgets.QWidget):
    refresh_plots = QtCore.pyqtSignal()
    sig_clicked = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, *args, **kwargs):

        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)

        layout = QtWidgets.QGridLayout()
        self.layout = layout

        self.pg_canvas = MyGLwidget()
        self.pg_canvas.setBackgroundColor('k')
        self.pg_canvas.unit_clicked.connect(self.get_item)

        self.layout.addWidget(self.pg_canvas, 0, 0)

        self.toolbar = ViewToolbar(self)
        self.layout.addWidget(self.toolbar, 1, 0)

        self.layout.setRowStretch(0, 10)

        self.setLayout(self.layout)

        self.camera_position = None
        self._axes_gl_options = 'translucent'
        self._grid_size = 3000
        self._grid_spacing = 100
        self.means = []
        self.positions = []
        self.selected_plots = []
        self.suggested_plots = []
        self.shadow_pen_colour = (0.9, 0.9, 0.9, 0.5)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)

    def setup_axes(self, size=None, spacing=None, gl_options=None, axes='xyz', set_camera=True, **kwargs):

        if size is None:
            size = self._grid_size
        if spacing is None:
            spacing = self._grid_spacing
        if gl_options is None:
            gl_options = self._axes_gl_options

        if 'x' in axes:
            x_grid = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=gl_options)
            x_grid.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            self.pg_canvas.addItem(x_grid)

        if 'y' in axes:
            y_grid = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=gl_options)
            y_grid.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            y_grid.rotate(90, 0, 1, 0)
            self.pg_canvas.addItem(y_grid)

        if 'z' in axes:
            z_grid = gl.GLGridItem(size=QtGui.QVector3D(size, size, size), glOptions=gl_options)
            z_grid.setSpacing(spacing=QtGui.QVector3D(spacing, spacing, spacing))
            z_grid.rotate(90, 1, 0, 0)
            self.pg_canvas.addItem(z_grid)

        if set_camera:
            distance = kwargs.get("distance", 2 * size)
            elevation = kwargs.get("elevation", None)
            azimuth = kwargs.get("azimuth", None)
            self.set_camera_position(distance=distance, elevation=elevation, azimuth=azimuth)

    def add_scatter_plot_item(self, plot_item=None, gl_options='translucent'):
        if plot_item is None:
            self.pg_canvas.addItem(
                MyScatterPlotItem(pos=array([0, 0, 0]), size=1, color=(0.5, 0.5, 0.5, 0.5), pxMode=True))
        else:
            plot_item.setGLOptions(gl_options)
            self.pg_canvas.addItem(plot_item)

    def add_surface_plot_item(self, surface_item):
        self.pg_canvas.addItem(surface_item)

    def create_scatter_plot_item(self, pos, size, color, unit_id=None, session=None, px_mode=True, clickable=False):
        item = MyScatterPlotItem(pos=pos, size=size, color=color, pxMode=px_mode)
        item.opts["clickable"] = clickable
        item.opts["unit_id"] = unit_id
        item.opts["session"] = session
        return item

    def create_surface_plot_item(self, x, y, z, color, shader='shaded'):
        if x is not None and y is not None:
            return gl.GLSurfacePlotItem(x=x, y=y, z=z, color=color, shader=shader)
        elif x is None and y is None:
            return gl.GLSurfacePlotItem(z=z, color=color, shader=shader)
        else:
            raise ValueError("x and y must both be None or be 1D arrays of shape (z.shape[0], z.shape[1])")

    def set_camera_position(self, distance=None, elevation=None, azimuth=None):
        self.pg_canvas.setCameraPosition(pos=None, distance=distance, elevation=elevation, azimuth=azimuth)

    def save_camera_position(self):
        distance = self.pg_canvas.opts['distance']
        elevation = self.pg_canvas.opts['elevation']
        azimuth = self.pg_canvas.opts['azimuth']

        self.camera_position = (distance, elevation, azimuth)

    def restore_camera_position(self):
        distance = self.camera_position[0]
        elevation = self.camera_position[1]
        azimuth = self.camera_position[2]

        self.set_camera_position(distance=distance, elevation=elevation, azimuth=azimuth)

    def clear_suggests(self):
        for old_suggested_plot in self.suggested_plots:
            old_suggested_plot.restore_pen()
            self.suggested_plots.remove(old_suggested_plot)

    def reset_plot(self):
        self.pg_canvas.items = []
        self.setup_axes(gl_options=self._axes_gl_options)

    def show_plot(self):
        self.pg_canvas.show()

    def trigger_refresh(self):
        self.refresh_plots.emit()

    @QtCore.pyqtSlot(object)
    def get_item(self, item):
        self.sig_clicked.emit(item)

    @QtCore.pyqtSlot(object, bool)
    def highlight_curve_from_plot(self, plot, select):
        scatter_plot_mean = next((x for x in self.means if (x.opts["session"], x.opts["unit_id"]) == plot.pos), None)
        scatter_plot_pos = next((x for x in self.positions if (x.opts["session"], x.opts["unit_id"]) == plot.pos), None)
        # suggested_plots = [x for x in self.positions if
        #                    x.opts["session"] == plot.pos[0] and x not in self.selected_plots]

        if scatter_plot_mean is not None:
            if select:
                # self.clear_suggests()
                # for suggested_plot in suggested_plots:
                #     if suggested_plot not in self.suggested_plots:
                #         suggested_plot.set_suggest_pen()
                #         self.suggested_plots.append(suggested_plot)
                if scatter_plot_mean not in self.selected_plots:
                    self.selected_plots.append(scatter_plot_mean)
                if scatter_plot_pos not in self.selected_plots:
                    self.selected_plots.append(scatter_plot_pos)
                if scatter_plot_pos in self.suggested_plots:
                    self.suggested_plots.remove(scatter_plot_pos)

                scatter_plot_mean.set_shadow_pen(self.shadow_pen_colour)
                scatter_plot_pos.set_shadow_pen(self.shadow_pen_colour)

            elif not select:
                if scatter_plot_mean in self.selected_plots:
                    scatter_plot_mean.restore_pen()
                    self.selected_plots.remove(scatter_plot_mean)
                if scatter_plot_pos in self.selected_plots:
                    scatter_plot_pos.restore_pen()
                    self.selected_plots.remove(scatter_plot_pos)
                # if not self.selected_plots:
                #     self.clear_suggests()

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 400)


class MyScatterPlotItem(gl.GLScatterPlotItem, QtWidgets.QGraphicsItem):

    def __init__(self, **kwargs):
        gl.GLScatterPlotItem.__init__(self, **kwargs)
        QtWidgets.QGraphicsItem.__init__(self)
        self.opts = {"clickable": kwargs.get("clickable", False),
                     "unit_id": None,
                     "session": None,
                     "defaultColor": self.color,
                     "defaultSize": self.size,
                     "highlightedSize": self.size + 1}

        self.highlighted = False

    def set_name(self, name):
        self.opts["name"] = name

    def set_clickable(self, choice=True):
        self.opts["clickable"] = choice

    def set_suggest_pen(self):
        self.highlighted = True
        self.setData(size=self.opts["highlightedSize"])

    def set_shadow_pen(self, color):
        self.highlighted = True
        self.setData(color=color, size=self.opts["highlightedSize"])

    def restore_pen(self, default_size=True):
        self.highlighted = False
        if default_size:
            self.setData(color=self.opts["defaultColor"], size=self.opts["defaultSize"])
        else:
            self.setData(color=self.opts["defaultColor"])


class PyQtWidget2d(QtWidgets.QWidget):
    sig_clicked = QtCore.pyqtSignal(object)
    refresh_plots = QtCore.pyqtSignal()

    def __init__(self, parent=None, *args, **kwargs):

        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)

        self.layout = QtWidgets.QGridLayout()

        self.pg_canvas = pg.PlotWidget(background='k')
        self.layout.addWidget(self.pg_canvas, 0, 0)

        self.toolbar = ViewToolbar(self)
        self.layout.addWidget(self.toolbar, 1, 0)

        self.setLayout(self.layout)

        self.layout.setRowStretch(0, 10)

        self.selected_curves = []

        self._home = None
        self._processing = False

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def show_grid(self):
        self.pg_canvas.plotItem.showGrid(x=True, y=True)

    def save_home(self):
        self._home = self.pg_canvas.saveState()

    def restore_home(self):
        self.pg_canvas.restoreState(self._home)

    def make_plot(self, *args, **kwargs):

        color = kwargs.get('color', 'w')
        width = kwargs.get('width', 2)
        style = kwargs.get('style', None)
        dash = kwargs.get('dash', None)
        cosmetic = kwargs.get('cosmetic', True)
        hsv = kwargs.get('hsv', None)
        unit_id = kwargs.get('unit_id', None)
        session = kwargs.get('session', None)
        clickable = kwargs.get('clickable', False)

        data_item = pg.PlotDataItem(pen=pg.mkPen(color=color,
                                                 width=width,
                                                 style=style,
                                                 dash=dash,
                                                 cosmetic=cosmetic,
                                                 hsv=hsv
                                                 ),
                                    *args, **kwargs)

        data_item.opts['unit_id'] = unit_id
        data_item.opts['session'] = session
        data_item.opts['clickable'] = clickable

        self.add_plot(data_item)

        return data_item

    def add_plot(self, data_item):
        self.pg_canvas.plotItem.addItem(data_item)
        self.save_home()

    def create_curve_item(self, x, y, color, name, clickable):
        return pg.PlotCurveItem(x=x, y=y, pen=pg.mkPen(color=color), name=name, clickable=clickable)

    def create_filled_curve_item(self, y1, y2, color):
        return pg.FillBetweenItem(curve1=y1, curve2=y2, brush=pg.mkBrush(color))

    def create_scatter_plot_item(self, *args, **kwargs):

        color = kwargs.get('color', 'w')
        size = kwargs.get('size', 2)
        name = kwargs.get('name', None)

        symbol = 's'
        symbol_size = size
        symbol_brush = pg.mkBrush(color=color)
        symbol_pen = pg.mkPen(color=color)

        scatter_plot_item = pg.PlotDataItem(pen=None,
                                            symbol=symbol,
                                            symbolPen=symbol_pen,
                                            symbolBrush=symbol_brush,
                                            symbolSize=symbol_size,
                                            *args, **kwargs)

        scatter_plot_item.opts['name'] = name

        self.pg_canvas.plotItem.addItem(scatter_plot_item)

        self.save_home()

        return scatter_plot_item

    def create_vertical_line(self, xval, color='w', width=2):

        pen = pg.mkPen(color=color, width=width)

        self.pg_canvas.plotItem.addLine(x=xval, pen=pen)

    def set_x_label(self, text, units=None, *args):

        self.pg_canvas.plotItem.setLabel('bottom', text=text, units=units, *args)

    def set_y_label(self, text, units=None, *args):

        self.pg_canvas.plotItem.setLabel('left', text=text, units=units, *args)

    def set_plot_title(self, text):

        self.pg_canvas.plotItem.setTitle(title=text)

    def connect_layers_to_function(self, function):
        for item in self.toolbar.layer_items:
            item.toggled.connect(function)

    @QtCore.pyqtSlot(object)
    def get_item(self, item):
        self.sig_clicked.emit(item)

    @QtCore.pyqtSlot(object, bool)
    def highlight_curve_from_plot(self, plot, select):
        plot_position = plot.pos

        curve = next((x for x in self.pg_canvas.plotItem.curves
                      if x.opts["unit_id"] == plot_position[1]
                      and x.opts["session"] == plot_position[0]
                      and x.opts["clickable"]),
                     None)

        if curve is not None:
            if select:
                curve.setShadowPen('w', width=3)
                if curve not in self.selected_curves:
                    self.selected_curves.append(curve)

            elif not select:
                curve.setShadowPen('k', width=1)
                if curve in self.selected_curves:
                    self.selected_curves.remove(curve)

    def clear_all(self):
        self.pg_canvas.plotItem.clear()
        self.selected_curves = []
        self.show_grid()

    def trigger_refresh(self):
        self.refresh_plots.emit()

    def is_processing(self):
        return self._processing

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(300, 400)
