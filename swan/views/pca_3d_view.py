#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 12:56:06 2017

@author: sridhar
"""

from swan.widgets.mypgwidget import PyQtWidget3d
from numpy import count_nonzero, argmax, amax, zeros, trim_zeros, any as np_any
from sklearn.decomposition import PCA
from itertools import chain


class PgWidgetPCA(PyQtWidget3d):

    def __init__(self, parent=None):

        PyQtWidget3d.__init__(self, parent=parent)

        layers = ["units", "sessions"]
        self.toolbar.setup_radio_buttons(layers)
        self.toolbar.doLayer.connect(self.trigger_refresh)
        self.toolbar.collapsible_widget.set_content_layout(self.toolbar.grid_layout)
        self.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.setup_axes(gl_options='opaque')
        self.positions = []
        self.means = []

        self.fill_alpha = 0.9

        self.pg_canvas.set_clickable(True)

        self.max_distance = 0
        self.wave_length = 0  # Initial dummy value, later updated from data

    def add_scatter_plot(self, plot_item=None, gl_options='opaque'):
        self.add_scatter_plot_item(plot_item=plot_item, gl_options=gl_options)

    def clear_plot(self):
        self.reset_plot()
        self.positions = []
        self.means = []

    def connect_means(self):
        self.pg_canvas.set_means(self.means)
        # for plot in self.pg_canvas.means:
        #     plot.sig_clicked.connect(self.get_item)

    def do_plot(self, vum, data):
        self.save_camera_position()
        self.clear_plot()

        if self.toolbar.activate_button.current_state:

            layers = self.toolbar.get_checked_layers()

            max_distance = 0

            self.wave_length = data.get_wave_length()

            active = vum.get_active().tolist()

            if np_any(active) and layers:
                for n, num in enumerate(active):
                    active[n] = trim_zeros(num, 'b')
                    if not active[n]:
                        active[n] = [0]

                dom = argmax([count_nonzero(nu) for nu in active])
                dom_session = []

                for unit_index in range(len(active[dom])):
                    if active[dom][unit_index]:
                        runit = vum.get_realunit(dom, unit_index, data)
                        dom_session.append(data.get_data("all", runit))

                m_dom_session, lv_dom_session = self.merge_session(dom_session)

                pca = PCA(n_components=3)
                dom_pca = pca.fit_transform(m_dom_session)
                dom_ch_pca = self.split_waves(dom_pca, lv_dom_session, 'all')

                for layer in layers:
                    if layer == "units":
                        for session_index in range(len(active)):
                            if session_index != dom:
                                session = []
                                for unit_index in range(len(active[session_index])):
                                    if active[session_index][unit_index]:
                                        runit = vum.get_realunit(session_index, unit_index, data)
                                        session.append(data.get_data("all", runit))

                                merged_session, len_vec = self.merge_session(session)
                                try:
                                    pca_session = self.split_waves(pca.transform(merged_session), len_vec, 'all')

                                    max_distance = self.return_max(pca_session)
                                    if max_distance > self.max_distance:
                                        self.max_distance = max_distance

                                    c = 0
                                    for unit_index in range(len(active[session_index])):
                                        if active[session_index][unit_index]:
                                            col = vum.get_colour(unit_index)
                                            col = tuple(val / 255. for val in col) + (self.fill_alpha,)
                                            self.positions.append(
                                                self.create_scatter_plot_item(pos=pca_session[c], size=1, color=col,
                                                                              unit_id=unit_index, session=session_index,
                                                                              px_mode=True))
                                            self.means.append(
                                                self.create_scatter_plot_item(pos=pca_session[c].mean(axis=0), size=15,
                                                                              color=col, unit_id=unit_index,
                                                                              session=session_index, px_mode=True,
                                                                              clickable=True))
                                            c += 1

                                    del session
                                    del merged_session
                                    del pca_session

                                except ValueError:
                                    pass

                            elif session_index == dom:
                                try:
                                    max_distance = self.return_max(dom_ch_pca)
                                    if max_distance > self.max_distance:
                                        self.max_distance = max_distance

                                    c = 0
                                    for unit_index in range(len(active[dom])):
                                        if active[dom][unit_index]:
                                            col = vum.get_colour(unit_index)
                                            col = tuple(val / 255. for val in col) + (self.fill_alpha,)
                                            self.positions.append(
                                                self.create_scatter_plot_item(pos=dom_ch_pca[c], size=1, color=col,
                                                                              unit_id=unit_index, session=session_index,
                                                                              px_mode=True))
                                            self.means.append(
                                                self.create_scatter_plot_item(pos=dom_ch_pca[c].mean(axis=0), size=15,
                                                                              color=col, unit_id=unit_index,
                                                                              session=session_index, px_mode=True,
                                                                              clickable=True))
                                            c += 1
                                except ValueError:
                                    pass

                    del dom
                    del dom_session
                    del dom_ch_pca
                    del dom_pca

            if len(self.positions) == len(self.means):
                for item in self.positions:
                    self.add_scatter_plot(item, gl_options='translucent')
                for mean in self.means:
                    self.add_scatter_plot(mean, gl_options='opaque')
                self.connect_means()
            else:
                print("Something is wrong!")
                print("Length of positions list: {}".format(len(self.positions)))
                print("Length of means list: {}".format(len(self.means)))

            if self.camera_position is not None:
                self.restore_camera_position()

    def merge_session(self, session):
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

    def return_max(self, nested_list):
        return amax(list(chain.from_iterable(nested_list)))
