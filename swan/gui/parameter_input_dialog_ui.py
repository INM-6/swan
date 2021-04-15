from PyQt5 import QtWidgets, QtCore
from swan.widgets.mypgwidget import PyQtWidget2d


class ParameterInputDialogUI(object):

    def __init__(self, parent_dialog):

        self.main_layout = QtWidgets.QGridLayout()

        plot_height = 2

        self.plot_box = QtWidgets.QGroupBox("Choose point corresponding to optimal number of clusters:")
        self.plot_box_layout = QtWidgets.QHBoxLayout()

        self.elbow_curve_plot = PyQtWidget2d(parent=parent_dialog)
        self.elbow_curve_plot.set_x_label("Number of Clusters")
        self.elbow_curve_plot.set_y_label("Sum of Squared Errors (SSE)")
        self.elbow_curve_plot.show_grid()
        self.plot_box_layout.addWidget(self.elbow_curve_plot)
        self.elbow_curve_plot.toolbar.collapsible_widget.setParent(None)
        self.elbow_curve_plot.toolbar.setParent(None)

        self.plot_box.setLayout(self.plot_box_layout)
        self.main_layout.addWidget(self.plot_box, 0, 0, 2, 4)

        self.checkboxes = {}
        self.key_names = []

        self.option_choice = QtWidgets.QGroupBox("Choose features for KMeans clustering")
        self.option_layout = QtWidgets.QVBoxLayout()

        horizontal_layout = QtWidgets.QHBoxLayout()
        self.clusters = QtWidgets.QSpinBox()
        self.clusters.setRange(0, parent_dialog.algorithm.additional_dict['max_clusters'])
        self.clusters.setValue(parent_dialog.algorithm.feature_dict['clusters'])
        clusters_label = QtWidgets.QLabel("Number of initial clusters:")
        horizontal_layout.addWidget(clusters_label)
        horizontal_layout.addWidget(self.clusters)
        self.option_layout.addLayout(horizontal_layout)

        self.mean_waveforms_choice = QtWidgets.QGroupBox("Mean Waveforms")
        self.mean_waveforms_layout = QtWidgets.QHBoxLayout()

        checkbox_text = ["Mean", "Reduced Mean", "First Derivative", "Second Derivative"]
        key_names = ["mean", "reduced mean", "first derivative", "second derivative"]
        default_states = [True, True, True, True]

        self.add_checkbox_group(checkbox_text, key_names, default_states, self.mean_waveforms_layout)

        self.mean_waveforms_choice.setLayout(self.mean_waveforms_layout)
        self.option_layout.addWidget(self.mean_waveforms_choice)

        self.waveform_features_choice = QtWidgets.QGroupBox("Waveform Features")
        self.waveform_features_layout = QtWidgets.QHBoxLayout()

        checkbox_text = ["Peak-to-peak Amplitude", "Waveform Asymmetry", "Square Sum", "Spike Width"]
        key_names = ["p2p amplitude", "asymmetry", "square sum", "spike width"]
        default_states = [True, True, True, True]

        self.add_checkbox_group(checkbox_text, key_names, default_states, self.waveform_features_layout)

        self.waveform_features_choice.setLayout(self.waveform_features_layout)
        self.option_layout.addWidget(self.waveform_features_choice)

        self.spiketrain_features_choice = QtWidgets.QGroupBox("Spiketrain Features")
        self.spiketrain_features_layout = QtWidgets.QHBoxLayout()

        checkbox_text = ["Coefficient of Variation (CV2)", "Local Coefficient of Variation (LV)", "Firing Rate"]
        key_names = ["cv2", "lv", "firing rate"]
        default_states = [True, True, True]

        self.add_checkbox_group(checkbox_text, key_names, default_states, self.spiketrain_features_layout)

        self.spiketrain_features_choice.setLayout(self.spiketrain_features_layout)
        self.option_layout.addWidget(self.spiketrain_features_choice)

        self.isi_histograms_choice = QtWidgets.QGroupBox("ISI Histograms")
        self.isi_histograms_layout = QtWidgets.QHBoxLayout()

        checkbox_text = ["Inter-spike Interval Histogram", "Described ISI Histogram"]
        key_names = ["isi", "described isi"]
        default_states = [True, True]

        self.add_checkbox_group(checkbox_text, key_names, default_states, self.isi_histograms_layout)

        self.isi_histograms_choice.setLayout(self.isi_histograms_layout)
        self.option_layout.addWidget(self.isi_histograms_choice)

        self.option_choice.setLayout(self.option_layout)

        self.main_layout.addWidget(self.option_choice, plot_height, 0, 4, 4)

        offset_height = plot_height + 4

        self.form_layout = QtWidgets.QFormLayout()

        self.time_split_box = QtWidgets.QGroupBox("Cluster Curation: Time split")
        self.time_split_box.setCheckable(True)
        time_split_layout = QtWidgets.QVBoxLayout()

        vertical_layout = QtWidgets.QVBoxLayout()
        self.time_split_threshold = QtWidgets.QSpinBox()
        self.time_split_threshold.setRange(0, 1000)
        self.time_split_threshold.setValue(parent_dialog.algorithm.feature_dict['time split'])
        info_label = QtWidgets.QLabel("Split clusters if the contained units differ in "
                                      "time more than a specified threshold.")
        time_split_label = QtWidgets.QLabel("Time split threshold (in days):")
        vertical_layout.addWidget(info_label)
        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.addWidget(time_split_label)
        horizontal_layout.addWidget(self.time_split_threshold)
        vertical_layout.addLayout(horizontal_layout)
        time_split_layout.addLayout(vertical_layout)

        self.time_split_box.setLayout(time_split_layout)

        self.main_layout.addWidget(self.time_split_box, offset_height + 1, 0, 1, 4)

        self.main_layout.addLayout(self.form_layout, offset_height + 2, 0)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.main_layout.addWidget(self.cancel_button, offset_height + 3, 0, 1, 1)
        self.cancel_button.clicked.connect(parent_dialog.on_cancel)

        self.update_plot_button = QtWidgets.QPushButton("Update Plot")
        self.main_layout.addWidget(self.update_plot_button, offset_height + 3, 2, 1, 1)
        self.update_plot_button.clicked.connect(parent_dialog.plot)

        self.confirm_button = QtWidgets.QPushButton("Calculate")
        self.main_layout.addWidget(self.confirm_button, offset_height + 3, 3, 1, 1)
        self.confirm_button.clicked.connect(parent_dialog.on_confirm)

        parent_dialog.setLayout(self.main_layout)

    def add_checkbox_group(self, texts, keys, default_states, layout):
        for c, (text, key, val) in enumerate(zip(texts, keys, default_states)):
            checkbox = QtWidgets.QCheckBox(text)
            state = QtCore.Qt.Checked if val else QtCore.Qt.Unchecked
            checkbox.setCheckState(state)
            layout.addWidget(checkbox)
            self.key_names.append(key)
            self.checkboxes[key] = checkbox