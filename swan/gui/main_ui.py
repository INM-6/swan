#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 23:26:08 2017

@author: Shashwat Sridhar
"""
# system imports
from PyQt5 import QtCore, QtGui
from os import sep

# swan-specific imports
from swan.res import icons
from swan.src.views.mean_waveforms_view import pgWidget2d
from swan.src.widgets.myplotgrid import MyPlotGrid
from swan.src.views.isi_histograms_view import pgWidgetISI
from swan.src.views.pca_3d_view import pgWidgetPCA
from swan.src.views.waveforms_3d_view import pgWidget3d
from swan.src.views.pca_2d_view import pgWidgetPCA2d
from swan.src.views.rate_profile_view import pgWidgetRateProfile
from swan.src.widgets.plotgridtools import plotGridTools
from swan.src.widgets.viewtoolbar import collapsibleWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _from_utf_8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class MainUI(object):
    def __init__(self, main_application):
        main_application.setObjectName(_from_utf_8("Main"))

        main_application.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks |
                                        QtGui.QMainWindow.AllowNestedDocks |
                                        QtGui.QMainWindow.GroupedDragging)

        self.plotGridDock = QtGui.QDockWidget("Plot Grid")
        self.plotGridDock.setObjectName(_from_utf_8("PlotGridDock"))
        self.plotGrid = MyPlotGrid(main_application)
        self.plotGridDock.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                      QtGui.QDockWidget.DockWidgetFloatable)
        self.plotGridDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.plotGridDock.setWidget(self.plotGrid)
        main_application.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.plotGridDock, QtCore.Qt.Vertical)

        self.dock_mean_waveforms_view = QtGui.QDockWidget("Mean Waveforms")
        self.dock_mean_waveforms_view.setObjectName(_from_utf_8("meanWaveformView"))
        self.dock_mean_waveforms_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                  QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_mean_waveforms_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_mean_waveforms_view, QtCore.Qt.Vertical)

        self.mean_waveforms_view = pgWidget2d()
        self.mean_waveforms_view.setObjectName(_from_utf_8("meanWaveformsView"))

        self.dock_mean_waveforms_view.setWidget(self.mean_waveforms_view)

        self.dock_waveforms_3d_view = QtGui.QDockWidget("3D Waveforms")
        self.dock_waveforms_3d_view.setObjectName(_from_utf_8("3dWaveformView"))
        self.dock_waveforms_3d_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_waveforms_3d_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_waveforms_3d_view, QtCore.Qt.Vertical)

        self.waveforms_3d_view = pgWidget3d()
        self.waveforms_3d_view.setObjectName(_from_utf_8("3dWaveformsView"))

        self.dock_waveforms_3d_view.setWidget(self.waveforms_3d_view)

        self.dock_isi_histograms_view = QtGui.QDockWidget("ISI Histograms")
        self.dock_isi_histograms_view.setObjectName(_from_utf_8("ISIHView"))
        self.dock_isi_histograms_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                  QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_isi_histograms_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_isi_histograms_view, QtCore.Qt.Vertical)

        self.isi_histograms_view = pgWidgetISI()
        self.isi_histograms_view.setObjectName(_from_utf_8("IsihView"))

        self.dock_isi_histograms_view.setWidget(self.isi_histograms_view)

        self.dock_pca_3d_view = QtGui.QDockWidget("Principal Component Analysis")
        self.dock_pca_3d_view.setObjectName(_from_utf_8("PCAView"))
        self.dock_pca_3d_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                          QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_pca_3d_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_pca_3d_view, QtCore.Qt.Vertical)

        self.pca_3d_view = pgWidgetPCA()
        self.pca_3d_view.setObjectName(_from_utf_8("PcaView"))

        self.dock_pca_3d_view.setWidget(self.pca_3d_view)

        self.dock_raster_plots_view = QtGui.QDockWidget("Raster Plots")
        self.dock_raster_plots_view.setObjectName(_from_utf_8("RasterPlotView"))
        self.dock_raster_plots_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_raster_plots_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_raster_plots_view, QtCore.Qt.Vertical)

        self.raster_plots_view = pgWidgetPCA2d()
        self.raster_plots_view.setObjectName(_from_utf_8("RasterView"))

        self.dock_raster_plots_view.setWidget(self.raster_plots_view)

        self.dock_rate_profiles_view = QtGui.QDockWidget("Rate Profiles")
        self.dock_rate_profiles_view.setObjectName(_from_utf_8("RateProfiles"))
        self.dock_rate_profiles_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                 QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_rate_profiles_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        main_application.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_rate_profiles_view, QtCore.Qt.Vertical)

        self.rate_profiles_view = pgWidgetRateProfile()
        self.rate_profiles_view.setObjectName(_from_utf_8("RateProfileView"))

        self.dock_rate_profiles_view.setWidget(self.rate_profiles_view)

        self.tools = plotGridTools()

        self.plotGridOptionsLayout = QtGui.QGridLayout()
        self.plotGridOptionsLayout.setObjectName(_from_utf_8("PlotGridOptionsLayout"))

        self.plotGridOptionsLayout.addWidget(self.tools)
        self.plotGridOptions = collapsibleWidget(parent=self.plotGrid, title="Options", animationDuration=400)
        self.plotGridOptions.setContentLayout(self.plotGridOptionsLayout)

        self.plotGrid.mainGridLayout.addWidget(self.plotGridOptions, 1, 0)
        self.plotGrid.mainGridLayout.setRowStretch(0, 10)

        self.menubar = QtGui.QMenuBar(main_application)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1159, 25))
        self.menubar.setObjectName(_from_utf_8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_from_utf_8("menu_File"))
        self.menu_Edit = QtGui.QMenu(self.menubar)
        self.menu_Edit.setObjectName(_from_utf_8("menu_Edit"))
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName(_from_utf_8("menu_Help"))
        self.menu_View = QtGui.QMenu(self.menubar)
        self.menu_View.setObjectName(_from_utf_8("menu_View"))
        main_application.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(main_application)
        self.statusbar.setObjectName(_from_utf_8("statusbar"))
        main_application.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(main_application)
        self.toolBar.setObjectName(_from_utf_8("toolBar"))
        main_application.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_new_project = QtGui.QAction(main_application)
        self.action_new_project.setObjectName(_from_utf_8("action_new_project"))
        self.action_load_project = QtGui.QAction(main_application)
        self.action_load_project.setObjectName(_from_utf_8("action_load_project"))
        self.action_save_project = QtGui.QAction(main_application)
        self.action_save_project.setObjectName(_from_utf_8("action_save_project"))
        self.action_quit = QtGui.QAction(main_application)
        self.action_quit.setObjectName(_from_utf_8("action_quit"))
        self.action_swap = QtGui.QAction(main_application)
        self.action_swap.setObjectName(_from_utf_8("action_swap"))
        self.action_collapse = QtGui.QAction(main_application)
        self.action_collapse.setObjectName(_from_utf_8("action_collapse"))
        self.action_recalculate_mapping = QtGui.QAction(main_application)
        self.action_recalculate_mapping.setObjectName(_from_utf_8("action_recalculate_mapping"))
        self.action_save_as = QtGui.QAction(main_application)
        self.action_save_as.setObjectName(_from_utf_8("action_save_as"))
        self.action_load_connector_map = QtGui.QAction(main_application)
        self.action_load_connector_map.setObjectName(_from_utf_8("action_load_connector_map"))
        self.action_zoom_in = QtGui.QAction(main_application)
        self.action_zoom_in.setObjectName(_from_utf_8("action_zoom_in"))
        self.action_zoom_out = QtGui.QAction(main_application)
        self.action_zoom_out.setObjectName(_from_utf_8("action_zoom_out"))
        self.action_revert_mapping = QtGui.QAction(main_application)
        self.action_revert_mapping.setObjectName(_from_utf_8("action_revert_mapping"))
        self.action_collapse_overview = QtGui.QAction(main_application)
        self.action_collapse_overview.setObjectName(_from_utf_8("action_collapse_overview"))
        self.action_expand_overview = QtGui.QAction(main_application)
        self.action_expand_overview.setObjectName(_from_utf_8("action_expand_overview"))
        self.action_preferences = QtGui.QAction(main_application)
        self.action_preferences.setObjectName(_from_utf_8("action_preferences"))
        self.action_about = QtGui.QAction(main_application)
        self.action_about.setObjectName(_from_utf_8("action_about"))
        self.action_tutorials = QtGui.QAction(main_application)
        self.action_tutorials.setObjectName(_from_utf_8("action_tutorials"))
        self.action_virtual_units = QtGui.QAction(main_application)
        self.action_virtual_units.setObjectName(_from_utf_8("action_virtual_units"))
        self.action_export_to_csv = QtGui.QAction(main_application)
        self.action_export_to_csv.setObjectName(_from_utf_8("action_export_to_csv"))
        self.action_export_to_odml = QtGui.QAction(main_application)
        self.action_export_to_odml.setObjectName(_from_utf_8("action_export_to_odml"))
        self.action_import_from_csv = QtGui.QAction(main_application)
        self.action_import_from_csv.setObjectName(_from_utf_8("action_import_from_csv"))
        self.action_import_from_od_ml = QtGui.QAction(main_application)
        self.action_import_from_od_ml.setObjectName(_from_utf_8("action_import_from_od_ml"))
        self.action_revert_state = QtGui.QAction(main_application)
        self.action_revert_state.setObjectName(_from_utf_8("action_revert_state"))
        self.action_restore_state = QtGui.QAction(main_application)
        self.action_restore_state.setObjectName(_from_utf_8("action_restore_state"))
        self.action_save_state = QtGui.QAction(main_application)
        self.action_save_state.setObjectName(_from_utf_8("action_save_state"))

        self.menu_File.addAction(self.action_new_project)
        self.menu_File.addAction(self.action_load_project)
        self.menu_File.addAction(self.action_save_project)
        self.menu_File.addAction(self.action_save_as)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_load_connector_map)
        self.menu_File.addAction(self.action_export_to_csv)
        self.menu_File.addAction(self.action_export_to_odml)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_quit)

        self.menu_Edit.addAction(self.action_recalculate_mapping)
        self.menu_Edit.addAction(self.action_revert_mapping)
        self.menu_Edit.addAction(self.action_swap)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_zoom_in)
        self.menu_Edit.addAction(self.action_zoom_out)
        self.menu_Edit.addAction(self.action_expand_overview)
        self.menu_Edit.addAction(self.action_collapse_overview)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_preferences)

        self.menu_Help.addAction(self.action_tutorials)
        self.menu_Help.addAction(self.action_about)
        self.menu_View.addAction(self.action_virtual_units)
        self.menu_View.addAction(self.action_save_state)
        self.menu_View.addAction(self.action_restore_state)
        self.menu_View.addAction(self.action_revert_state)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.toolBar.addAction(self.action_new_project)
        self.toolBar.addAction(self.action_load_project)
        self.toolBar.addAction(self.action_save_project)
        self.toolBar.addAction(self.action_save_as)
        self.toolBar.addAction(self.action_preferences)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_revert_mapping)
        self.toolBar.addAction(self.action_swap)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_zoom_in)
        self.toolBar.addAction(self.action_zoom_out)
        self.toolBar.addAction(self.action_expand_overview)
        self.toolBar.addAction(self.action_collapse_overview)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_virtual_units)

        self.load_icons()
        self.retranslate_ui(main_application)

        main_application.tabifyDockWidget(self.dock_rate_profiles_view, self.dock_raster_plots_view)
        main_application.tabifyDockWidget(self.dock_raster_plots_view, self.dock_pca_3d_view)
        main_application.tabifyDockWidget(self.dock_pca_3d_view, self.dock_isi_histograms_view)
        main_application.tabifyDockWidget(self.dock_isi_histograms_view, self.dock_waveforms_3d_view)
        main_application.tabifyDockWidget(self.dock_waveforms_3d_view, self.dock_mean_waveforms_view)

        # self.action_quit.triggered.connect(main_application.close)
        QtCore.QMetaObject.connectSlotsByName(main_application)

    @staticmethod
    def set_program_title(main_application, text):
        main_application.setWindowTitle(_translate("main_application", text, None))

    def retranslate_ui(self, main_application):
        main_application.setWindowTitle(_translate("main_application", "SWAN - Sequential waveform analyser", None))
        self.menu_File.setTitle(_translate("main_application", "&File", None))
        self.menu_Edit.setTitle(_translate("main_application", "&Edit", None))
        self.menu_Help.setTitle(_translate("main_application", "&Help", None))
        self.menu_View.setTitle(_translate("main_application", "&View", None))
        self.toolBar.setWindowTitle(_translate("main_application", "toolBar", None))
        self.action_new_project.setText(_translate("main_application", "&New Project...", None))
        self.action_new_project.setIconText(_translate("main_application", "New Project...", None))
        self.action_new_project.setToolTip(_translate("main_application", "Create a new project", None))
        self.action_new_project.setShortcut(_translate("main_application", "Ctrl+N", None))
        self.action_load_project.setText(_translate("main_application", "&Load Project...", None))
        self.action_load_project.setIconText(_translate("main_application", "Load Project...", None))
        self.action_load_project.setToolTip(_translate("main_application", "Load project from file", None))
        self.action_load_project.setShortcut(_translate("main_application", "Ctrl+L", None))
        self.action_save_project.setText(_translate("main_application", "&Save Project", None))
        self.action_save_project.setIconText(_translate("main_application", "Save Project", None))
        self.action_save_project.setToolTip(_translate("main_application", "Save project", None))
        self.action_save_project.setShortcut(_translate("main_application", "Ctrl+S", None))
        self.action_quit.setText(_translate("main_application", "&Quit", None))
        self.action_quit.setToolTip(_translate("main_application", "Close this application", None))
        self.action_quit.setShortcut(_translate("main_application", "Ctrl+Q", None))
        self.action_swap.setText(_translate("main_application", "Swap", None))
        self.action_swap.setToolTip(_translate("main_application", "Swap two selected units", None))
        self.action_collapse.setText(_translate("main_application", "Collapse", None))
        self.action_collapse.setToolTip(_translate("main_application", "Collapse selected unit row(s)", None))
        self.action_recalculate_mapping.setText(_translate("main_application", "Recalculate mapping", None))
        self.action_recalculate_mapping.setToolTip(_translate("main_application", "Try to find a mapping automatically",
                                                              None))
        self.action_save_as.setText(_translate("main_application", "Save project as...", None))
        self.action_save_as.setToolTip(_translate("main_application", "Save project to a new file", None))
        self.action_load_connector_map.setText(_translate("main_application", "Load connector map...", None))
        self.action_zoom_in.setText(_translate("main_application", "Zoom in", None))
        self.action_zoom_in.setToolTip(_translate("main_application", "Zoom overview in", None))
        self.action_zoom_in.setShortcut(_translate("main_application", "Ctrl++", None))
        self.action_zoom_out.setText(_translate("main_application", "Zoom out", None))
        self.action_zoom_out.setToolTip(_translate("main_application", "Zoom overview out", None))
        self.action_zoom_out.setShortcut(_translate("main_application", "Ctrl+-", None))
        self.action_revert_mapping.setText(_translate("main_application", "Revert mapping...", None))
        self.action_revert_mapping.setToolTip(_translate("main_application", "Revert current mapping to last saved",
                                                         None))
        self.action_collapse_overview.setText(_translate("main_application", "Collapse overview", None))
        self.action_collapse_overview.setToolTip(_translate("main_application", "Decrease overview\'s y range", None))
        self.action_expand_overview.setText(_translate("main_application", "Expand overview", None))
        self.action_expand_overview.setToolTip(_translate("main_application", "Increase overview\'s y range", None))
        self.action_preferences.setText(_translate("main_application", "Preferences", None))
        self.action_preferences.setToolTip(_translate("main_application", "View and change preferences", None))
        self.action_about.setText(_translate("main_application", "About", None))
        self.action_about.setToolTip(_translate("main_application", "Information about SWAN", None))
        self.action_tutorials.setText(_translate("main_application", "Tutorials", None))
        self.action_virtual_units.setText(_translate("main_application", "Virtual units", None))
        self.action_virtual_units.setToolTip(_translate("main_application", "See virtual units", None))
        self.action_export_to_csv.setText(_translate("main_application", "Export to csv", None))
        self.action_export_to_odml.setText(_translate("main_application", "Export to odML", None))
        self.action_import_from_csv.setText(_translate("main_application", "Import from csv", None))
        self.action_import_from_od_ml.setText(_translate("main_application", "Import from odML", None))
        self.action_restore_state.setText(_translate("main_application", "Restore GUI state", None))
        self.action_revert_state.setText(_translate("main_application", "Revert GUI state", None))
        self.action_save_state.setText(_translate("main_application", "Save GUI state", None))

    def load_icons(self):
        """
        Loads the icons.
        
        """
        try:
            prefix = ":" + sep + "icons" + sep
            # File
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_new_project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_load_project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_save_project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_save_as.setIcon(icon)
            # Edit
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "revert.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_revert_mapping.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "swap.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_swap.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "zoom_in.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_zoom_in.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "zoom_out.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_zoom_out.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_expand_overview.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "collapse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_collapse_overview.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "preferences.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_preferences.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "vunits.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_virtual_units.setIcon(icon)
        except Exception as e:
            print("Icon Exception: {exception}".format(exception=e))
            pass
