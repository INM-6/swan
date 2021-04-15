import time
import numpy as np
import pandas as pd
import elephant as el
import pyqtgraph as pg

from scipy import stats
from multiprocessing import Pool
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from PyQt5 import QtWidgets, QtCore

from swan.gui.parameter_input_dialog_ui import ParameterInputDialogUI


def p2p_amplitude(waves):
    return np.amax(waves[:, 10:], axis=1) - np.amin(waves[:, 10:], axis=1)


def asymmetry(waves):
    return np.amax(waves[:, 10:], axis=1) / np.amin(waves[:, 10:], axis=1)


def square_sum(waves):
    return np.sum(np.einsum('ij, ij -> ij', waves, waves), axis=1)


def diff(waves):
    return np.gradient(waves, axis=1).mean(axis=0)


def diffdiff(waves):
    return np.gradient(np.gradient(waves, axis=1), axis=1).mean(axis=0)


def isi(train):
    return el.statistics.isi(train)


def lv(train):
    intervals = isi(train)
    return el.statistics.lv(intervals)


def cv2(train):
    intervals = isi(train)
    return el.statistics.cv2(intervals)


def fr(train):
    return el.statistics.mean_firing_rate(train)


def isih(train, bin_max, bin_step):
    intervals = isi(train)
    hist, bins = np.histogram(intervals, bins=range(0, bin_max, bin_step), density=True)
    return hist


def run_kmeans_solver(data, n_clusters, n_init=10):
    solver = KMeans(n_clusters=n_clusters, n_init=n_init)
    solver.fit(data)
    clusters = solver.cluster_centers_
    labels = solver.predict(data)
    return solver, clusters, labels


def run_kmeans_solver_no_prediction(data, n_clusters, n_init=10):
    solver = KMeans(n_clusters=n_clusters, n_init=n_init)
    solver.fit(data)
    return solver, n_clusters


def generate_feature_vectors(parent_class, feature_dictionary, additional_dictionary):
    feature_vectors = []

    for u, (waves, train, reduced_mean, mean) in \
            enumerate(zip(parent_class.all_waveforms,
                          parent_class.all_spiketrains,
                          parent_class.reduced_means,
                          parent_class.mean_waveforms)):
        feature_vectors.append([])
        if feature_dictionary['p2p amplitude']:
            feature_vectors[u].extend(list(stats.describe(p2p_amplitude(waves)))[2:])
        if feature_dictionary['asymmetry']:
            feature_vectors[u].extend(list(stats.describe(asymmetry(waves)))[2:])
        if feature_dictionary['square sum']:
            feature_vectors[u].extend(list(stats.describe(square_sum(waves)))[2:])
        if feature_dictionary['spike width']:
            feature_vectors[u].extend(list(stats.describe(spike_width(waves)))[2:])
        if feature_dictionary['cv2']:
            feature_vectors[u].append((cv2(train)))
        if feature_dictionary['lv']:
            feature_vectors[u].append((lv(train)))
        if feature_dictionary['firing rate']:
            feature_vectors[u].append((fr(train)))
        if feature_dictionary['mean']:
            feature_vectors[u].extend(mean)
        if feature_dictionary['reduced mean']:
            feature_vectors[u].extend(reduced_mean)
        if feature_dictionary['first derivative']:
            feature_vectors[u].extend(diff(waves))
        if feature_dictionary['second derivative']:
            feature_vectors[u].extend(diffdiff(waves))
        if feature_dictionary['described isi']:
            feature_vectors[u].extend(list(stats.describe(isih(train,
                                                               additional_dictionary['bin max'],
                                                               additional_dictionary['bin step']
                                                               )
                                                          )
                                           )[2:]
                                      )
        if feature_dictionary['isi']:
            feature_vectors[u].extend(isih(train,
                                           additional_dictionary['bin max'],
                                           additional_dictionary['bin step']
                                           )
                                      )

    feature_vectors = np.array(feature_vectors)
    feature_vectors = (feature_vectors - feature_vectors.mean(axis=0, keepdims=True)) / feature_vectors.std(axis=0)

    return np.nan_to_num(feature_vectors)


def get_session_ids(blocks):
    session_ids = []
    for b, block in enumerate(blocks):
        units = block.groups
        for unit in units:
            session_ids.append(b)

    return session_ids


def get_real_unit_ids(blocks):
    unit_ids = []
    for block in blocks:
        units = block.groups
        for u, unit in enumerate(units):
            unit_ids.append(u)

    return unit_ids


def get_mean_waveforms(blocks):
    mean_waveforms = []
    for block in blocks:
        units = block.groups
        for unit in units:
            waves = unit.spiketrains[0].waveforms.magnitude[:, 0, :]
            waves = waves - waves.mean(axis=1, keepdims=True)
            mean_waveforms.append(waves.mean(axis=0))

    return mean_waveforms


def get_all_waveforms(blocks):
    waveforms = []
    for block in blocks:
        units = block.groups
        for unit in units:
            waves = unit.spiketrains[0].waveforms.magnitude[:, 0, :]
            waves = waves - waves.mean(axis=1, keepdims=True)
            waveforms.append(waves)
    return waveforms


def get_all_spiketrains(blocks):
    spiketrains = []
    for block in blocks:
        units = block.groups
        for unit in units:
            train = unit.spiketrains[0].times.magnitude
            spiketrains.append(train)
    return spiketrains


def get_time_stamps(blocks):
    all_time_stamps = []
    for block in blocks:
        units = block.groups
        for unit in units:
            all_time_stamps.append(block.rec_datetime)

    corrected_time_stamps = []
    for ts in all_time_stamps:
        cts = time.mktime(ts.timetuple())
        while cts in corrected_time_stamps:
            cts += 1.
        corrected_time_stamps.append(cts)

    time_stamps = [ts - corrected_time_stamps[0] for ts in corrected_time_stamps]

    return time_stamps


def spike_width(waves):
    return np.argmax(waves[:, 10:], axis=1) - np.argmin(waves[:, 10:], axis=1)


class SwanImplementation:

    # noinspection PyArgumentList
    def __init__(self, neodata, parent=None):

        self.blocks = neodata.blocks
        self.parent = parent

        self.feature_dict = {'mean': True,

                             'reduced mean': True,

                             'first derivative': True,
                             'second derivative': True,

                             'p2p amplitude': True,
                             'asymmetry': True,
                             'square sum': True,
                             'spike width': True,

                             'cv2': True,
                             'lv': True,
                             'firing rate': True,

                             'isi': True,
                             'described isi': True,

                             'clusters': 2,

                             'time split': 10
                             }

        self.additional_dict = {'reduced mean dims': 5,
                                'bin max': 15000,
                                'bin step': 60,
                                'max_clusters': 20}

        self.mean_waveforms = get_mean_waveforms(self.blocks)
        self.all_waveforms = get_all_waveforms(self.blocks)
        self.all_spiketrains = get_all_spiketrains(self.blocks)
        self.timestamps = get_time_stamps(self.blocks)
        self.unit_ids = get_real_unit_ids(self.blocks)
        self.session_ids = get_session_ids(self.blocks)

        self.pca = PCA(n_components=self.additional_dict['reduced mean dims'])
        self.pca.fit(np.vstack(self.all_waveforms))
        self.reduced_means = self.pca.transform(self.mean_waveforms)

        QtWidgets.QApplication.restoreOverrideCursor()
        self.feature_dict, solver, okay = ParameterInputDialog(parent=self.parent, algorithm=self).exec_()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        if okay:
            self.feature_vectors = generate_feature_vectors(self, self.feature_dict, self.additional_dict)

            if solver is not None:
                self.solver = solver

                clusters = self.solver.cluster_centers_
                labels = self.solver.predict(self.feature_vectors)
            else:
                self.solver, clusters, labels = run_kmeans_solver(self.feature_vectors,
                                                                  self.feature_dict['clusters'], n_init=100)

            labels = self.remove_duplicates(self.feature_vectors, self.session_ids, self.unit_ids, labels, clusters)

            if self.feature_dict['time split'] is not None:
                labels = self.time_splits(days=self.feature_dict['time split'],
                                          labels=labels, timestamps=self.timestamps)

            self.result = self.generate_result_dataframe(self.session_ids, self.unit_ids, labels)
        else:
            self.result = pd.DataFrame({})

    def time_splits(self, days, labels, timestamps):
        threshold = days * 86400.0

        labels_dict = self.generate_labels_dictionary(labels, timestamps)

        while self.has_time_conflicts(labels_dict, threshold):
            for label in sorted(labels_dict.keys()):
                timestamps = labels_dict[label]
                if timestamps.size > 1:
                    time_diffs = timestamps[1:] - timestamps[:-1]
                    if np.any(time_diffs > threshold):
                        cuts = np.where(time_diffs > threshold)[0]
                        for cut in cuts:
                            max_label = max(labels_dict.keys())
                            labels_dict[max_label + 1] = timestamps[cut + 1:]
                            labels_dict[label] = timestamps[:cut + 1]
                            break
                else:
                    continue
        return self.recreate_labels_list(labels_dict)

    @staticmethod
    def has_time_conflicts(dictionary, threshold):
        for label in dictionary.keys():
            timestamps = dictionary[label]
            if timestamps.size > 1 and np.any((timestamps[1:] - timestamps[:-1]) > threshold):
                return True
        else:
            return False

    @staticmethod
    def recreate_labels_list(dictionary):
        outstamps, outlabels = [], []
        for key in dictionary.keys():
            vals = dictionary[key]
            outstamps.extend(vals.tolist())
            outlabels.extend([key] * vals.size)

        outstamps, outlabels = np.array(outstamps), np.array(outlabels)
        return outlabels[np.argsort(outstamps)].tolist()

    def remove_duplicates(self, feature_vectors, session_ids, unit_ids, labels, clusters):
        def get_duplicates(sessions, units, unit_labels):
            df = pd.DataFrame({
                'session': sessions,
                'unit': units,
                'label': unit_labels
            })

            return df.sort_values(by=['label', 'session']).loc[
                df[['session', 'label']].duplicated(keep=False)
            ]

        duplicates = get_duplicates(session_ids, unit_ids, labels)

        visited = []

        count = 1
        while not duplicates.empty:
            clusters = clusters
            labels = labels

            maximum_distances = self.compute_intracluster_maximum_distance(clusters=clusters,
                                                                           feature_vectors=feature_vectors,
                                                                           labels=labels)
            cross_distances = cdist(feature_vectors, clusters)

            for label in np.unique(duplicates.label):
                cluster_df = duplicates.loc[duplicates.label == label]
                for session in np.unique(cluster_df.session):
                    session_duplicates = cluster_df.loc[cluster_df.session == session]
                    conflicting_unit_distances = cross_distances[session_duplicates.index, label]

                    discard_unit_position = np.argmax(conflicting_unit_distances)
                    discard_unit_id = session_duplicates.unit[session_duplicates.index[discard_unit_position]]

                    visited.append((session, discard_unit_id, label))

                    other_distances = cross_distances[discard_unit_position]
                    differences = other_distances - maximum_distances
                    candidates = []

                    for d, difference in enumerate(differences):
                        if d == label:
                            candidates.append(0.0)
                        elif difference < 0.0:
                            candidates.append(difference)
                        else:
                            candidates.append(0.0)

                    while np.any(np.array(candidates) < 0.0):
                        new_cluster_position = np.argmin(candidates)
                        # noinspection PyTypeChecker
                        candidates[new_cluster_position] = 0.0
                        if (session, discard_unit_id, new_cluster_position) not in visited:
                            labels = self.assign_new_cluster(sessions=session_ids,
                                                             units=unit_ids,
                                                             labels=labels,
                                                             session_id=session,
                                                             unit_id=discard_unit_id,
                                                             new_cluster=new_cluster_position)
                            break
                    else:
                        labels = self.create_new_cluster(sessions=session_ids,
                                                         units=unit_ids,
                                                         labels=labels,
                                                         session_id=session,
                                                         unit_id=discard_unit_id)

                    clusters = self.recompute(feature_vectors, labels)
                    break
                break

            duplicates = get_duplicates(session_ids, unit_ids, labels)
            count += 1

        return labels

    @staticmethod
    def compute_intracluster_maximum_distance(clusters, feature_vectors, labels):
        maximum_distances = []
        for c, center in enumerate(clusters):
            members = feature_vectors[np.where(labels == c)[0]]
            max_dist = 0.0
            for member in members:
                distance = np.linalg.norm(member - center)
                if distance > max_dist:
                    max_dist = distance
            maximum_distances.append(max_dist)

        return np.array(maximum_distances)

    @staticmethod
    def assign_new_cluster(sessions, units, labels, session_id, unit_id, new_cluster):
        pair_list = [(s, u) for s, u in zip(sessions, units)]
        position = [pos for pos, val in enumerate(pair_list) if val == (session_id, unit_id)]

        labels[position] = new_cluster

        return labels

    @staticmethod
    def create_new_cluster(sessions, units, labels, session_id, unit_id):
        pair_list = [(s, u) for s, u in zip(sessions, units)]
        position = [pos for pos, val in enumerate(pair_list) if val == (session_id, unit_id)]

        max_label = np.amax(labels)
        labels[position] = max_label + 1

        return labels

    @staticmethod
    def recompute(feature_vectors, labels):
        cluster_labels = np.unique(labels)
        total_clusters = cluster_labels.size
        label_list = labels

        cluster_centers = np.zeros((total_clusters, feature_vectors.shape[1]))

        for idx, label in enumerate(cluster_labels):
            vectors = feature_vectors[label_list == label]
            cluster_centers[idx] = vectors.mean(axis=0)

        return cluster_centers

    @staticmethod
    def generate_result_dataframe(session_ids, unit_ids, labels):
        dataframe = pd.DataFrame({'session': session_ids,
                                  'unit': unit_ids,
                                  'label': labels
                                  })

        return dataframe.sort_values(by=['session', 'unit'])

    @staticmethod
    def generate_labels_dictionary(labels, timestamps):
        labels = np.array(labels)
        timestamps = np.array(timestamps)

        labels_dict = {}
        for label in np.unique(labels):
            labels_dict[label] = timestamps[np.where(labels == label)[0]]

        return labels_dict


# noinspection PyArgumentList
class ParameterInputDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, algorithm=None):
        # noinspection PyArgumentList
        QtWidgets.QDialog.__init__(self, parent=parent)

        self.setWindowTitle("Automatic algorithm: SWAN Implementation")
        self.algorithm = algorithm

        self.interface = ParameterInputDialogUI(self)
        self.plot_widget = self.interface.elbow_curve_plot.pg_canvas

        self.interface.clusters.textChanged.connect(self.update_plot)

        self._solvers = []
        self._clusters = []
        self._inertias = []
        self.chosen_solver = None

        self.values_dict = {}
        self.final_state = False

        self.spot_size = 10
        self.default_pen = pg.mkPen(color='w',
                                    width=2,
                                    style=QtCore.Qt.DotLine)
        self.default_symbol_pen = pg.mkPen(color='b')
        self.default_brush = pg.mkBrush((0, 255, 0, 128))
        self.default_symbol = 'o'

        self.current_clusters_value = 2

    def on_confirm(self):
        self.final_state = True
        self.accept()

    def on_cancel(self):
        self.final_state = False
        self.reject()

    # @QtCore.pyqtSlot(object, object)
    # def on_plot_clicked(self, data_item, ev):
    #     if ev.button() == 1:
    #         x_pos = ev.pos().x()
    #         closest_val = self._get_closest_val(x_pos)
    #         if closest_val is not None:
    #             self.interface.clusters.setValue(closest_val)
    #
    # @staticmethod
    # def _get_closest_val(input_value):
    #     lower = np.floor(input_value)
    #     lower_diff = input_value - lower
    #     upper = np.ceil(input_value)
    #     upper_diff = upper - input_value
    #
    #     pprint({"lower": lower,
    #             "lower_diff": lower_diff,
    #             "upper": upper,
    #             "upper_diff": upper_diff})
    #
    #     if lower_diff < upper_diff and lower_diff < 0.1:
    #         return lower
    #     elif upper_diff < lower_diff and upper_diff < 0.1:
    #         return upper
    #     else:
    #         return None

    @QtCore.pyqtSlot()
    def update_plot(self):
        clusters = self._clusters
        inertias = self._inertias
        sizes = []
        pens = []
        brushes = []
        symbols = []

        self.current_clusters_value = int(self.interface.clusters.value())

        for cluster in clusters:
            sizes.append(self.spot_size)
            symbols.append(self.default_symbol)
            if cluster == self.current_clusters_value:
                pens.append(pg.mkPen('r'))
                brushes.append(pg.mkBrush((255, 0, 0, 128)))
            else:
                pens.append(self.default_symbol_pen)
                brushes.append(self.default_brush)

        self._plot(clusters, inertias,
                   symbolPen=pens,
                   symbolSize=sizes,
                   symbol=symbols,
                   symbolBrush=brushes,
                   pxMode=True,
                   clear=True)

    def plot(self):
        solvers = []
        clusters = []
        inertias = []

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.update_values_dict()
        feature_vectors = generate_feature_vectors(self.algorithm, self.values_dict, self.algorithm.additional_dict)

        with Pool(processes=None) as pool:
            results = pool.starmap_async(run_kmeans_solver_no_prediction,
                                         [(feature_vectors, n_clusters, 100)
                                          for n_clusters in range(2, feature_vectors.shape[0])])

            for result in results.get():
                solver, n_clusters = result[0], result[1]
                solvers.append(solver)
                clusters.append(n_clusters)
                inertias.append(solver.inertia_)

        self._solvers = solvers
        self._clusters = clusters
        self._inertias = inertias

        self.update_plot()

        QtWidgets.QApplication.restoreOverrideCursor()

    def _plot(self, x, y, *args, **kwargs):
        self.interface.elbow_curve_plot.pg_canvas.clear()
        plot_item = self.interface.elbow_curve_plot.pg_canvas.plot(x, y, *args, **kwargs)
        # plot_item.sigClicked.connect(self.on_plot_clicked)

    def update_values_dict(self):
        output_dict = {}
        for key in self.interface.key_names:
            output_dict[key] = self.interface.checkboxes[key].isChecked()
        output_dict["clusters"] = int(self.interface.clusters.value())
        if self.interface.time_split_box.isChecked():
            output_dict["time split"] = int(self.interface.time_split_threshold.value())
        else:
            output_dict["time split"] = None
        self.values_dict = output_dict

    def exec_(self):
        QtWidgets.QDialog.exec_(self)
        self.update_values_dict()
        if self._solvers is not None:
            self.chosen_solver = self._solvers[self._clusters.index(self.current_clusters_value)]
        return self.values_dict, self.chosen_solver, self.final_state
