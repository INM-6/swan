"""
Created on Nov 16, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from swan.widgets.mypgwidget import PyQtWidget2d
from numpy import count_nonzero, argmax, zeros, trim_zeros, any as np_any, mean as mn, array
from sklearn.decomposition import PCA


class pgWidgetPCA2d(PyQtWidget2d):
    """
    A class with only one plot that shows 2d PCA scatter plots.

    """

    def __init__(self):
        """
        **Properties**

            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.

        """
        PyQtWidget2d.__init__(self)

        layers = ["units", "sessions"]
        self.toolbar.setup_radio_buttons(layers)
        self.toolbar.doLayer.connect(self.trigger_refresh)
        self.toolbar.collapsible_widget.set_content_layout(self.toolbar.grid_layout)
        self.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)

        self._plotItem = self.pg_canvas.getPlotItem()
        self._plotItem.enableAutoRange()

        self._means = []
        self._positions = []

        self.show_grid()

    #### general methods ####

    def plotMean(self, x, y, size, color, name, pxMode=True):
        x = [x]
        y = [y]
        self._means.append(self.create_scatter_plot_item(x=x, y=y, size=size, color=color, name=name, pxMode=pxMode))

    def plotPoints(self, pos, size, color, name, pxMode=True):
        pos = array(pos)
        x = pos[:, 0]
        y = pos[:, 1]
        self._positions.append(
            self.create_scatter_plot_item(x=x, y=y, size=size, color=color, name=name, pxMode=pxMode, autoDownsample=True,
                                          antialias=True))

    def do_plot(self, vum, data):
        """
        Plots data for every layer and every visible unit.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed to get the unit indexes.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get the units.
            *layers* (list of string):
                The layers that are visible.
        
        """
        self.clear_plots()

        if self.toolbar.layers.isChecked():

            layers = self.toolbar.get_checked_layers()

            self.wave_length = data.get_wave_length()

            active = vum.get_active().tolist()

            if np_any(active) and layers:
                for n, num in enumerate(active):
                    active[n] = trim_zeros(num, 'b')
                    if not active[n]:
                        active[n] = [0]
                dom = argmax([count_nonzero(nu) for nu in active])
                dom_channel = []

                for j in range(len(active[dom])):
                    runit = vum.get_realunit(dom, j, data)
                    if active[dom][j]:
                        dom_channel.append(data.get_data("all", runit))

                m_dom_channel, lv_dom_channel = self.merge_channel(dom_channel)

                pca = PCA(n_components=2)

                dom_pca = pca.fit_transform(m_dom_channel)
                dom_ch_pca = self.split_waves(dom_pca, lv_dom_channel, 'all')

                for layer in layers:
                    if layer == "units":
                        for i in range(len(active)):
                            if i != dom:
                                session = []
                                for j in range(len(active[i])):
                                    runit = vum.get_realunit(i, j, data)
                                    if active[i][j]:
                                        session.append(data.get_data("all", runit))

                                merged_channel, len_vec = self.merge_channel(session)
                                try:
                                    pca_channel = self.split_waves(pca.transform(merged_channel), len_vec, 'all')

                                    c = 0
                                    for u in range(len(active[i])):
                                        if active[i][u]:
                                            col = vum.get_colour(u)
                                            self.plotPoints(pos=pca_channel[c], size=1, color=col, name="".format(i, u))
                                            self.plotMean(x=mn(pca_channel[c][:, 0], axis=0),
                                                          y=mn(pca_channel[c][:, 1], axis=0), size=15, color=col,
                                                          name="".format(i, u))
                                            c += 1

                                    del session
                                    del merged_channel
                                    del pca_channel

                                except ValueError:
                                    pass

                            elif i == dom:
                                c = 0
                                for u in range(len(active[dom])):
                                    if active[dom][u]:
                                        col = vum.get_colour(u)
                                        self.plotPoints(pos=dom_ch_pca[c], size=1, color=col, name="".format(i, u))
                                        self.plotMean(x=mn(dom_ch_pca[c][:, 0], axis=0),
                                                      y=mn(dom_ch_pca[c][:, 1], axis=0), size=15, color=col,
                                                      name="".format(i, u))
                                        c += 1

                    #                if layer == "sessions":
                    #                    for i in range(len(data.blocks)):
                    #                        if i != dom:
                    #                            session = []
                    #                            for j in range(len(active[i])):
                    #                                runit = vum.get_realunit(i, j, data)
                    #                                if active[i][j] != 0 and vum.visible[j] and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                    #                                    session.append(data.get_data("all", runit))
                    #
                    #                            merged_channel, len_vec = self.merge_channel(session)

                    del dom
                    del dom_channel
                    del dom_ch_pca
                    del dom_pca
            else:
                print("Something is wrong!")
                print("Length of positions list: {}".format(len(self._positions)))
                print("Length of means list: {}".format(len(self._means)))

    def merge_channel(self, session):
        total_length = 0
        length_vector = [0]

        for unit in session:
            total_length += len(unit)
            length_vector.append(total_length)

        waves = zeros((total_length, self.wave_length))

        for u, unit in enumerate(session):
            for wf, wave in enumerate(unit):
                waves[wf + length_vector[u]] = wave

        return waves, length_vector

    def split_waves(self, waves, length_vector, components):

        session = []

        if components == 'all':
            for n in range(len(length_vector) - 1):
                session.append(waves[length_vector[n]:length_vector[n + 1]])
        else:
            for n in range(len(length_vector) - 1):
                session.append(waves[length_vector[n]:length_vector[n + 1], :components])

        return session

    def connectPlots(self):
        for item in self._means:
            item.curve.set_clickable(True, width=5)
            item.sigClicked.connect(self.get_item)

    def clear_plots(self):
        self._means = []
        for item in self._positions:
            self.pg_canvas.removeItem(item)
        self._positions = []
        self.clear_all()
