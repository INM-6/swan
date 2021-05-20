import numpy
import numpy as np
from PyQt5 import QtWidgets, QtCore
from probeinterface import get_probe, Probe, read_prb, read_probeinterface
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os

class ProbeWidget(QtWidgets.QWidget):

    doChannel = QtCore.pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super(ProbeWidget, self).__init__(*args, **kwargs)


        layout=QtWidgets.QGridLayout()

        self.coordinates = []
        self.dirty_channels = []
        self.lastcannel = 1
        self.currentchannel = 1

        for i in range(1, 11):
            for j in range(1, 11):
                self.coordinates.append([i, j])

        self.graphWidget = pg.PlotWidget(parent=self)
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        # plot data: x, y values
        self.plot_points(numpy.array(self.coordinates))
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')

    def plot_points(self, coords):
        scatterplot = pg.ScatterPlotItem(pos = coords)
        scatterplot.sigClicked.connect(self.points_clicked)
        self.graphWidget.addItem(scatterplot)

    def points_clicked(self, item,  points, ev):
        point = points[0]
        x, y = point.pos().x(), point.pos().y()
        try:
            print(self.coordinates.index([x, y]))
            self.dirty_channels.append(self.coordinates.index([x, y]))
            self.select_channel(self, self.coordinates.index([x, y]))
        except ValueError:
            print('couldnt be found')
        ev.accept()

    def load_geometry(self, filename): #bsp load_geometry
        if filename.endswith('prb'):
            probe = read_prb(filename)
        elif filename.endswith('json'):
            probe = read_probeinterface(filename)
        else: raise ValueError
        self.graphWidget.clear()
        self.coordinates = probe.probes[0].contact_positions.tolist()
        self.chosenCoordsLi = probe.probes[0].contact_positions.tolist()
        self.chosenCoordsArr = probe.probes[0].contact_positions
        self.plot_points(numpy.array(self.coordinates))


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

    def select_channel(self, item, channel):
        """
        Selects a channel and emits the doChannel signal
        which causes the program to change the channel.

        **Arguments**

            *item* (:class:`SelectorItem`):
                The item that should be selected.
            *channel* (integer):
                The channel id of the item.

        """
        self.lastchannel = self.currentchannel
        self.currentchannel = channel
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

    def set_dirty(self, channel, dirty):
        """
        Sets a item as dirty or not.

        **Arguments**

            *channel* (integer):
                The channel id of the item.
            *dirty* (boolean):
                Whether or not the item is dirty.

        """
        pass

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