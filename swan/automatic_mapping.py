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
        units = block.channel_indexes[0].units
        for u, unit in enumerate(units):
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                session_ids.append(b)

    return session_ids


def get_real_unit_ids(blocks):
    unit_ids = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for u, unit in enumerate(units):
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                unit_ids.append(u)

    return unit_ids


def get_mean_waveforms(blocks):
    mean_waveforms = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                waves = unit.spiketrains[0].waveforms.magnitude[:, 0, :]
                waves = waves - waves.mean(axis=1, keepdims=True)
                mean_waveforms.append(waves.mean(axis=0))

    return mean_waveforms


def get_all_waveforms(blocks):
    waveforms = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                waves = unit.spiketrains[0].waveforms.magnitude[:, 0, :]
                waves = waves - waves.mean(axis=1, keepdims=True)
                waveforms.append(waves)
    return waveforms


def get_all_spiketrains(blocks):
    spiketrains = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                train = unit.spiketrains[0].times.magnitude
                spiketrains.append(train)
    return spiketrains


def get_time_stamps(blocks):
    all_time_stamps = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
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


def calculate_mapping_bu(virtual_unit_map, data, storage):
    """
    Calculates a mapping for the units based on features like distance.

    The units will be compared pare-wise and sequential.

    **Arguments**

        *data* (:class:`src.neodata.NeoData`):
            This object is needed to get the data
            which will be used to compare the units.

    """
    wave_length = data.get_wave_length()

    for i in range(len(data.blocks) - 1):
        sessions = np.zeros((sum(data.total_units_per_block), 2, wave_length))

        for j, val in enumerate(storage.get_map().mapping[i]):
            if val != 0:
                runit = virtual_unit_map.get_realunit(i, j, data)
                avg = data.get_data("average", runit)
                sessions[j][0] = avg / np.max(avg)
            else:
                sessions[j][0] = np.zeros(wave_length)

        for j, val in enumerate(storage.get_map().mapping[i + 1]):
            if val != 0:
                runit = virtual_unit_map.get_realunit(i + 1, j, data)
                avg = data.get_data("average", runit)
                sessions[j][1] = avg / np.max(avg)
            else:
                sessions[j][1] = np.zeros(wave_length)

        distances = cdist(sessions[:, 0], sessions[:, 1], metric='euclidean')
        threshold = np.mean(distances[distances > 0])
        print(threshold)
        extend = 0
        exclude = []
        for j, val in enumerate(storage.get_map().mapping[i + 1]):
            # print("Executing this in session {}".format(i))
            # print("J: {}, Val: {}".format(j, val))

            if val != 0:
                print(distances[j])

                min_arg = np.argmin(distances[j])
                # print("Min Arg: {}".format(min_arg))

                if min_arg == j:
                    pass
                elif distances[j, min_arg] < threshold and (j, min_arg) not in exclude:
                    # print("Swapping {} and {}".format(j, min_arg))
                    virtual_unit_map.swap(i + 1, j, min_arg)
                    exclude.append((j, min_arg))
                    exclude.append((min_arg, j))
                elif distances[j, min_arg] >= threshold:
                    # print("Swapping {} and {}".format(j, data.total_units_per_block[i + 1] + extend))
                    virtual_unit_map.swap(i + 1, j, data.total_units_per_block[i + 1] + extend)
                    extend += 1
                    print(extend)
                else:
                    print("Logic flawed, check again!")
        print(exclude)
    storage.change_map()


def swan_implementation(virtual_unit_map, data, storage):
    swaps = 0
    # Retrieve mapping from base
    backup_mapping = np.array(storage.get_map().mapping.copy()).T
    pre_mapping = backup_mapping.copy()
    # loop over columns/sessions
    for s in range(pre_mapping.shape[1]):
        # initialize array of mean waveform max amplitudes
        averages = np.zeros((pre_mapping.shape[0]))

        # loop over rows/units
        for j in range(len(averages)):
            # ignore zeros in the map (correspond to non-existent units)
            if pre_mapping[j][s] != 0:
                # Retrieve unit
                runit = virtual_unit_map.get_realunit(s, j, data)
                # Retrieve mean waveform for the unit
                wave = data.get_data("average", runit)
                # Store max amplitude of mean waveform
                averages[j] = np.amax(np.abs(wave))

        #
        # Sort the units in each session by max amplitude of mean waveform
        # and swap the corresponding units in the base.
        #

        # loop over rows/units
        for i in range(len(averages)):
            # retrieve index of max value in session
            max_index = np.argmax(averages[i:]) + i
            if max_index != i:
                virtual_unit_map.swap(s, i, max_index)
                tmp = averages[max_index]
                averages[max_index] = averages[i]
                averages[i] = tmp
                swaps += 1

    storage.change_map()
    # Refresh the mapping using the values in base
    mapping = np.array(storage.get_map().mapping.copy()).T

    # Initialize an array shaped like "mapping" and set all values to np.nan
    history = np.zeros_like(mapping, dtype=np.float)
    history[history == 0.0] = None
    # print("Initial Mapping: {}".format(mapping))

    # Loop over all columns/sessions except the last one
    for i in range(mapping.shape[1] - 1):
        # Loop over all rows/units
        # print("\nFirst loop: {}".format(i))
        for j in range(mapping.shape[0]):
            # ignore zeros in the map (correspond to non-existent units)
            # print("\tSecond Loop: {}".format(j))
            if mapping[j][i] > 0:  # to avoid errors in float comparison
                # Choose (j, i)th unit as the actor and obtain it's mean waveform
                runit_actor = virtual_unit_map.get_realunit(i, j, data)
                actor_wave = data.get_data("average", runit_actor)
                actor_rp = data.get_data("rate profile", runit_actor)

                # Initialize matrix to store distances to the actor unit
                distances_waves = np.zeros((mapping.shape[0], mapping.shape[1]))
                distances_rp = np.zeros((mapping.shape[0], mapping.shape[1]))

                # Loop over all columns/sessions again
                for k in range(mapping.shape[1]):
                    # Loop over all rows/units again
                    # print("\t\tThird Loop: {}".format(k))
                    for l in range(mapping.shape[0]):
                        if mapping[l][k] > 0:
                            # Choose (l, k)th units as the support and obtain it's mean waveform
                            # print("\t\t\tFourth Loop {}\n".format(l))
                            runit_support = virtual_unit_map.get_realunit(k, l, data)
                            support_wave = data.get_data("average", runit_support)
                            support_rp = data.get_data("rate profile", runit_support)
                            #
                            # Calculate and store the Euclidean distance to
                            # support from actor (multiplied by a distance
                            # factor)
                            #
                            distances_waves[l][k] = np.linalg.norm(
                                np.subtract(actor_wave, support_wave))  # * np.exp(abs(k-i))
                            distances_rp[l][k] = np.linalg.norm(np.subtract(actor_rp, support_rp))
                #                            if mapping[l][k] > 0:
                #                                history[l][k] = distances[l][k]

                # print("Distances:\n {}\n".format(distances))

                #
                # Extract the dataset corresponding to all distance measures
                # with non-zero mapping values and calculate the reject threshold
                #

                distances = distances_waves  # + distances_rp

                threshold_dataset = distances[mapping > 0]
                dataset_reject_threshold = np.mean(threshold_dataset)
                # dataset_std = np.std(threshold_dataset)
                # threshold_range_L = threshold_mean + 0.5 * threshold_std
                # dataset_reject_threshold = dataset_mean + 0.5 * dataset_std

                # print("Threshold: {}\n".format(dataset_reject_threshold))

                #
                # The following loop is the main part of the mapping algorithm,
                # which uses the distances between units to rearrange (swap) them.
                #

                # Generate loop range for the loop
                if mapping.shape[1] < 10:
                    loop_range = range(mapping.shape[1])
                else:
                    loop_range = [x for x in range(i + 9) if (i + x) <= mapping.shape[1]]

                # Start looping over sessions/columns
                for k in loop_range:
                    # Find the argument of the minimum in the kth column
                    min_arg = np.argmin(distances[:, k])
                    # print("i: {}, j: {}, k: {}, min_arg: {}\n".format(i, j, k, min_arg))
                    if min_arg == j:
                        # Do nothing if the minimum argument is the same as the row we're looping over
                        pass
                    elif distances[min_arg][k] <= dataset_reject_threshold:
                        # If the distance between the two waveforms falls within
                        # the threshold, we swap the two positions in the kth col
                        if np.isnan(history[min_arg][k]):
                            # If the unit has not been swapped earlier.
                            history[j][k] = distances[min_arg][k]
                            virtual_unit_map.swap(k, min_arg, j)
                            # mapping = backup_mapping.copy()
                            swaps += 1
                        else:
                            # If the unit has been swapped earlier, swap only if
                            # the new distance is less than the old distance
                            prev_dist = history[min_arg][k]
                            curr_dist = distances[min_arg][k]
                            if curr_dist < prev_dist:
                                history[j][k] = distances[min_arg][k]
                                virtual_unit_map.swap(k, min_arg, j)
                                # mapping = backup_mapping.copy()
                                swaps += 1
                    elif distances[min_arg][k] > dataset_reject_threshold:
                        # If the distance between the two waveforms is greater than
                        # the threshold, move the unit to the first available free
                        # plot
                        loc = 0
                        first_zero = np.where(mapping[:, k] == 0)[0][loc]

                        try:
                            while np.sum(mapping[first_zero]) > 0.5:
                                loc += 1
                                first_zero = np.where(mapping[:, k] == 0)[0][loc]
                        except IndexError:
                            first_zero = 0
                        virtual_unit_map.swap(k, first_zero, min_arg)
                        history[min_arg][k] = np.nan
                        mapping = backup_mapping.copy()
                        swaps += 1
                        # print("Swapped {} with empty plot {} on day {}".format(min_arg, first_zero, k))
                        # print("Mapping: {}".format(mapping))
                    else:
                        # If none of the above cases yield true, something is wrong
                        print("Exception reached")
                        print(distances_waves)
                        print(distances_rp)
                        print(distances)
                        mapping = backup_mapping.copy()
    storage.change_map()
    # print("Total swaps: {}\n".format(swaps))


"""
def calculate_mapping(self, data, base):

    Calculates a mapping for the units based on features like distance.

    The units will be compared pare-wise and sequential.

    **Arguments**

        *data* (:class:`src.neodata.NeoData`):
            This object is needed to get the data 
            which will be used to compare the units.


    print("Map being calculated")
    #dis = {}
    #for each block except the last one
    for i in range(len(data.blocks) - 1):
        swapped1 = []
        swapped2 = []

        #do it so often that each real unit can find a partner
        for n in range(data.total_units_per_block[i]):
            distances = []

            #for each unit in block i
            for j in range(self.maximum_units):
                if self.mapping[i][j] != 0:
                    unit1 = self.get_realunit(i, j, data)
                    y1 = data.get_data("average", unit1)[0]

                    #for each unit in block i+1
                    for k in range(self.maximum_units):
                        if self.mapping[i+1][k] != 0:
                            unit2 = self.get_realunit(i+1, k, data)
                            y2 = data.get_data("average", unit2)[0]
                            #calculates the distance between the average waveforms
                            distance = np.linalg.norm(np.subtract(y2, y1))

                            #calculate cross correlation {
                            #calculates the inter-spike-interval
                            isi1 = data.get_data("units", unit1)[0]
                            isi2 = data.get_data("units", unit2)[0]
                            len1 = len(isi1)
                            len2 = len(isi2)
                            if len1 > len2:
                                isi1 = isi1[:len2]
                            else:
                                isi2 = isi2[:len1]
                            cor1 = np.corrcoef(y1, y2)
                            cor2 = np.corrcoef(isi1, isi2)
                            c = ((cor1 + cor2) / 2.0)[1][0]
                            #print("unit {} vs. unit {} = {}, crosscorr = {}".format(j, k, distance, c))
                            # }

                            #calculate norm {
                            y = y1 + y2
                            isi = isi1 + isi2
                            av1 = np.mean(y)
                            std1 = np.std(y)
                            av2 = np.mean(isi)
                            std2 = np.std(isi)
                            yn1 = (y1 - av1) / std1
                            yn2 = (y2 - av1) / std1
                            isin1 = (isi1 - av2) / std2
                            isin2 = (isi2 - av2) / std2
                            #fig = plt.figure("dist: {}; corr: {}".format(distance, c))
                            #fig.add_subplot(111)
                            #plt.plot(yn1)
                            #plt.plot(yn2)
                            #plt.plot(isin1)
                            #plt.plot(isin2)
                            #plt.show()
                            #print("unit {} vs. unit {} = {}, y = {} {}, isi = {} {}".format(j, k, distance,
                            #                                                                yn1[:2], yn2[:2],
                            #                                                                isin1[:2], isin2[:2]))
                            #  }

                            if j not in swapped1 and k not in swapped2:
                                distances.append((j, k, distance))
                                #dis[c] = distance
            if distances:
                #finds the min of the distances
                mini = min(distances, key=lambda x: x[2])
                #swap only if distance is under a threshold
                if mini[2] < 200:
                    #swaps the units to have them in the same unit row                
                    self.swap(i+1, mini[0], mini[1])
                    swapped1.append(mini[0])
                    swapped2.append(mini[0])
                #otherwise search for an empty row and swap there
                #but only if the units are in the same row 
                else:
                    if mini[0] == mini[1]:
                        for u, v in enumerate(self.mapping[i+1]):
                            testing = True
                            for l in range(i+2):
                                if self.mapping[l][u] != 0:
                                    testing = False
                            if testing:
                                self.swap(i+1, mini[1], u)
                                swapped1.append(mini[0])
                                swapped2.append(u)

    #plt.plot(dis.keys(), dis.values(), "o")
    #plt.show()
"""
