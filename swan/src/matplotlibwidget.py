"""
Created on Wed Feb, 2013
@author: Christoph Gollan
In this module you can find the :class:`MatplotlibWidget` which is
a matplotlib to PyQt aggregation widget.
To achieve that a :class:`MplCanvas` is needed. This class puts
a matplotlib figure to a canvas (which is already a PyQt
aggregation). So the figure can be used like the normal matplotlib
figure.
On default, the figure will not have a :class:`NavigationToolbar`,
but you can activate it.
"""
from PyQt5 import QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2QTAgg
import matplotlib
# matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


class MplCanvas(FigureCanvasQTAgg):
    """
  A class to get a matplotlib figure on a canvas.

  """

    def __init__(self):
        """

    """
        # create the figure on which the plots can be added
        self.fig = Figure(facecolor="white")

        # add this figure to a canvas
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)


class NavigationToolbar(NavigationToolbar2QTAgg):
    """
  A NavigationToolbar extended with some functions for using
  in a PyQt aggregation.
  **Arguments**
      *plotCanvas* (:class:`src.matplotlibwidget.MplCanvas`):
          The canvas the toolbar belongs to.
      *parent* (:class:`PyQt4.QtGui.QWidget`):
          The parent object for the toolbar.
      *custom_actions* (boolean):
          If true, some custom actions will be created on the toolbar.
  """

    def __init__(self, plotCanvas, parent, custom_actions=True):
        """
    **Properties**

        *_firstChange* (boolean):
            Whether or not the y limits of the plots were
            changed before.
        *_plot_params* (dictionary):
            The plot parameters given as (key, value) pare.

    """
        NavigationToolbar2QTAgg.__init__(self, plotCanvas, parent)

        # properties {
        self._firstChange = True
        self._plot_params = {"xlim": [0, 38],
                             "ylim": [-300, 300]}
        # }

        # custom actions {
        if custom_actions:
            self.addSeparator()
            self.action_reset = self.addAction("Reset", self.onReset)
            self.action_reset.setToolTip("Reset the y limits")
            self.action_plus = self.addAction("+", self.onPlus)
            self.action_plus.setToolTip("Expand the y limits")
            self.action_minus = self.addAction("-", self.onMinus)
            self.action_minus.setToolTip("Reduce the y limits")
        # }

    #### General methods ####

    def add_action(self, name, handle):
        """
    Adds a custom action to the toolbar.
    **Arguments**
        *name* (string):
            The name of the action.
        *handle* (method):
            The python method that should be called
            if you click on the action.
    **Returns**
        ???
    """
        return self.addAction(name, handle)

    def remove_custom_actions(self):
        """
    Removes the initial custom actions from the toolbar.
    """
        self.removeAction(self.action_reset)
        self.removeAction(self.action_plus)
        self.removeAction(self.action_minus)

    def remove_actions(self, actions):
        """
    Removes default actions from the toolbar.
    **Arguments**
        *actions* (list of integer):
            The indexes of the actions that should be
            removed.
    """
        for i in actions:
            self.removeAction(self.actions()[i])

    #### Action handler ####

    def onReset(self):
        """
    Resets the ylim of all subplots.

    """
        if not self._firstChange:
            axes_list = self.canvas.fig.get_axes()
            for ax in axes_list:
                limx = self._plot_params['xlim']
                ax.set_xlim(limx[0], limx[1])
                limy = self._plot_params['ylim']
                ax.set_ylim(limy[0], limy[1])
            self.canvas.draw()

    def onPlus(self, step=1.0):
        """
    Expands the ylim of all subplots.

    """
        axes_list = self.canvas.fig.get_axes()
        for ax in axes_list:
            limy = ax.get_ylim()
            limx = ax.get_xlim()
            rat = abs((limy[1] - limy[0]) / 2) / abs((limx[1] - limx[0]) / 2)
            if self._firstChange:
                self._plot_params["ylim"] = limy
                self._plot_params["xlim"] = limx
                self._firstChange = False
            ax.set_ylim(limy[0] / rat, limy[1] / rat)
            ax.set_xlim(limx[0] / rat, limx[1] / rat)
        self.canvas.draw()

    def onMinus(self, step=1.0):
        """
    Reduces the ylim of all subplots.

    """
        axes_list = self.canvas.fig.get_axes()
        for ax in axes_list:
            limy = ax.get_ylim()
            limx = ax.get_xlim()
            rat = abs((limy[1] - limy[0]) / 2) / abs((limx[1] - limx[0]) / 2)
            if self._firstChange:
                self._plot_params["ylim"] = limy
                self._plot_params["xlim"] = limx
                self._firstChange = False
            ax.set_ylim(limy[0] * rat, limy[1] * rat)
            ax.set_xlim(limx[0] * rat, limx[1] * rat)
        self.canvas.draw()


class MatplotlibWidget(QtWidgets.QWidget):
    """
  A class to have a PyQt widget with a matplotlib figure on it.

  **Arguments**

      *parent* (:class:`PyQt5.QtGui.QWidget` or None):
          The parent of this widget.
          Default: None

  """

    def __init__(self, parent=None, c_actions=False):
        """

    """
        QtGui.QWidget.__init__(self, parent=parent)

        vgl = QtGui.QGridLayout(self)
        self.vgl = vgl
        self.canvas = MplCanvas()
        self.naviBar = NavigationToolbar(self.canvas, self, custom_actions=c_actions)
        self.naviBar.hide()
        vgl.addWidget(self.canvas, 0, 0, 1, 1)
        vgl.addWidget(self.naviBar, 1, 0, 1, 1)
        self.setLayout(vgl)

        # properties {
        # }

    #### General methods ####

    def setup(self, shape=(1, 1), naviBar=True, proj3d=False):
        """
    Sets up the widget.

    The shape format is: *(rows, cols)*.
    Set *naviBar* to *True* to activate the :class:`NavigationToolbar`.

    **Arguments**

        *shape* (tuple of integer):
            The shape of the plot grid.
        *naviBar* (boolean):
            Whether or not you want to have the tool bar enabled.
        *proj3d* (boolean):
            Whether or not you want to have a 3d plot instead of a 2d plot.

    """
        self._grid(shape, proj3d)
        if naviBar:
            self.naviBar.show()

    def _grid(self, shape, proj3d):
        """
    Creates a plot grid.

    **Arguments**

        *shape* (tuple of integer):
            The shape of the plot grid.
        *proj3d* (boolean):
            Whether or not there will be a 3d plot instead of a 2d plot.

    """
        m = shape[0]
        n = shape[1]
        if proj3d:
            for i in range(1, n * m + 1):
                self.canvas.fig.add_subplot(m, n, i, projection='3d')
        else:
            for i in range(1, n * m + 1):
                self.canvas.fig.add_subplot(m, n, i)

    def get_axes(self):
        """
    Wrapper for getting the axes.

        **Returns**: list of :class:`matplotlib.axes.Axes` or list of :class:`mpl_toolkits.mplot3d.Axes3d`
            All plots on the grid.

    """
        return self.canvas.fig.get_axes()

    def draw(self):
        """
    Wrapper for the draw function. Draws everything.

    """
        self.canvas.draw()

    def pca_draw(self, axis, patchCollection, kwargs):
        """
    Wrapper for the drawing the PCA. Draws only the patch collection (scatter
    plot) and the background (ax.patch).

    """

        axis.draw_artist(axis.patch)
        axis.draw_artist(patchCollection)

        self.canvas.fig.canvas.update()
        self.canvas.fig.canvas.flush_events()

        for k, v in kwargs.items():
            getattr(axis, str(k))(v)

    def clear_and_reset_axes(self, grid=True, tick_params={"labelsize": 7, }, **kwargs):
        """
    Clears the axes and sets the parameter for the axes
    because otherwise they are lost.

    If *kwargs* is set, for every entry *<key>(<value>)* will be called.
    If not, some default *kwargs* will be set.

    **Arguments**

        *grid* (boolean):
            Whether or not you want a grid on your plot.
        *tick_params* (dictionary):
            A dictionary containing tick parameters.

    """
        axes_list = self.canvas.fig.get_axes()
        if not kwargs:
            kwargs = {"set_ylim": (-150, 150),
                      "set_xlabel": "time",
                      "set_ylabel": "voltage"}
        for ax in axes_list:
            ax.cla()
            ax.grid(grid)
            ax.tick_params(**tick_params)
            for k, v in kwargs.items():
                getattr(ax, str(k))(v)
