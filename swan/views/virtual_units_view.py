"""
Created on Mar 10, 2015

@author: Christoph Gollan

In this module you can find the :class:`VUnits` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 2d plot and the plotting methods.
"""
import math
import numpy as np
from matplotlib import colors
from matplotlib.ticker import FixedLocator, FormatStrFormatter
from swan.gui.palettes import UNIT_COLORS
from swan.widgets.matplotlib_widget import MatplotlibWidget
from pyqtgraph.Qt import QtCore, QtWidgets


class VUnits(MatplotlibWidget):
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
        """
        **Properties**

            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
            *_cmap* (:class:`matplotlib.colors.ListedColormap`)
                A colormap for the pcolormesh plot.
            *_settings* (dictionary):
                A dictionary containing settings as key value pares.

        """
        MatplotlibWidget.__init__(self, *args, **kwargs)

        self.setup(naviBar=True)
        #self.naviBar.remove_custom_actions()
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(["1", "2", "3", "auto"])
        # self.combo.addItems(["1", "2", "3"])
        self.naviBar.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.settings_changed)
        self.canvas.mpl_connect("pick_event", self.on_pick)

        clist = UNIT_COLORS / 255.

        #properties{
        self._axes = self.get_axes()[0]
        self._cmap = colors.ListedColormap(clist, N=20)
        self._settings = {"num_vu":"1"}
        #}


    def on_pick(self, event):
        """
        Is called if you pick a virtual unit in the pcolor plot.

        **Arguments**

            *event* (:class:`matplotlib.backend_bases.PickEvent`):
                The pick event with information
                about what was picked.

        """
        ymouse = event.mouseevent.ydata
        y = math.ceil(ymouse)
        num_vu = self._settings["num_vu"]
        try:
            num_vu = int(num_vu)
            channel = int(y/num_vu)
            self.load.emit(channel)
        except:
            pass

    def settings_changed(self):
        """
        Is called if you select something in the combobox in the
        navigation toolbar.

        Emits a signal to redraw the plot.

        """
        self._settings["num_vu"] = str(self.combo.currentText())
        self.redraw.emit()

    def plot(self, y):
        """
        Plots data to the plot.

        **Arguments**

            *y* (tuple of iterable objects):
                The data that should be plotted.

        """
        self._axes.pcolormesh(y, cmap=self._cmap, picker=True)

    def do_plot(self, vum, data):
        """
        Plots data.

        **Arguments**

            *vum* (dictionary):
                A dictionary containing all virtual unit maps.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get block length.

        """
        kwargs = {"set_xlabel":"sessions", "set_ylabel":"electrodes and virtual units"}
        tick_params = {"which":"both", "direction":"out", "labelsize":8}
        self.clear_and_reset_axes(grid=True, tick_params=tick_params, **kwargs)
        num_vu = self._settings["num_vu"]
        l = len(data.blocks)

        if num_vu != "auto":
            # num_vu is an integer
            num_vu = int(num_vu)

        values = []
        lens = []
        # for every channel
        for i in range(100):
            lens.append(0)
            try:
                m = vum["vum" + str(i+1)]

                if num_vu == "auto":
                    # search for the indexes of the virtual units
                    inds = []
                    kmax = max([key for key in m.keys() if isinstance(key, int)])
                    for k in range(kmax):
                        for j in range(l):
                            v = m[k+1][j][1]
                            if v is not None:
                                inds.append(k)
                                lens[i] += 1
                                break
                else:
                    kmax = num_vu
                    inds = range(kmax)

                # for every virtual unit to show
                for k in inds:
                    val = []
                    # for every session
                    for j in range(l):
                        v = m[k+1][j][1]
                        if v is not None:
                            if i % 2 == 0:
                                val.append(0.1 * (k+1))
                            else:
                                val.append(1 - 0.1 * (k+1))
                        else:
                            val.append(0)
                    values.append(val)
            except:
                if num_vu != "auto":
                    for k in range(num_vu):
                        values.append([0 for j in range(l)])
                else:
                    lens[i] = 1
                    values.append([0 for j in range(l)])

        if num_vu != "auto":
            maj_ticks = [num_vu * i * 2 for i in range(50)]
            min_ticks = [num_vu * i for i in range(100)]
        else:
            min_ticks = [sum(lens[:i]) for i in range(100)]
            maj_ticks = [min_ticks[i*2] for i in range(50)]

        minorLocator = FixedLocator(min_ticks)
        majorLocator = FixedLocator(maj_ticks)

        labels = ["ch. " + str(1+i*2) for i in range(0, 50)]

        # loc = MultipleLocator(1)
        loc = FixedLocator(range(l+1))
        majorFormatter = FormatStrFormatter('%d')

        # setting the major and minor ticks
        self._axes.xaxis.set_major_formatter(majorFormatter)
        self._axes.xaxis.set_major_locator(loc)
        self._axes.yaxis.set_major_locator(majorLocator)
        self._axes.yaxis.set_major_formatter(majorFormatter)
        self._axes.yaxis.set_minor_locator(minorLocator)

        self._axes.set_title("pick a virtual unit to go to the channel")

        self.plot(np.array(values))
        self.draw()

        # setting the labels
        self._axes.set_xticklabels([str(i) for i in range(l+1)])
        self._axes.set_yticklabels(labels)
        self.draw()


# if __name__ == "__main__":
#     import sys
#     from PyQt5.QtGui import QApplication
#
#     app = QApplication(sys.argv)
#     m = VUnits()
#     m.show()
#     sys.exit(app.exec_())