"""
Created on Oct 22, 2013

@author: Christoph Gollan

This is the main module.

It contains the :class:`Main` class which is the main window of the application
and a :class:`MemoryTask` to show the memory usage on the status bar.

To run the application, you just have to execute *run.py*.

Look at :mod:`src.run` for more information.
"""
# system imports
from os import mkdir
from os.path import basename, split, isdir, join, exists
import platform
import csv
import webbrowser as web
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import os
import pickle as pkl

# swan-specific imports
from swan import about, title
from swan.gui.main_ui import Ui_Main
from swan.src.widgets.file_dialog import File_Dialog
from swan.src.widgets.preferences_dialog import Preferences_Dialog
from swan.src.mystorage import MyStorage
from swan.src.views.virtual_units_view import VUnits
from swan.src.export import Export

if platform.system() == "Linux":
    onLinux = True
    import resource
else:
    onLinux = False


class MemoryTask(QtWidgets.QProgressBar):
    """
    A class to show the memory usage on the main window's status bar.
    
    **Arguments**
    
        *timer* (:class:`PyQt5.QtCore.QTimer`):
            The timer that will be called periodic.
        *statusBar* (:class:`PyQt5.QtGui.QStatusBar`):
            The main window's status bar. 
            The memory usage will be shown here.
            This works only on Linux.
    
    """

    def __init__(self, timer, status_bar):
        """
        **Properties**:
        
            *timer* (:class:`PyQt5.QtCore.QTimer`)
            *bar* (:class:`PyQt5.QtGui.QStatusBar`)
        
        """
        QtWidgets.QProgressBar.__init__(self)
        self.timer = timer
        self.bar = status_bar
        timer.timeout.connect(self.refresh_memory)

    def run(self):
        """
        Calls :func:`start_timer`.
        
        """
        self.start_timer()

    def start_timer(self):
        """
        Starts the timer.
        
        """
        self.timer.start(1000)

    def stop_timer(self):
        """
        Stops the timer.
        
        """
        self.timer.stop()

    def refresh_memory(self):
        """
        Gets the memory usage and shows it.
        
        """
        QtGui.QApplication.processEvents()
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        usage = int((usage / 1024.0) * 100) / 100.0
        self.bar.showMessage("Memory used: " + str(usage) + "Mb", 0)


class Main(QtGui.QMainWindow):
    """
    This is the main window.
    
    It is the parent widget of all other widgets and closing it quits
    the application.
    
    This class has methods to handle the user actions either by itself or
    by delegating to the child widgets.
    
    **Arguments:**
    
        *program_dir* (string):
            The directory in which the program is located. It has to end with the top-level directory swan.
        *home_dir* (string):
            The directory where the project files will be written to by default.
            If you didn't execute *run.py* with an additional argument this will be your home directory. 
            Otherwise it will be the one you gave as an argument.
        *dark* (bool):
            Whether the dark theme should be enabled or not.
    
    """

    doPlot = QtCore.pyqtSignal(object, object)

    def __init__(self, program_dir, home_dir):
        """
        **Properties**:
       
            *_program_dir* (string):
                The path to this program. It has to end with the top-level directory swan.
            *_CACHEDIR* (string):
                The default path of the cache directory.
            *_currentdirty* (boolean):
                Whether or not the current (virtual unit) mapping is dirty because of changes.
            *_globaldirty* (boolean):
                Whether or not one or more (virtual unit) mappings are dirty.
            *_preferences* (dictionary):
                A dictionary containing all preferences in (key, value) pairs.
                The dictionary will be loaded at program start or set to default values.
            *_PREFS* (dictionary):
                The preferences dictionary containing the default values.
            *_prodir* (string):
                The path where the project files will be written to by default.
            *_mystorage* (:class:`stg.mystorage.MyStorage`):
                The class which handles the data and the project files.
        
        """
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_Main()
        self.ui.setupUi(self)

        # properties{
        self._program_dir = program_dir
        self._CACHEDIR = join(program_dir, "cache")
        self._currentdirty = False
        self._globaldirty = False
        self._preferences = None
        self._PREFS = {"defaultProName": "swan.txt",
                       "zinStep": 20.0,
                       "cacheDir": self._CACHEDIR,
                       "zoutStep": 20.0,
                       "expandStep": 5,
                       "collapseStep": 5,
                       }
        self._prodir = join(home_dir)

        # preferences have to be present for the storage.
        self.load_preferences()

        self._mystorage = MyStorage(program_dir, self._preferences["cacheDir"])
        # }
        self.setWindowTitle(title)

        # for the virtual unit overview
        self.vu = VUnits()
        self.vu.setWindowTitle("Virtual Units")

        # connect channel selection
        self.ui.tools.selector.doChannel.connect(self.do_channel)
        self.ui.plotGrid.child.indicatorToggle.connect(self.plot_all)
        self.ui.plotGrid.child.visibilityToggle.connect(self._mystorage.changeVisibility)
        # connect loading progress
        self._mystorage.progress.connect(self.setProgress)
        # connect redraw signal of the views
        # self.ui.view_3.redraw.connect(self.plot_all)
        self.vu.redraw.connect(self.plot_all)
        # connect channel loading
        self.vu.load.connect(self.load_channel)

        self.ui.view_1.sigClicked.connect(self.ui.plotGrid.child.highlightPlot)
        self.ui.view_3.sigClicked.connect(self.ui.plotGrid.child.highlightPlot)
        self.ui.view_4.sigClicked.connect(self.ui.plotGrid.child.highlightPlot)
        self.ui.view_6.sigClicked.connect(self.ui.plotGrid.child.highlightPlot)

        self.ui.plotGrid.child.plotSelected.connect(self.ui.view_1.highlightCurveFromPlot)
        self.ui.plotGrid.child.plotSelected.connect(self.ui.view_3.highlightCurveFromPlot)
        self.ui.plotGrid.child.plotSelected.connect(self.ui.view_4.highlightCurveFromPlot)
        self.ui.plotGrid.child.plotSelected.connect(self.ui.view_6.highlightCurveFromPlot)

        # shortcut reference
        self.plots = self.ui.plotGrid.child
        self.selector = self.ui.tools.selector

        self.check_dirs()

        self.doPlot.connect(self.plots.do_plot)
        self.doPlot.connect(self.ui.view_1.do_plot)
        self.doPlot.connect(self.ui.view_2.do_plot)
        self.doPlot.connect(self.ui.view_3.do_plot)
        self.doPlot.connect(self.ui.view_4.do_plot)
        self.doPlot.connect(self.ui.view_5.do_plot)
        self.doPlot.connect(self.ui.view_6.do_plot)

        self.ui.view_1.refreshPlots.connect(self.refresh_views)
        self.ui.view_2.refreshPlots.connect(self.refresh_views)
        self.ui.view_3.refreshPlots.connect(self.refresh_views)
        self.ui.view_4.refreshPlots.connect(self.refresh_views)
        self.ui.view_5.refreshPlots.connect(self.refresh_views)
        self.ui.view_6.refreshPlots.connect(self.refresh_views)

        # setting up the progress bar
        self.p = QtGui.QProgressBar()
        self.p.setRange(0, 100)
        self.p.setValue(0)
        self.ui.statusbar.addPermanentWidget(self.p)
        self.p.hide()

        self._defaultGuiState = self.saveState()
        self.saved_gui_state = self._defaultGuiState

        if onLinux:
            # starting memory usage task
            timer = QtCore.QTimer(self)
            self.timer = timer
            self.memorytask = MemoryTask(timer, self.ui.statusbar)
            self.memorytask.start_timer()

        self.showMaximized()

    #### action handler ####

    ### menu:File ###

    @QtCore.pyqtSlot(bool)
    def on_action_New_Project_triggered(self):
        """
        This method is called if you click on *File->New Project*.
        
        Shows a :class:`src.file_dialog.File_Dialog` to choose files and after accepting it creates a
        new project. The project consists of two files. One is a .txt file which contains
        the data file paths and the other one is a .vum file which contains
        the :class:`src.virtualunitmap.VirtualUnitMap`.
        
        The default names for the files are swan.txt and swan_vum.vum.
        If they already exist, they will be changed to swan(1).txt and swan(1)_vum.vum.
        If they exist, too, the number in the brackets will be incremented until the files
        don't exist.
        
        You can choose another default name in the preferences. 
        Look at :class:`src.preferences_dialog.Preferences_Dialog` for more. 
        
        """
        if self.dirty_project():

            dia = File_Dialog()

            if dia.exec_():
                files = dia.get_files()
                files.sort()

                channel = self._mystorage.get_channel()

                success = self._mystorage.load_project(self._prodir, self._preferences["defaultProName"], channel,
                                                       files)

                if success and self.do_channel(self._mystorage.get_channel(), self._mystorage.get_last_channel()):
                    filesStr = self._mystorage.get_files(True)
                    # setting filelist detail
                    self.set_detail(1, filesStr)

                    self.save_project()
                    self.update_project()
                    self.reset_dirty()
                    self.selector.select_only(self._mystorage.get_channel())
                    self.set_status("Created new project successfully.")
                else:
                    self.set_status("No files given. Nothing loaded.")

    @QtCore.pyqtSlot(bool)
    def on_action_Load_Project_triggered(self):
        """
        This method is called if you click on *File->Load Project*.
        
        You have to choose a .txt project file which contains correct paths to the data files.
        Loads the project by reading the .txt file and the .vum file.
        
        """
        if self.dirty_project():
            filename, nonsense = QtGui.QFileDialog.getOpenFileName(self,
                                                                   "Choose the file which includes the absolute paths",
                                                                   self._prodir)
            if filename:
                (prodir, proname) = split(filename)

                channel = self._mystorage.get_channel()

                success = self._mystorage.load_project(prodir, proname, channel)

                if success and self.do_channel(self._mystorage.get_channel(), self._mystorage.get_last_channel()):
                    filesStr = self._mystorage.get_files(True)
                    # setting filelist detail
                    self.set_detail(4, filesStr)

                    self.save_project()
                    self.update_project()
                    self.reset_dirty()
                    self.selector.select_only(self._mystorage.get_channel())
                    self.set_status("Loaded project successfully.")
                else:
                    self.set_status("No files given. Nothing loaded.")

    @QtCore.pyqtSlot(bool)
    def on_action_Save_Project_triggered(self):
        """
        This method is called if you click on *File->Save Project*.
        
        Works like :func:`on_action_Save_as_triggered()` but without asking you to type in a save name.
        
        """
        if self.check_project():
            self.save_project()

    @QtCore.pyqtSlot(bool)
    def on_action_Save_as_triggered(self):
        """
        This method is called if you click on *File->Save as*.
        
        Saves your project under a new name by showing you a dialog 
        where you can type the new project name (the one with the .txt extension).
        After that your loaded files will be written into that file
        (the absolute path to the files) so that you can later load them.
        
        The :class:`src.virtualunitmap.VirtualUnitMap` will be saved to 
        the file with the .vum extension.
        
        """
        if self.check_project():
            filename, nonsense = QtGui.QFileDialog.getSaveFileName(self, "Choose a name for the savefiles",
                                                                   self._prodir)
            if filename:
                self._mystorage.save_project_as(filename)
                self.update_project()
                self.save_project()

    @QtCore.pyqtSlot(bool)
    def on_action_Load_connector_map_triggered(self):
        """
        This method is called if you click on *File->Load connector map*.
        
        Loads a connector map given as a .csv file.
        
        Delegates the loading to :func:`load_connector_map`.
        
        """
        filename, nonsense = QtGui.QFileDialog.getOpenFileName(self, "Choose a file", self._prodir)
        try:
            self.load_connector_map(filename)
        except ValueError:
            QtGui.QMessageBox.critical(self, "Loading error", "The connector map could not be loaded!")

    @QtCore.pyqtSlot(bool)
    def on_action_Export_to_csv_triggered(self):
        """
        This method is called if you click on *File->Export to csv*.

        Exports the virtual unit mappings to a csv file.

        """
        filename, nonsense = QtGui.QFileDialog.getSaveFileName(self, "Choose a savename", self._prodir)
        if filename:
            try:
                if filename.endswith(".csv"):
                    filename = os.path.basename(filename)
                Export.export_csv(filename, self._mystorage.load_map())
            except IOError:
                QtGui.QMessageBox.critical(self, "Export error", "The virtual unit maps could not be exported")

    @QtCore.pyqtSlot(bool)
    def on_action_Export_to_odML_triggered(self):
        """
        This method is called if you click on *File->Export to odML*.

        Exports the virtual unit mappings to an odML file.

        """
        filename, nonsense = QtGui.QFileDialog.getSaveFileName(self, "Choose a savename", self._prodir)
        if filename:
            try:
                if filename.endswith(".odml"):
                    filename = os.path.basename(filename)
                Export.export_odml(filename, self._mystorage.load_map())
            except IOError:
                QtGui.QMessageBox.critical(self, "Export error", "The virtual unit maps could not be exported")

    def closeEvent(self, event):
        """
        This method is called if you click on *File->Quit*.
        
        Quits the application.
        If there are unsaved mappings, you will have a chance to save them.
        
        The event will be always accepted.
        
        **Arguments**
        
            *event* (:class:`PyQt5.QtCore.QEvent`)
        """
        if self.dirty_project():
            event.accept()
        else:
            event.ignore()

    ### menu:Edit ###

    @QtCore.pyqtSlot(bool)
    def on_action_Recalculate_mapping_triggered(self):
        """
        This method is called if you click on *Edit->Recalculate mapping*.
        
        Delegates the calculating to another class. Updates the overview.
        
        See :func:`src.mystorage.MyStorage.recalculate`.
        
        """
        if self._mystorage.has_project():
            answer = QtGui.QMessageBox(self)
            answer.setWindowTitle("Recalculate mapping")
            answer.setText(
                "WARNING! This will irreversibly change the current mapping!\n\nChoose the mapping algorithm to implement:")

            btn1 = QtGui.QPushButton("SWAN Implementation")
            btn2 = QtGui.QPushButton("Fraser-Schwarz Implementation")
            btn3 = QtGui.QPushButton("Cancel")

            answer.addButton(btn1, QtGui.QMessageBox.AcceptRole)
            answer.addButton(btn2, QtGui.QMessageBox.AcceptRole)
            answer.addButton(btn3, QtGui.QMessageBox.NoRole)

            answer.exec_()
            if answer.clickedButton() in [btn1, btn2]:
                if answer.clickedButton() == btn1:
                    mapping = 1
                elif answer.clickedButton() == btn2:
                    mapping = 2
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                self._mystorage.recalculate(mapping)
                self._currentdirty = True
                self._globaldirty = True
                self.plots.setAllForUpdate()
                self.plot_all()
                self.plots.set_tooltips(self._mystorage.get_tooltips())
                QtGui.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(bool)
    def on_action_Revert_mapping_triggered(self):
        """
        This method is called if you click on *Edit->Revert mapping*.
        
        Delegates the reverting to another class. Updates the overview.
        
        See :func:`src.mystorage.MyStorage.revert`.
        
        """
        if self._mystorage.has_project():
            answer = QtGui.QMessageBox.question(self, "Revert mapping", "Are you sure you want to do this?",
                                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                defaultButton=QtGui.QMessageBox.No)

            if answer == QtGui.QMessageBox.Yes:
                self._mystorage.revert()
                self.reset_current_dirty()
                self.plots.setAllForUpdate()
                self.plot_all()
                self.plots.set_tooltips(self._mystorage.get_tooltips())

    @QtCore.pyqtSlot(bool)
    def on_action_Swap_triggered(self):
        """
        This method is called if you click on *Edit->Swap*.
        
        Swaps two plots if two are selected.
        Otherwise nothing will happen.
        
        The swapping itself is done somewhere else.
        
        See :func:`src.mystorage.MyStorage.swap`.
        
        """
        plots = self.plots.get_selection()
        if len(plots) == 2:
            # get the positions
            plot_1 = plots[0]
            plot_2 = plots[1]
            plot_1.toBeUpdated = True
            plot_2.toBeUpdated = True
            session = plot_1.pos[0]
            unit_id_1 = plot_1.pos[1]
            unit_id_2 = plot_2.pos[1]

            # swapping
            self._mystorage.swap(session, unit_id_1, unit_id_2)
            self.plot_all()
            self.plots.reset_selection()

            # setting tooltips
            self.plots.swap_tooltips(plot_1, plot_2)

            self._currentdirty = True
            self._globaldirty = True

    @QtCore.pyqtSlot(bool)
    def on_action_Zoom_in_triggered(self):
        """
        This method is called if you click on *Edit->Zoom in*.
        
        Zooms the overview in. The zoom step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.zoom_in(self._preferences["zinStep"])

    @QtCore.pyqtSlot(bool)
    def on_action_Zoom_out_triggered(self):
        """
        This method is called if you click on *Edit->Zoom out*.
        
        Zooms the overview out. The zoom step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.zoom_out(self._preferences["zoutStep"])

    @QtCore.pyqtSlot(bool)
    def on_action_Expand_overview_triggered(self):
        """
        This method is called if you click on *Edit->Expand overview*.
        
        Increases the y range of the plots in the overview.
        The step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.expand(self._preferences["expandStep"])

    @QtCore.pyqtSlot(bool)
    def on_action_Collapse_overview_triggered(self):
        """
        This method is called if you click on *Edit->Collapse overview*.
        
        Decreases the y range of the plots in the overview.
        The step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.collapse(self._preferences["collapseStep"])

    @QtCore.pyqtSlot(bool)
    def on_action_Preferences_triggered(self):
        """
        This method is called if you click on *Edit->Preferences*.
        
        Shows you a :class:`src.preferences_dialog.Preferences_Dialog`
        to view and change the preferences.
        
        """
        dia = Preferences_Dialog(self._preferences.copy(), self._PREFS.copy())
        if dia.exec_():
            pref = dia.get_preferences()
            self._preferences = pref
            self.save_preferences()
            self._mystorage.set_cache_dir(pref["cacheDir"])

    ### menu:View ###

    @QtCore.pyqtSlot(bool)
    def on_action_Virtual_Units_triggered(self):
        """
        This method is called if you click on *View->Virtual units*.

        Shows an overview for the virtual units.

        """
        self.vu.show()

    ### menu:Help ###

    @QtCore.pyqtSlot(bool)
    def on_action_Tutorials_triggered(self):
        """
        This method is called if you click on *Help->Tutorials*.
        
        Shows you tutorials and help for this application.
        
        """
        p = os.path.join(self._program_dir, "doc", "build", "html", "tutorial.html")
        d = "file://" + p
        web.open_new_tab(d)

    @QtCore.pyqtSlot(bool)
    def on_action_About_triggered(self):
        """
        This method is called if you click on *Help->About*.
        
        Shows you information about the application.
        
        """
        QtGui.QMessageBox.information(self, "About", about)

    @QtCore.pyqtSlot(bool)
    def on_action_RevertState_triggered(self):
        """
        This method is called if you click on *View->Revert GUI State*.
        
        Restores the GUI to it's default configuration.
        """

        self.restoreState(self._defaultGuiState)

    @QtCore.pyqtSlot(bool)
    def on_action_RestoreState_triggered(self):
        """
        This method is called if you click on *View->Restore GUI State*.

        Restores the GUI to the previously saved configuration. Restores to default
        configuration if no saves were performed.
        """

        self.restoreState(self.saved_gui_state)

    @QtCore.pyqtSlot(bool)
    def on_action_SaveState_triggered(self):
        """
        This method is called if you click on *View->Save GUI State*.

        Saves the current configuration of the GUI to be restored later.
        """

        self.saved_gui_state = self.saveState()

    #### signal handler ####

    def do_channel(self, channel, lastchannel, automaticMapping=0):
        """
        Loads the data from the given electrode and plots it.
        
        **Arguments**
        
            *channel* (integer):
                The electrode channel that will be loaded.
            *lastchannel* (integer):
                The channel that was loaded before.
        
            **Returns**: boolean
                Whether or not there was something to load for the electrode.
        
        """
        if self._mystorage.has_project() and not self._mystorage.is_loading():
            # initialize the progress bar
            self.p.setValue(0)
            self.p.show()

            self.check_cache()

            # let the user know that loading can be take some time
            if onLinux:
                self.memorytask.stop_timer()
            self.set_status("Loading... This may take a while...", 0)

            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            # checking if the last channel's mapping was dirty
            if self._currentdirty:
                self.selector.set_dirty(lastchannel, True)

            self._currentdirty = self.selector.get_item(channel).dirty

            # loading
            (n, m) = self._mystorage.load_channel(channel)

            #            self.ui.tools.units.init_units(n)

            # plotting
            self.plots.reset_selection()
            data = self._mystorage.get_data()
            self.plots.make_plots(n, m, data.get_dates())

            if any(data.total_units_per_block):
                min0, max0 = data.get_yscale()
            else:
                min0, max0 = [-100, 100]
            self.plots.set_yranges(min0, max0)

            vum = self._mystorage.get_map()
            vum.calculate_mapping(data, self._mystorage, automaticMapping)

            self.plot_all()

            # setting channel detail
            self.set_detail(1, str(channel))
            self.ui.setProgramTitle(self, self._preferences["defaultProName"] + " | " + "Channel " + str(
                channel) + " | " + title)

            # setting tooltips
            self.plots.set_tooltips(self._mystorage.get_tooltips())

            self.p.hide()
            QtGui.QApplication.restoreOverrideCursor()
            if onLinux:
                self.memorytask.start_timer()
            return True
        elif self._mystorage.is_loading():
            self.selector.select_only(self._mystorage.get_channel())
            return False

    def plot_all(self, i=None, j=None, visible=False):
        """
        Plots everything that has to be plotted.
        
        It is possible to make a row in the :class:`src.virtualunitmap.VirtualUnitMap`
        (in)visible by passing extra arguments. This method is called every time something
        has to be plotted or updated.
        
        **Arguments**
        
            *i* (integer or None):
                The index of the row you want to make invisible.
                Default: None
            *visible* (boolean or None):
                Whether or not the row given by i should be visible.
                Default: None
        
        """
        if self._mystorage.has_project():
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            vum = self._mystorage.get_map()
            data = self._mystorage.get_data()
            vum_all = self._mystorage.get_mappings()

            if i is not None and j is not None:
                vum.set_visible(i, j, visible)

            self.doPlot.emit(vum, data)
            self.vu.do_plot(vum_all, data)

            QtGui.QApplication.restoreOverrideCursor()

    def refresh_views(self):

        if self._mystorage.has_project():
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            vum = self._mystorage.get_map()
            data = self._mystorage.get_data()

            # plotting
            # plots: pyqtgraph plotwidget overview
            self.plots.do_plot(vum, data)
            # view_1: 2D mpl plot
            self.ui.view_1.do_plot(vum, data)
            # view_2: mpl movie plot
            self.ui.view_2.do_plot(vum, data)
            # view_3: ISI mpl plot
            self.ui.view_3.do_plot(vum, data)
            # view_4: PCA pyqtgraph plot
            self.ui.view_4.do_plot(vum, data)
            # view_5: 2D PCA pyqtgraph plot
            self.ui.view_5.do_plot(vum, data)
            # view_6: Rate Profiles plot
            self.ui.view_6.do_plot(vum, data)

            QtGui.QApplication.restoreOverrideCursor()

    def setProgress(self, i):
        """
        Sets the progress in the status bar.

        **Arguments**
                
            *i* (integer):
                The value to be set.
        
        """
        self.p.setValue(i)

    def showProgressBar(self, show):
        """
        Shows or hides the progress bar.

        **Arguments**
                
            *show* (boolean):
                Whether or not the progress bar should be shown.
        
        """
        if show:
            self.p.show()
        else:
            self.p.hide()

    def load_channel(self, channel):
        """
        Loads a channel.

        This method is connected to the load signal of the
        :class:`src.VUnits` class.

        **Arguments**

            *channel* (integer):
                The channel to load.

        """
        item = self.selector.get_item(channel)
        if item != 0:
            if item.selectable:
                self.selector.select_channel(item, channel)
                self.selector.select_only(channel)

    #### general methods ####

    def dirty_project(self):
        """
        Lets you save your project before losing your progress.
        
        Shows you a confirmation dialog and if you accept, the project
        will be saved.
        
        """
        if self._globaldirty:
            answer = QtGui.QMessageBox.question(self, "Confirmation",
                                                "There are unsaved changes.\nDo you want to save your project first?",
                                                buttons=QtGui.QMessageBox.Cancel | QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                                defaultButton=QtGui.QMessageBox.Yes)
            if answer == QtGui.QMessageBox.Yes:
                self.save_project()
                return True
            elif answer == QtGui.QMessageBox.No:
                return True
            else:
                return False
        else:
            return True

    def update_project(self):
        """
        Updates the project data like the project name and the directory.
        Shows the changed values in the details tab.
        
        """
        if self._mystorage.has_project():
            (prodir, proname) = split(self._mystorage.get_project_path())
            vumname = basename(self._mystorage.get_map_path())
            # setting project details
            self.set_detail(0, proname)
            self.set_detail(1, prodir)
            self.set_detail(2, vumname)

    def check_project(self):
        """
        Checks if there is currently a project loaded.
         
            **Returns**: boolean
                Whether or not there is a project loaded.
         
        """
        if not self._mystorage.has_project():
            QtGui.QMessageBox.warning(self, "Error", "No project loaded.")
            return False
        else:
            return True

    def save_project(self):
        """
        Saves the project.
        
        See :func:`src.mystorage.MyStorage.save_project`.
        
        """
        self._mystorage.save_project()
        self.reset_dirty()
        self.set_status("Saved project successfully")

    def reset_dirty(self):
        """
        Resets the project to a not dirty state.
        
        """
        self._currentdirty = False
        self._globaldirty = False
        self.selector.reset_dirty()

    def reset_current_dirty(self):
        """
        Resets the current channel.

        """
        self._currentdirty = False
        self.selector.set_dirty(self._mystorage.get_channel(), False)
        if len(self.selector.get_dirty_channels()) == 0:
            self._globaldirty = False

    def set_detail(self, i, value):
        """
        Sets a detail in the details tab.
        
        **Arguments**
        
            *i* (integer):
                The index of the detail.
            *value* (string):
                The value that should be shown.
        
        """
        self.ui.tools.details.item(i, 0).setText(value)

    def check_dirs(self):
        """
        Checks if all directories exist which are needed by the program.
        If not, they will be created.
        
        """
        data_dir = join(self._program_dir, "data")
        if not isdir(data_dir):
            mkdir(data_dir)
        self.check_cache()

    def check_cache(self):
        """
        Checks if the cache directory exists.
        If not, it will be created.
        
        """
        if not isdir(self._preferences["cacheDir"]):
            mkdir(self._preferences["cacheDir"])

    def load_connector_map(self, filename):
        """
        Loads a connector map given as a .csv file.
        
        The file has to contain two columns. The first will be ignored but must exist
        (e.g. the numbers 1-100) and the other one has to contain the mapped channel numbers.
        Choose **,** as delimiter.
        
        **Arguments**
        
            *filename* (string):
                The csv file to load.
        
            **Raises**: :class:`ValueError`
                If the connector map could not be loaded.
                
        """
        if filename:
            delimiter = ','
            try:
                with open(filename, "r") as fn:
                    channel_list = []
                    reader = csv.reader(fn, delimiter=delimiter)
                    for row in reader:
                        # just read the second column
                        channel_list.append(int(row[1]))
                channels = self.selector.get_dirty_channels()

                # overwrite existing mapping
                self.selector.set_channels(channel_list)
                self.selector.reset_sel()
                self.selector.reset_dirty()

                # the dirty channels and the selected one has to be set again
                for channel in channels:
                    self.selector.set_dirty(channel, True)

                self.selector.select_only(self._mystorage.get_channel())
            except Exception as e:
                print(e)

    def load_preferences(self):
        """
        Loads the preferences from the preferences file.
        If it doesn't exist, defaults are used.
        
        """
        name = join(self._program_dir, "data", "preferences.pkl")
        if exists(name):
            prefs = pkl.load(open(name, "rb"))
            self._preferences = prefs
        else:
            self._preferences = self._PREFS.copy()

    def save_preferences(self):
        """
        Writes the preferences to a file.
        
        """
        name = join(self._program_dir, "data", "preferences.pkl")
        with open(name, "wb") as fn:
            pkl.dump(self._preferences, fn)

    def set_status(self, content, duration=5000):
        """
        Shows a message in the status bar for a given duration.
        
        **Arguments**
        
            *content* (string):
                The message.
            *duration* (integer):
                The duration in ms.
                Default: 5000 
        
        """
        self.ui.statusbar.showMessage(content, duration)
