import math

import numpy
from PyQt5 import QtWidgets, QtCore
from probeinterface import read_prb, read_probeinterface
import pyqtgraph as pg

class ProbeWidget(QtWidgets.QWidget):

    doChannel = QtCore.pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super(ProbeWidget, self).__init__(*args, **kwargs)
        layout=QtWidgets.QGridLayout()

        self.coordinates = []
        self.dirty_channels = []
        self.lastcannel = 1
        self.currentchannel = 1
        self.brushes = []
        self.blackCoords = []
        self.blue_brush = pg.mkBrush(0, 0, 255, 255)
        self.red_brush = pg.mkBrush(255, 0, 0, 255)
        self.green_brush = pg.mkBrush(0, 255, 0, 255)

        for i in range(0, 10):
            for j in range(0, 10):
                self.coordinates.append([i, j])

        for elem in self.coordinates:
            self.brushes.append(self.blue_brush)

        self.graphWidget = pg.PlotWidget(parent=self)
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        # plot data: x, y values
        self.plot_points(numpy.array(self.coordinates), numpy.array(self.dirty_channels))
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')

    def plot_points(self, coords, dirty):
        self.brushes[self.currentchannel] = self.green_brush
        scatterplot = pg.ScatterPlotItem(pos = coords, brush=self.brushes)
        scatterplot.sigClicked.connect(self.points_clicked)
        self.graphWidget.addItem(scatterplot)

    def points_clicked(self, item, points, ev):
        point = points[0]
        x, y = point.pos().x(), point.pos().y()
        if self.brushes[self.coordinates.index([x, y])] != pg.mkBrush(0, 0, 0, 255):
            self.brushes[self.currentchannel] = self.blue_brush
            self.lastchannel = self.currentchannel
            self.currentchannel = self.coordinates.index([x, y])
            try:
                #self.set_dirty(self.coordinates.index([x, y]))
                self.select_channel(self.coordinates.index([x, y]))
                self.plot_points(numpy.array(self.coordinates), self.dirty_channels)
            except ValueError:
                print('couldnt be found')
        ev.accept()

    def load_geometry(self, filename):
        if filename.endswith('prb'):
            probe = read_prb(filename)
        elif filename.endswith('json'):
            probe = read_probeinterface(filename)
        else: raise ValueError
        self.graphWidget.clear()
        self.coordinates = probe.probes[0].contact_positions.tolist()
        self.chosenCoordsLi = probe.probes[0].contact_positions.tolist()
        self.chosenCoordsArr = probe.probes[0].contact_positions
        self.brushes.clear()
        for elem in self.coordinates:
            self.brushes.append(self.blue_brush)
        self.plot_points(numpy.array(self.coordinates), self.dirty_channels)

    def reset_to_standard_grid(self):

        coordCount = len(self.coordinates)
        self.coordinates.clear()
        self.brushes.clear()
        self.blackCoords.clear()

        for i in range(0, math.ceil(math.sqrt(coordCount))):
            for j in range(0, math.ceil(math.sqrt(coordCount))):
                self.coordinates.append([i, j])
                self.brushes.append(self.blue_brush)
        for k in range(1, len(self.coordinates)-coordCount+1):
            self.brushes[-k] = pg.mkBrush(0, 0, 0, 255)
            self.blackCoords.append(self.coordinates[-k])
        #print(self.coordinates)
        self.graphWidget.clear()
        self.plot_points(numpy.array(self.coordinates), self.dirty_channels)


    def make_grid(self, rows=10, cols=10):
        """
        Creates a grid of widgets which represent the electrodes.

        **Arguments**

            *rows* (integer):
                The number of rows.
                Default: 10.
            *cols* (integer):
                The number of cols.
                Default: 10.

        """
        pass

    def set_channels(self, channel_list=None):
        """
        Sets the channels of the widgets.

        **Arguments**

            channel_list (list of integer or None):
                The channel list which contains the channel ids.
                If None, the default setting will be used.

        """
        pass

    def get_item(self, channel):
        """
        Returns a :class:`SelectorItem` for the given channel.

        **Arguments**

            *channel* (integer):
                The channel id of the item.

            **Returns**: :class:`SelectorItem` or None
                If found, it returns the item.
                If not, it returns None.

        """
        pass

    def select_channel(self, channel):
        """
        Selects a channel and emits the doChannel signal
        which causes the program to change the channel.

        **Arguments**

            *item* (:class:`SelectorItem`):
                The item that should be selected.
            *channel* (integer):
                The channel id of the item.

        """
        lastchannel = self.lastchannel
        self.doChannel.emit(channel, lastchannel)


    def select_only(self, channel):
        """
        Selects the item with the given channel id but emits no signal.

        **Arguments**

            *channel* (integer):
                The channel id of the item
                that should be selected.

        """
        pass

    def reset_sel(self):
        """
        Resets the selected item.

        """
        pass

    def get_dirty_channels(self):
        """
        Returns the channels that are currently dirty.

            **Returns**: list of integer
                Channel ids.

        """
        pass

    def set_dirty(self, channel):
        """
        Sets a item as dirty or not.

        **Arguments**

            *channel* (integer):
                The channel id of the item.

        """
        if channel not in self.dirty_channels:
            self.dirty_channels.append(channel)
            self.brushes[channel] = pg.mkBrush(255, 0, 0, 255)
            self.plot_points(numpy.array(self.coordinates), numpy.array(self.dirty_channels))

    def reset_dirty(self):
        """
        Resets the dirty property for all items.

        """
        pass

    def find_saved(self, vum_all):
        pass

    '''
    def minimumSizeHint(self) -> QtCore.QSize:
        return self.sizeHint()

    def sizeHint(self):
        return QtCore.QSize(200, 250)

    def heightForWidth(self, width):
        return width
        '''