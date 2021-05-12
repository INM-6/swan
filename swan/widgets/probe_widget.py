import numpy
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

        #self.standardCoords = []

        layout=QtWidgets.QGridLayout()

        standardCoordsTmp = []
        for i in range(1, 11):
            for j in range(1, 11):
                standardCoordsTmp.append((i, j))
        self.standardCoords = numpy.array(standardCoordsTmp)

        self.graphWidget = pg.PlotWidget(parent=self)
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        # plot data: x, y values
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')
        self.graphWidget.plot(self.standardCoords, pen=None, symbol='o', symbolSize=10, clickable=True)



    def update(self, filename):
        if filename.endswith('prb'):
            probe = read_prb(filename)
            self.graphWidget.clear()
            self.graphWidget.plot(probe.probes[0].contact_positions, pen=None, symbol='o', symbolSize=10)
        elif filename.endswith('json'):
            print('json')
            probe = read_probeinterface(filename)
            self.graphWidget.clear()
            self.graphWidget.plot(probe.probes[0].contact_positions, pen=None, symbol='o', symbolSize=10)
        else: raise ValueError


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
        pass

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