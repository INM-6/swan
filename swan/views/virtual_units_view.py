"""
Created on Mar 10, 2015

@author: Christoph Gollan

In this module you can find the :class:`VUnits` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 2d plot and the plotting methods.
"""
import math
import numpy as np
import pyqtgraph as pg
from swan.gui.palettes import UNIT_COLORS
from PyQt5 import QtCore, QtWidgets, QtGui

from swan.widgets.mypgwidget import PyQtWidget2d


class VirtualUnitsView(QtWidgets.QWidget):
    """
    A class for showing a virtual unit overview.

    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.

    """

    redraw = QtCore.pyqtSignal()
    """
    Plot signal to let the parent widget know
    that it should redraw everything.

    """

    load = QtCore.pyqtSignal(int)
    """
    Load signal to let the parent widget know
    that it should load a channel.

    """

    def __init__(self, *args, **kwargs):
        super(VirtualUnitsView, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self.pg_canvas = pg.PlotWidget()
        self.options = QtWidgets.QWidget()

        self.data_mapping = {}

        layout.addWidget(self.pg_canvas, 9)
        layout.addWidget(self.options, 1)

        self.setLayout(layout)

    def do_plot(self, vum_all, data):
        self.pg_canvas.clear()
        channels = [name[3:] for name in vum_all.keys() if "vum" in name]
        num_processed_channels = len(channels)

        self.data_mapping = {}

        if num_processed_channels > 0:
            all_mappings = []
            channel_stops = []
            for channel in channels:
                channel_mapping = vum_all[f"vum{channel}"]
                global_unit_ids = sorted([key for key in channel_mapping.keys() if isinstance(key, int)])
                global_unit_counter = 0
                for global_id in global_unit_ids:
                    global_units_by_session = channel_mapping[global_id]
                    real_unit_pos = [element[1] for element in global_units_by_session]
                    if any(real_unit_pos):
                        global_unit_pos = []
                        for element in real_unit_pos:
                            if element == 0:
                                global_unit_pos.append(-1)
                            else:
                                global_unit_pos.append(global_id)

                        all_mappings.append(global_unit_pos)
                        global_unit_counter += 1

                channel_stops.append(global_unit_counter)

            mapping_array = np.vstack(all_mappings)

            mapping_mesh_plot = SwanColorMeshItem(mapping_array.T)
            mapping_mesh_plot.clicked.connect(self.on_mapping_clicked)

            self.pg_canvas.addItem(mapping_mesh_plot)

            for channel_stop in channel_stops:
                line = pg.InfiniteLine(pos=channel_stop, angle=0, pen=pg.fn.mkPen(color='k', width=3))
                self.pg_canvas.addItem(line)

    @QtCore.pyqtSlot(object, object)
    def on_mapping_clicked(self, x, y):
        pass


class SwanColorMeshItem(pg.GraphicsObject):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`
    """

    clicked = QtCore.pyqtSignal(object, object)

    def __init__(self, *args, **kwargs):
        """
        Create a pseudocolor plot with convex polygons.

        Function adapted from pyqtgraph's PColorMeshItem:

        https://github.com/pyqtgraph/pyqtgraph/blob/master/pyqtgraph/graphicsItems/PColorMeshItem.py

        Call signature:
        ``PColorMeshItem([x, y,] z, **kwargs)``
        x and y can be used to specify the corners of the quadrilaterals.
        z must be used to specified to color of the quadrilaterals.
        Parameters
        ----------
        x, y : np.ndarray, optional, default None
            2D array containing the coordinates of the polygons
        z : np.ndarray
            2D array containing the value which will be maped into the polygons
            colors.
            If x and y is None, the polygons will be displaced on a grid
            otherwise x and y will be used as polygons vertices coordinates as::
                (x[i+1, j], y[i+1, j])           (x[i+1, j+1], y[i+1, j+1])
                                    +---------+
                                    | z[i, j] |
                                    +---------+
                    (x[i, j], y[i, j])           (x[i, j+1], y[i, j+1])
            "ASCII from: <https://matplotlib.org/3.2.1/api/_as_gen/
                         matplotlib.pyplot.pcolormesh.html>".
        edgecolors : dict, default None
            The color of the edges of the polygons.
            Default None means no edges.
            The dict may contains any arguments accepted by :func:`mkColor() <pyqtgraph.mkColor>`.
            Example:
                ``mkPen(color='w', width=2)``
        antialiasing : bool, default False
            Whether to draw edgelines with antialiasing.
            Note that if edgecolors is None, antialiasing is always False.
        """

        super(SwanColorMeshItem, self).__init__()

        self.qpicture = None  # rendered picture for display

        self.axisOrder = pg.getConfigOption('imageAxisOrder')

        self.edgecolors = kwargs.get("edgecolors", None)
        self.antialiasing = kwargs.get("antialiasing", False)

        self.lut = UNIT_COLORS

        self.border = None

        # If some data have been sent we directly display it
        if len(args) > 0:
            self.set_data(*args)

    def _prepare_data(self, args):
        """
        Check the shape of the data.
        Return a set of 2d array x, y, z ready to be used to draw the picture.
        """

        # User didn't specified data
        if len(args) == 0:

            self.x = None
            self.y = None
            self.z = None

        # User only specified z
        elif len(args) == 1:
            # If x and y is None, the polygons will be displaced on a grid
            x = np.arange(0, args[0].shape[0] + 1, 1)
            y = np.arange(0, args[0].shape[1] + 1, 1)
            self.x, self.y = np.meshgrid(x, y, indexing='ij')
            self.z = args[0]

        # User specified x, y, z
        elif len(args) == 3:

            # Shape checking
            if args[0].shape[0] != args[2].shape[0] + 1 or args[0].shape[1] != args[2].shape[1] + 1:
                raise ValueError('The dimension of x should be one greater than the one of z')

            if args[1].shape[0] != args[2].shape[0] + 1 or args[1].shape[1] != args[2].shape[1] + 1:
                raise ValueError('The dimension of y should be one greater than the one of z')

            self.x = args[0]
            self.y = args[1]
            self.z = args[2]

        else:
            ValueError('Data must been sent as (z) or (x, y, z)')

    def set_data(self, *args):
        """
        Set the data to be drawn.
        Parameters
        ----------
        x, y : np.ndarray, optional, default None
            2D array containing the coordinates of the polygons
        z : np.ndarray
            2D array containing the value which will be maped into the polygons
            colors.
            If x and y is None, the polygons will be displaced on a grid
            otherwise x and y will be used as polygons vertices coordinates as::

                (x[i+1, j], y[i+1, j])           (x[i+1, j+1], y[i+1, j+1])
                                    +---------+
                                    | z[i, j] |
                                    +---------+
                    (x[i, j], y[i, j])           (x[i, j+1], y[i, j+1])
            "ASCII from: <https://matplotlib.org/3.2.1/api/_as_gen/
                         matplotlib.pyplot.pcolormesh.html>".
        """

        # Prepare data
        cd = self._prepare_data(args)

        # Has the view bounds changed
        shape_changed = False
        if self.qpicture is None:
            shape_changed = True
        elif len(args) == 1:
            if args[0].shape[0] != self.x[:, 1][-1] or args[0].shape[1] != self.y[0][-1]:
                shape_changed = True
        elif len(args) == 3:
            if np.any(self.x != args[0]) or np.any(self.y != args[1]):
                shape_changed = True

        self.qpicture = QtGui.QPicture()
        p = QtGui.QPainter(self.qpicture)
        # We set the pen of all polygons once
        if self.edgecolors is None:
            p.setPen(pg.fn.mkPen(QtGui.QColor(0, 0, 0, 0)))
        else:
            p.setPen(pg.fn.mkPen(self.edgecolors))
            if self.antialiasing:
                p.setRenderHint(QtGui.QPainter.Antialiasing)

        # Prepare colormap
        # First we get the LookupTable
        lut = self.lut

        # # Second we associate each z value, that we normalize, to the lut
        # norm = self.z - self.z.min()
        # norm = norm / norm.max()
        # norm = (norm * (len(lut) - 1)).astype(int)

        z = self.z.copy().astype(int)

        # Go through all the data and draw the polygons accordingly
        for xi in range(self.z.shape[0]):
            for yi in range(self.z.shape[1]):
                # Set the color of the polygon first
                z_val = z[xi][yi]
                if z_val < 0:
                    c = [0, 0, 0]
                else:
                    c = lut[z_val]
                p.setBrush(pg.fn.mkBrush(QtGui.QColor(c[0], c[1], c[2])))

                polygon = QtGui.QPolygonF(
                    [QtCore.QPointF(self.x[xi][yi], self.y[xi][yi]),
                     QtCore.QPointF(self.x[xi + 1][yi], self.y[xi + 1][yi]),
                     QtCore.QPointF(self.x[xi + 1][yi + 1], self.y[xi + 1][yi + 1]),
                     QtCore.QPointF(self.x[xi][yi + 1], self.y[xi][yi + 1])]
                )

                # DrawConvexPlygon is faster
                p.drawConvexPolygon(polygon)

        p.end()
        self.update()

        self.prepareGeometryChange()
        if shape_changed:
            self.informViewBoundsChanged()

    def paint(self, p, *args):
        if self.z is None:
            return

        p.drawPicture(0, 0, self.qpicture)

    def set_border(self, b):
        self.border = pg.fn.mkPen(b)
        self.update()

    def width(self):
        if self.x is None:
            return None
        return np.max(self.x)

    def height(self):
        if self.y is None:
            return None
        return np.max(self.y)

    def boundingRect(self):
        if self.qpicture is None:
            return QtCore.QRectF(0., 0., 0., 0.)
        return QtCore.QRectF(self.qpicture.boundingRect())

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            pos = ev.pos()
            x, y = pos.x(), pos.y()
            self.clicked.emit(x, y)
            print(x, y)
        else:
            ev.ignore()
