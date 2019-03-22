import time
import numpy as np
import pandas as pd
import elephant as el
from scipy import stats
from scipy.spatial.distance import cdist
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from PyQt5 import QtWidgets, QtGui, QtCore

from swan.src.widgets.mypgwidget import PyQtWidget2d


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


def run_kmeans_solver(data, n_clusters, n_init=100):
    solver = KMeans(n_clusters=n_clusters, n_init=n_init, n_jobs=-1)
    solver.fit(data)
    clusters = solver.cluster_centers_
    labels = solver.predict(data)
    return solver, clusters, labels


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
    all_waveforms = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                waves = unit.spiketrains[0].waveforms.magnitude[:, 0, :]
                waves = waves - waves.mean(axis=1, keepdims=True)
                all_waveforms.append(waves)
    return all_waveforms


def get_all_spiketrains(blocks):
    all_spiketrains = []
    for block in blocks:
        units = block.channel_indexes[0].units
        for unit in units:
            if 'noise' not in unit.description.split() and 'unclassified' not in unit.description.split():
                train = unit.spiketrains[0].times.magnitude
                all_spiketrains.append(train)
    return all_spiketrains


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

    return [ts - corrected_time_stamps[0] for ts in corrected_time_stamps]


class SwanImplementation:

    def __init__(self, neodata, parent=None):

        self.blocks = neodata.blocks
        self.parent = parent

        self.feature_dict = {'mean': True,

                             'reduced mean': False,

                             'first derivative': True,
                             'second derivative': True,

                             'waveform features': False,

                             'spiketrain features': True,

                             'histogram': True,
                             'described histogram': False,

                             'clusters': 6,

                             'time split': 10
                             }

        QtGui.QApplication.restoreOverrideCursor()
        self.feature_dict, okay = ParameterInputDialog(parent=self.parent).exec_()
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        self.additional_dict = {'reduced mean dims': 5,
                                'bin max': 15000,
                                'bin step': 60}

        if okay:
            self.mean_waveforms = get_mean_waveforms(self.blocks)
            self.all_waveforms = get_all_waveforms(self.blocks)
            self.all_spiketrains = get_all_spiketrains(self.blocks)
            self.timestamps = get_time_stamps(self.blocks)
            self.unit_ids = get_real_unit_ids(self.blocks)
            self.session_ids = get_session_ids(self.blocks)

            self.pca = PCA(n_components=self.additional_dict['reduced mean dims'])
            self.pca.fit(np.array([np.array(l[0]) for l in self.all_waveforms]))
            self.reduced_means = self.pca.transform(self.mean_waveforms)

            self.feature_vectors = self.generate_feature_vectors()
            # np.random.shuffle(self.feature_vectors.T)

            self.solver, self.clusters, self.labels = run_kmeans_solver(data=self.feature_vectors,
                                                                        n_clusters=self.feature_dict['clusters'])

            self.remove_duplicates()
            if self.feature_dict['time split'] is not None:
                self.time_splits(days=self.feature_dict['time split'])

            self.result = self.generate_result_dataframe()

        else:
            self.result = pd.DataFrame({})

    def time_splits(self, days):
        threshold = days * 86400.0

        print("Threshold", threshold)

        labels_dict = self.generate_labels_dictionary()

        print("Labels dictionary", labels_dict)

        while self.has_time_conflicts(labels_dict, threshold):
            for label in sorted(labels_dict.keys()):
                times = labels_dict[label]
                if times.size > 1:
                    time_diffs = times[1:] - times[:-1]
                    if np.any(time_diffs > threshold):
                        cuts = np.where(time_diffs > threshold)[0]
                        for cut in cuts:
                            max_label = max(labels_dict.keys())
                            labels_dict[max_label + 1] = times[cut + 1:]
                            labels_dict[label] = times[:cut + 1]
                            break
                else:
                    continue

        print("Labels dict after processing", labels_dict)
        self.recreate_labels_list(labels_dict)

    @staticmethod
    def has_time_conflicts(dictionary, threshold):
        for key in dictionary.keys():
            values = dictionary[key]
            if values.size > 1 and np.any((values[1:] - values[:-1]) > threshold):
                return True
        else:
            return False

    def generate_labels_dictionary(self):
        labels = np.array(self.labels)
        timestamps = np.array(self.timestamps)

        print("Timestamps", timestamps)

        labels_dict = {}
        for label in np.unique(labels):
            labels_dict[label] = timestamps[np.where(labels == label)[0]]

        return labels_dict

    def recreate_labels_list(self, dictionary):
        outstamps, outlabels = [], []
        for key in dictionary.keys():
            vals = dictionary[key]
            outstamps.extend(vals.tolist())
            outlabels.extend([key] * vals.size)

        outstamps, outlabels = np.array(outstamps), np.array(outlabels)

        print("Outstamps", outstamps)
        print("Outlabels", outlabels)

        self.labels = outlabels[np.argsort(outstamps)].tolist()

    def remove_duplicates(self):
        def get_duplicates(session_ids, unit_ids, unit_labels):
            df = pd.DataFrame({
                'session': session_ids,
                'unit': unit_ids,
                'label': unit_labels
            })

            return df.sort_values(by=['label', 'session']).loc[
                df[['session', 'label']].duplicated(keep=False)
            ]

        feature_vectors = self.feature_vectors

        duplicates = get_duplicates(self.session_ids, self.unit_ids, self.labels)

        visited = []

        count = 1
        while not duplicates.empty:
            print("Loop {count}".format(count=count))
            clusters = self.clusters
            labels = self.labels

            maximum_distances = self.compute_intracluster_maximum_distance(clusters=clusters,
                                                                           feature_vectors=feature_vectors,
                                                                           labels=labels)
            cross_distances = cdist(feature_vectors, clusters)

            for label in np.unique(duplicates.label):
                print("Label (cluster): {label}".format(label=label))
                cluster_df = duplicates.loc[duplicates.label == label]
                for session in np.unique(cluster_df.session):
                    print("Session: {s}".format(s=session))
                    session_duplicates = cluster_df.loc[cluster_df.session == session]
                    conflicting_unit_distances = cross_distances[session_duplicates.index, label]

                    discard_unit_position = np.argmax(conflicting_unit_distances)
                    discard_unit_id = session_duplicates.unit[session_duplicates.index[discard_unit_position]]

                    visited.append((session, discard_unit_id, label))

                    other_distances = cross_distances[discard_unit_position]
                    differences = other_distances - maximum_distances
                    print("Distance of unit to other clusters: {d}".format(d=other_distances))
                    print("Intracluster maximum distances: {d}".format(d=maximum_distances))
                    print("Differences: {d}".format(d=differences))
                    candidates = []

                    for d, difference in enumerate(differences):
                        if d == label:
                            candidates.append(0.0)
                        elif difference < 0.0:
                            candidates.append(difference)
                        else:
                            candidates.append(0.0)

                    print("Candidates: {c}".format(c=candidates))

                    while np.any(np.array(candidates) < 0.0):
                        new_cluster_position = np.argmin(candidates)
                        candidates[new_cluster_position] = 0.0
                        if (session, discard_unit_id, new_cluster_position) not in visited:
                            self.assign_new_cluster(session_id=session,
                                                    unit_id=discard_unit_id,
                                                    new_cluster=new_cluster_position)
                            print("New cluster assigned: {s}, {u}, {l}".format(s=session,
                                                                               u=discard_unit_id,
                                                                               l=new_cluster_position))
                            break
                    else:
                        self.create_new_cluster(session_id=session,
                                                unit_id=discard_unit_id)
                        print("New cluster created: {s}, {u}".format(s=session,
                                                                     u=discard_unit_id))

                    self.recompute()
                    break
                break

            duplicates = get_duplicates(self.session_ids, self.unit_ids, self.labels)
            count += 1
            print("")

    def assign_new_cluster(self, session_id, unit_id, new_cluster):
        pair_list = [(s, u) for s, u in zip(self.session_ids, self.unit_ids)]
        position = [pos for pos, val in enumerate(pair_list) if val == (session_id, unit_id)]

        self.labels[position] = new_cluster

    def create_new_cluster(self, session_id, unit_id):
        pair_list = [(s, u) for s, u in zip(self.session_ids, self.unit_ids)]
        position = [pos for pos, val in enumerate(pair_list) if val == (session_id, unit_id)]

        max_label = np.amax(self.labels)
        self.labels[position] = max_label + 1

    def recompute(self):
        cluster_labels = np.unique(self.labels)
        total_clusters = cluster_labels.size
        label_list = self.labels

        cluster_centers = np.zeros((total_clusters, self.feature_vectors.shape[1]))

        for l, label in enumerate(cluster_labels):
            vectors = self.feature_vectors[label_list == label]
            cluster_centers[l] = vectors.mean(axis=0)

        self.clusters = cluster_centers

    def generate_result_dataframe(self):
        dataframe = pd.DataFrame({'session': self.session_ids,
                                  'unit': self.unit_ids,
                                  'label': self.labels
                                  })

        return dataframe.sort_values(by=['session', 'unit'])

    def generate_feature_vectors(self):
        feature_vectors = []

        for u, (waves, train, reduced_mean, mean) in \
                enumerate(zip(self.all_waveforms, self.all_spiketrains, self.reduced_means, self.mean_waveforms)):
            feature_vectors.append([])
            if self.feature_dict['waveform features']:
                for wave_method in [p2p_amplitude, asymmetry, square_sum]:
                    feature_vectors[u].extend(list(stats.describe(wave_method(waves)))[2:])
            if self.feature_dict['spiketrain features']:
                for train_method in [cv2, lv, fr]:
                    feature_vectors[u].append(train_method(train))
            if self.feature_dict['mean']:
                feature_vectors[u].extend(mean)
            if self.feature_dict['reduced mean']:
                feature_vectors[u].extend(reduced_mean)
            if self.feature_dict['first derivative']:
                feature_vectors[u].extend(diff(waves))
            if self.feature_dict['second derivative']:
                feature_vectors[u].extend(diffdiff(waves))
            if self.feature_dict['described histogram']:
                feature_vectors[u].extend(list(stats.describe(isih(train,
                                                                   self.additional_dict['bin max'],
                                                                   self.additional_dict['bin step']
                                                                   )
                                                              )
                                               )[2:]
                                          )
            if self.feature_dict['histogram']:
                feature_vectors[u].extend(isih(train,
                                               self.additional_dict['bin max'],
                                               self.additional_dict['bin step']
                                               )
                                          )

        feature_vectors = np.array(feature_vectors)
        feature_vectors = (feature_vectors - feature_vectors.mean(axis=0, keepdims=True)) / feature_vectors.std(axis=0)

        return np.nan_to_num(feature_vectors)

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


class ParameterInputDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)

        self.main_layout = QtGui.QGridLayout()

        plot_height = 0

        # self.plot = PyQtWidget2d(parent=self)
        # radio_buttons = ['auto update', 'manual update']
        # self.plot.toolbar.setupRadioButtons(radio_buttons)
        # self.main_layout.addWidget(self.plot, 0, 0, plot_height, 3)

        self.checkbox_text = ["Mean", "Reduced Mean", "First Derivative", "Second Derivative", "Waveform Features",
                              "Spiketrain Features", "Inter-spike Interval Histogram", "Reduced ISI Histogram"]
        self.key_names = ["mean", "reduced mean", "first derivative", "second derivative", "waveform features",
                          "spiketrain features", "histogram", "described histogram"]
        default_states = [True, False, True, True, False, True, True, False]

        self.option_choice = QtGui.QGroupBox("Choose features for KMeans clustering")
        self.option_layout = QtGui.QVBoxLayout()

        horizontal_layout = QtGui.QHBoxLayout()
        self.clusters = QtGui.QSpinBox()
        self.clusters.setRange(0, 10)
        clusters_label = QtGui.QLabel("Number of initial clusters:")
        horizontal_layout.addWidget(clusters_label)
        horizontal_layout.addWidget(self.clusters)
        self.option_layout.addLayout(horizontal_layout)

        self.checkboxes = {}
        for c, (text, key, val) in enumerate(zip(self.checkbox_text, self.key_names, default_states)):
            checkbox = QtGui.QCheckBox(text)
            state = QtCore.Qt.Checked if val else QtCore.Qt.Unchecked
            checkbox.setCheckState(state)
            self.option_layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox

        self.option_choice.setLayout(self.option_layout)

        self.main_layout.addWidget(self.option_choice, plot_height, 0, len(self.checkbox_text), 3)

        offset_height = plot_height + len(self.checkbox_text)

        self.form_layout = QtGui.QFormLayout()

        self.time_split_box = QtGui.QGroupBox("Cluster Curation: Time split")
        self.time_split_box.setCheckable(True)
        time_split_layout = QtGui.QVBoxLayout()

        vertical_layout = QtGui.QVBoxLayout()
        self.time_split_threshold = QtGui.QSpinBox()
        self.time_split_threshold.setRange(0, 1000)
        info_label = QtGui.QLabel("Split clusters if the contained units differ in "
                                  "time more than a specified threshold.")
        time_split_label = QtGui.QLabel("Time split threshold (in days):")
        vertical_layout.addWidget(info_label)
        horizontal_layout = QtGui.QHBoxLayout()
        horizontal_layout.addWidget(time_split_label)
        horizontal_layout.addWidget(self.time_split_threshold)
        vertical_layout.addLayout(horizontal_layout)
        time_split_layout.addLayout(vertical_layout)

        self.time_split_box.setLayout(time_split_layout)

        self.main_layout.addWidget(self.time_split_box, offset_height + 1, 0, 1, 3)

        self.main_layout.addLayout(self.form_layout, offset_height + 2, 0)

        # self.update_plot_button = QtGui.QPushButton("Update Elbow Curve")
        # self.main_layout.addWidget(self.update_plot_button, offset_height + 2, 2, 1, 1)
        # self.update_plot_button.clicked.connect(self.update_plot)

        self.confirm_button = QtGui.QPushButton("Calculate")
        self.main_layout.addWidget(self.confirm_button, offset_height + 3, 2, 1, 1)
        self.confirm_button.clicked.connect(self.on_confirm)

        self.cancel_button = QtGui.QPushButton("Cancel")
        self.main_layout.addWidget(self.cancel_button, offset_height + 3, 0, 1, 1)
        self.cancel_button.clicked.connect(self.on_cancel)

        self.setLayout(self.main_layout)

        self.values_dict = {}
        self.final_state = False

    def on_confirm(self):
        self.final_state = True
        self.accept()

    def on_cancel(self):
        self.final_state = False
        self.reject()

    def update_plot(self):
        pass

    def update_values_dict(self):
        output_dict = {}
        for key in self.key_names:
            output_dict[key] = self.checkboxes[key].isChecked()
        output_dict["clusters"] = int(self.clusters.value())
        if self.time_split_box.isChecked():
            output_dict["time split"] = int(self.time_split_threshold.value())
        else:
            output_dict["time split"] = None
        self.values_dict = output_dict

    def exec_(self):
        QtWidgets.QDialog.exec_(self)
        self.update_values_dict()
        return self.values_dict, self.final_state
