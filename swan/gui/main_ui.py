#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 23:26:08 2017

@author: Shashwat Sridhar
"""
# system imports
from pyqtgraph.Qt import QtCore, QtGui
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
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Main(object):
    def setupUi(self, Main):
        Main.setObjectName(_fromUtf8("Main"))

        Main.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks |
                            QtGui.QMainWindow.AllowNestedDocks |
                            QtGui.QMainWindow.GroupedDragging)

        self.plotGridDock = QtGui.QDockWidget("Plot Grid")
        self.plotGridDock.setObjectName(_fromUtf8("PlotGridDock"))
        self.plotGrid = MyPlotGrid(Main)
        self.plotGridDock.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                      QtGui.QDockWidget.DockWidgetFloatable)
        self.plotGridDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.plotGridDock.setWidget(self.plotGrid)
        Main.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.plotGridDock, QtCore.Qt.Vertical)

        self.dock_mean_waveforms_view = QtGui.QDockWidget("Mean Waveforms")
        self.dock_mean_waveforms_view.setObjectName(_fromUtf8("meanWaveformView"))
        self.dock_mean_waveforms_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                                  QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_mean_waveforms_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_mean_waveforms_view, QtCore.Qt.Vertical)

        self.mean_waveforms_view = pgWidget2d()
        self.mean_waveforms_view.setObjectName(_fromUtf8("meanWaveformsView"))

        self.dock_mean_waveforms_view.setWidget(self.mean_waveforms_view)

        self.dock_waveforms_3d_view = QtGui.QDockWidget("3D Waveforms")
        self.dock_waveforms_3d_view.setObjectName(_fromUtf8("3dWaveformView"))
        self.dock_waveforms_3d_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                     QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_waveforms_3d_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_waveforms_3d_view, QtCore.Qt.Vertical)

        self.waveforms_3d_view = pgWidget3d()
        self.waveforms_3d_view.setObjectName(_fromUtf8("3dWaveformsView"))

        self.dock_waveforms_3d_view.setWidget(self.waveforms_3d_view)

        self.dock_isi_histograms_view = QtGui.QDockWidget("ISI Histograms")
        self.dock_isi_histograms_view.setObjectName(_fromUtf8("ISIHView"))
        self.dock_isi_histograms_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                     QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_isi_histograms_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_isi_histograms_view, QtCore.Qt.Vertical)

        self.isi_histograms_view = pgWidgetISI()
        self.isi_histograms_view.setObjectName(_fromUtf8("IsihView"))

        self.dock_isi_histograms_view.setWidget(self.isi_histograms_view)

        self.dock_pca_3d_view = QtGui.QDockWidget("Principal Component Analysis")
        self.dock_pca_3d_view.setObjectName(_fromUtf8("PCAView"))
        self.dock_pca_3d_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                     QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_pca_3d_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_pca_3d_view, QtCore.Qt.Vertical)

        self.pca_3d_view = pgWidgetPCA()
        self.pca_3d_view.setObjectName(_fromUtf8("PcaView"))

        self.dock_pca_3d_view.setWidget(self.pca_3d_view)

        self.dock_raster_plots_view = QtGui.QDockWidget("Raster Plots")
        self.dock_raster_plots_view.setObjectName(_fromUtf8("RasterPlotView"))
        self.dock_raster_plots_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                     QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_raster_plots_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_raster_plots_view, QtCore.Qt.Vertical)

        self.raster_plots_view = pgWidgetPCA2d()
        self.raster_plots_view.setObjectName(_fromUtf8("RasterView"))

        self.dock_raster_plots_view.setWidget(self.raster_plots_view)

        self.dock_rate_profiles_view = QtGui.QDockWidget("Rate Profiles")
        self.dock_rate_profiles_view.setObjectName(_fromUtf8("RateProfiles"))
        self.dock_rate_profiles_view.setFeatures(QtGui.QDockWidget.DockWidgetMovable |
                                     QtGui.QDockWidget.DockWidgetFloatable)
        self.dock_rate_profiles_view.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        Main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_rate_profiles_view, QtCore.Qt.Vertical)

        self.rate_profiles_view = pgWidgetRateProfile()
        self.rate_profiles_view.setObjectName(_fromUtf8("RateProfileView"))

        self.dock_rate_profiles_view.setWidget(self.rate_profiles_view)

        self.tools = plotGridTools()

        self.plotGridOptionsLayout = QtGui.QGridLayout()
        self.plotGridOptionsLayout.setObjectName(_fromUtf8("PlotGridOptionsLayout"))

        self.plotGridOptionsLayout.addWidget(self.tools)
        self.plotGridOptions = collapsibleWidget(parent=self.plotGrid, title="Options", animationDuration=400)
        self.plotGridOptions.setContentLayout(self.plotGridOptionsLayout)

        self.plotGrid.mainGridLayout.addWidget(self.plotGridOptions, 1, 0)
        self.plotGrid.mainGridLayout.setRowStretch(0, 10)

        self.menubar = QtGui.QMenuBar(Main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1159, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Edit = QtGui.QMenu(self.menubar)
        self.menu_Edit.setObjectName(_fromUtf8("menu_Edit"))
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName(_fromUtf8("menu_Help"))
        self.menu_View = QtGui.QMenu(self.menubar)
        self.menu_View.setObjectName(_fromUtf8("menu_View"))
        Main.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Main)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        Main.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(Main)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        # self.toolBar.setStyleSheet('QToolBar{spacing:10px;}')
        Main.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_New_Project = QtGui.QAction(Main)
        self.action_New_Project.setObjectName(_fromUtf8("action_New_Project"))
        self.action_Load_Project = QtGui.QAction(Main)
        self.action_Load_Project.setObjectName(_fromUtf8("action_Load_Project"))
        self.action_Save_Project = QtGui.QAction(Main)
        self.action_Save_Project.setObjectName(_fromUtf8("action_Save_Project"))
        self.action_Quit = QtGui.QAction(Main)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.action_Swap = QtGui.QAction(Main)
        self.action_Swap.setObjectName(_fromUtf8("action_Swap"))
        self.action_Collapse = QtGui.QAction(Main)
        self.action_Collapse.setObjectName(_fromUtf8("action_Collapse"))
        self.action_Recalculate_mapping = QtGui.QAction(Main)
        self.action_Recalculate_mapping.setObjectName(_fromUtf8("action_Recalculate_mapping"))
        self.action_Save_as = QtGui.QAction(Main)
        self.action_Save_as.setObjectName(_fromUtf8("action_Save_as"))
        self.action_Load_connector_map = QtGui.QAction(Main)
        self.action_Load_connector_map.setObjectName(_fromUtf8("action_Load_connector_map"))
        self.action_Zoom_in = QtGui.QAction(Main)
        self.action_Zoom_in.setObjectName(_fromUtf8("action_Zoom_in"))
        self.action_Zoom_out = QtGui.QAction(Main)
        self.action_Zoom_out.setObjectName(_fromUtf8("action_Zoom_out"))
        self.action_Revert_mapping = QtGui.QAction(Main)
        self.action_Revert_mapping.setObjectName(_fromUtf8("action_Revert_mapping"))
        self.action_Collapse_overview = QtGui.QAction(Main)
        self.action_Collapse_overview.setObjectName(_fromUtf8("action_Collapse_overview"))
        self.action_Expand_overview = QtGui.QAction(Main)
        self.action_Expand_overview.setObjectName(_fromUtf8("action_Expand_overview"))
        self.action_Preferences = QtGui.QAction(Main)
        self.action_Preferences.setObjectName(_fromUtf8("action_Preferences"))
        self.action_About = QtGui.QAction(Main)
        self.action_About.setObjectName(_fromUtf8("action_About"))
        self.action_Tutorials = QtGui.QAction(Main)
        self.action_Tutorials.setObjectName(_fromUtf8("action_Tutorials"))
        self.action_Virtual_Units = QtGui.QAction(Main)
        self.action_Virtual_Units.setObjectName(_fromUtf8("action_Virtual_Units"))
        self.action_Export_to_csv = QtGui.QAction(Main)
        self.action_Export_to_csv.setObjectName(_fromUtf8("action_Export_to_csv"))
        self.action_Export_to_odML = QtGui.QAction(Main)
        self.action_Export_to_odML.setObjectName(_fromUtf8("action_Export_to_odML"))
        self.action_Import_from_csv = QtGui.QAction(Main)
        self.action_Import_from_csv.setObjectName(_fromUtf8("action_Import_from_csv"))
        self.action_Import_from_odML = QtGui.QAction(Main)
        self.action_Import_from_odML.setObjectName(_fromUtf8("action_Import_from_odML"))
        self.action_RevertState = QtGui.QAction(Main)
        self.action_RevertState.setObjectName(_fromUtf8("action_RevertState"))
        self.action_RestoreState = QtGui.QAction(Main)
        self.action_RestoreState.setObjectName(_fromUtf8("action_RestoreState"))
        self.action_SaveState = QtGui.QAction(Main)
        self.action_SaveState.setObjectName(_fromUtf8("action_SaveState"))

        self.menu_File.addAction(self.action_New_Project)
        self.menu_File.addAction(self.action_Load_Project)
        self.menu_File.addAction(self.action_Save_Project)
        self.menu_File.addAction(self.action_Save_as)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Load_connector_map)
        self.menu_File.addAction(self.action_Export_to_csv)
        self.menu_File.addAction(self.action_Export_to_odML)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Edit.addAction(self.action_Recalculate_mapping)
        self.menu_Edit.addAction(self.action_Revert_mapping)
        self.menu_Edit.addAction(self.action_Swap)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Zoom_in)
        self.menu_Edit.addAction(self.action_Zoom_out)
        self.menu_Edit.addAction(self.action_Expand_overview)
        self.menu_Edit.addAction(self.action_Collapse_overview)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Preferences)
        self.menu_Help.addAction(self.action_Tutorials)
        self.menu_Help.addAction(self.action_About)
        self.menu_View.addAction(self.action_Virtual_Units)
        self.menu_View.addAction(self.action_SaveState)
        self.menu_View.addAction(self.action_RestoreState)
        self.menu_View.addAction(self.action_RevertState)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.toolBar.addAction(self.action_New_Project)
        self.toolBar.addAction(self.action_Load_Project)
        self.toolBar.addAction(self.action_Save_Project)
        self.toolBar.addAction(self.action_Save_as)
        self.toolBar.addAction(self.action_Preferences)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_Revert_mapping)
        self.toolBar.addAction(self.action_Swap)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_Zoom_in)
        self.toolBar.addAction(self.action_Zoom_out)
        self.toolBar.addAction(self.action_Expand_overview)
        self.toolBar.addAction(self.action_Collapse_overview)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_Virtual_Units)

        self.load_icons()
        self.retranslateUi(Main)

        Main.tabifyDockWidget(self.dock_rate_profiles_view, self.dock_raster_plots_view)
        Main.tabifyDockWidget(self.dock_raster_plots_view, self.dock_pca_3d_view)
        Main.tabifyDockWidget(self.dock_pca_3d_view, self.dock_isi_histograms_view)
        Main.tabifyDockWidget(self.dock_isi_histograms_view, self.dock_waveforms_3d_view)
        Main.tabifyDockWidget(self.dock_waveforms_3d_view, self.dock_mean_waveforms_view)

        self.action_Quit.triggered.connect(Main.close)
        QtCore.QMetaObject.connectSlotsByName(Main)

    def setProgramTitle(self, Main, text):
        Main.setWindowTitle(_translate("Main", text, None))

    def retranslateUi(self, Main):
        Main.setWindowTitle(_translate("Main", "SWAN - Sequential waveform analyser", None))
        self.menu_File.setTitle(_translate("Main", "&File", None))
        self.menu_Edit.setTitle(_translate("Main", "&Edit", None))
        self.menu_Help.setTitle(_translate("Main", "&Help", None))
        self.menu_View.setTitle(_translate("Main", "&View", None))
        self.toolBar.setWindowTitle(_translate("Main", "toolBar", None))
        self.action_New_Project.setText(_translate("Main", "&New Project...", None))
        self.action_New_Project.setIconText(_translate("Main", "New Project...", None))
        self.action_New_Project.setToolTip(_translate("Main", "Create a new project", None))
        self.action_New_Project.setShortcut(_translate("Main", "Ctrl+N", None))
        self.action_Load_Project.setText(_translate("Main", "&Load Project...", None))
        self.action_Load_Project.setIconText(_translate("Main", "Load Project...", None))
        self.action_Load_Project.setToolTip(_translate("Main", "Load project from file", None))
        self.action_Load_Project.setShortcut(_translate("Main", "Ctrl+L", None))
        self.action_Save_Project.setText(_translate("Main", "&Save Project", None))
        self.action_Save_Project.setIconText(_translate("Main", "Save Project", None))
        self.action_Save_Project.setToolTip(_translate("Main", "Save project", None))
        self.action_Save_Project.setShortcut(_translate("Main", "Ctrl+S", None))
        self.action_Quit.setText(_translate("Main", "&Quit", None))
        self.action_Quit.setToolTip(_translate("Main", "Close this application", None))
        self.action_Quit.setShortcut(_translate("Main", "Ctrl+Q", None))
        self.action_Swap.setText(_translate("Main", "Swap", None))
        self.action_Swap.setToolTip(_translate("Main", "Swap two selected units", None))
        self.action_Collapse.setText(_translate("Main", "Collapse", None))
        self.action_Collapse.setToolTip(_translate("Main", "Collapse selected unit row(s)", None))
        self.action_Recalculate_mapping.setText(_translate("Main", "Recalculate mapping", None))
        self.action_Recalculate_mapping.setToolTip(_translate("Main", "Try to find a mapping automatically", None))
        self.action_Save_as.setText(_translate("Main", "Save project as...", None))
        self.action_Save_as.setToolTip(_translate("Main", "Save project to a new file", None))
        self.action_Load_connector_map.setText(_translate("Main", "Load connector map...", None))
        self.action_Zoom_in.setText(_translate("Main", "Zoom in", None))
        self.action_Zoom_in.setToolTip(_translate("Main", "Zoom overview in", None))
        self.action_Zoom_in.setShortcut(_translate("Main", "Ctrl++", None))
        self.action_Zoom_out.setText(_translate("Main", "Zoom out", None))
        self.action_Zoom_out.setToolTip(_translate("Main", "Zoom overview out", None))
        self.action_Zoom_out.setShortcut(_translate("Main", "Ctrl+-", None))
        self.action_Revert_mapping.setText(_translate("Main", "Revert mapping", None))
        self.action_Revert_mapping.setToolTip(_translate("Main", "Revert current mapping to last saved", None))
        self.action_Collapse_overview.setText(_translate("Main", "Collapse overview", None))
        self.action_Collapse_overview.setToolTip(_translate("Main", "Decrease overview\'s y range", None))
        self.action_Expand_overview.setText(_translate("Main", "Expand overview", None))
        self.action_Expand_overview.setToolTip(_translate("Main", "Increase overview\'s y range", None))
        self.action_Preferences.setText(_translate("Main", "Preferences", None))
        self.action_Preferences.setToolTip(_translate("Main", "View and change preferences", None))
        self.action_About.setText(_translate("Main", "About", None))
        self.action_About.setToolTip(_translate("Main", "Information about SWAN", None))
        self.action_Tutorials.setText(_translate("Main", "Tutorials", None))
        self.action_Virtual_Units.setText(_translate("Main", "Virtual units", None))
        self.action_Virtual_Units.setToolTip(_translate("Main", "See virtual units", None))
        self.action_Export_to_csv.setText(_translate("Main", "Export to csv", None))
        self.action_Export_to_odML.setText(_translate("Main", "Export to odML", None))
        self.action_Import_from_csv.setText(_translate("Main", "Import from csv", None))
        self.action_Import_from_odML.setText(_translate("Main", "Import from odML", None))
        self.action_RestoreState.setText(_translate("Main", "Restore GUI state", None))
        self.action_RevertState.setText(_translate("Main", "Revert GUI state", None))
        self.action_SaveState.setText(_translate("Main", "Save GUI state", None))

    def load_icons(self):
        """
        Loads the icons.
        
        """
        try:
            prefix = ":" + sep + "icons" + sep
            # File
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_New_Project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Load_Project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Save_Project.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Save_as.setIcon(icon)
            # Edit
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "revert.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Revert_mapping.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "swap.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Swap.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "zoom_in.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Zoom_in.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "zoom_out.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Zoom_out.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Expand_overview.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "collapse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Collapse_overview.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "preferences.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Preferences.setIcon(icon)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(prefix + "vunits.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.action_Virtual_Units.setIcon(icon)
        except:
            print("Icon Exception")
            pass
