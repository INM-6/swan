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
from os.path import basename, split, join, exists
import csv
import webbrowser as web
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import os
import pickle as pkl
import pathlib
import psutil

# swan-specific imports
from swan import about, title
from swan.gui.main_ui import MainUI
from swan.widgets.file_dialog import File_Dialog
from swan.widgets.preferences_dialog import Preferences_Dialog
from swan.storage import MyStorage
from swan.views.virtual_units_view import VirtualUnitsView
from swan.export import Export


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
        QtWidgets.QApplication.processEvents()
        usage = psutil.Process(os.getpid()).memory_info().rss
        usage = int(usage / 2 ** 20)
        self.bar.showMessage("Memory used: {0} MB".format(usage), 0)


class Main(QtWidgets.QMainWindow):
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

    def __init__(self, program_dir, home_dir, *args, **kwargs):
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
            *_mystorage* (:class:`base.mystorage.MyStorage`):
                The class which handles the data and the project files.
        
        """
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)

        self.ui = MainUI(self)

        # properties{
        self._program_dir = program_dir
        self._CACHEDIR = join(home_dir, "swan", "cache")
        self._current_dirty = False
        self._global_dirty = False
        self._preferences = None
        self._PREFS = {"projectName": "swan.txt",
                       "zinStep": 20.0,
                       "cacheDir": self._CACHEDIR,
                       "zoutStep": 20.0,
                       "expandStep": 5,
                       "collapseStep": 5,
                       }
        self._prodir = join(home_dir, "swan")

        # preferences have to be present for the base.
        self.load_preferences()

        self._my_storage = MyStorage(program_dir, self._preferences["cacheDir"])
        # }
        self.setWindowTitle(title)

        # connect channel selection
        self.ui.tools.selector.doChannel.connect(self.do_channel)
        self.ui.plotGrid.child.indicator_toggle.connect(self.plot_all)
        self.ui.plotGrid.child.visibility_toggle.connect(self._my_storage.changeVisibility)

        # connect loading progress
        self._my_storage.progress.connect(self.set_progress)

        # shortcut reference
        self.plots = self.ui.plotGrid.child
        self.selector = self.ui.tools.selector
        self.virtual_units_view = self.ui.virtual_units_view

        # connect channel loading
        self.virtual_units_view.load.connect(self.load_channel)

        # store all views in one list for easy access
        self.views = [
            self.ui.mean_waveforms_view,
            self.ui.isi_histograms_view,
            self.ui.rate_profiles_view,
            self.ui.pca_3d_view,
        ]

        self.check_dirs()

        self.doPlot.connect(self.plots.do_plot)

        # connect all views for update
        for view in self.views:
            self.doPlot.connect(view.do_plot)
            view.refresh_plots.connect(self.refresh_views)

            view.sig_clicked.connect(self.plots.highlight_plot)
            self.plots.plot_selected.connect(view.highlight_curve_from_plot)

        # setting up the progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.ui.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()

        self._default_gui_state = self.saveState()
        self.saved_gui_state = self._default_gui_state

        # starting memory usage task
        timer = QtCore.QTimer(self)
        self.timer = timer
        self.memorytask = MemoryTask(timer, self.ui.statusbar)
        self.memorytask.start_timer()

        self.showMaximized()

    @QtCore.pyqtSlot(name="")
    def on_action_new_project_triggered(self):
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

                channel = self._my_storage.get_channel()

                success = self._my_storage.load_project(self._prodir, self._preferences["projectName"], channel, files)

                if success and self.do_channel(self._my_storage.get_channel(), self._my_storage.get_last_channel()):
                    files_str = self._my_storage.get_files(as_string=True, only_basenames=True)

                    self.save_project()
                    self.update_project()
                    self.reset_dirty()
                    self.selector.select_only(self._my_storage.get_channel())
                    self.set_status("Created new project successfully.")
                else:
                    self.set_status("No files given. Nothing loaded.")

    @QtCore.pyqtSlot(name="")
    def on_action_load_project_triggered(self):
        """
        This method is called if you click on *File->Load Project*.
        
        You have to choose a .txt project file which contains correct paths to the data files.
        Loads the project by reading the .txt file and the .vum file.
        
        """
        if self.dirty_project():
            dialog_options = QtWidgets.QFileDialog.Options()
            dialog_options |= QtWidgets.QFileDialog.DontUseNativeDialog
            filename, nonsense = QtWidgets.QFileDialog.getOpenFileName(parent=None,
                                                                       caption="Choose saved project file",
                                                                       directory=self._prodir, options=dialog_options
                                                                      )
            if filename:
                (prodir, proname) = split(filename)

                channel = self._my_storage.get_channel()

                success = self._my_storage.load_project(prodir, proname, channel)

                if success and self.do_channel(self._my_storage.get_channel(), self._my_storage.get_last_channel()):
                    self.save_project()
                    self.update_project()
                    self.reset_dirty()
                    self.find_saved()
                    self.selector.select_only(self._my_storage.get_channel())
                    self.set_status("Loaded project successfully.")
                else:
                    self.set_status("No files given. Nothing loaded.")

    @QtCore.pyqtSlot(name="")
    def on_action_save_project_triggered(self):
        """
        This method is called if you click on *File->Save Project*.
        
        Works like :func:`on_action_save_as_triggered()` but without asking you to type in a save name.
        
        """
        if self.check_project():
            self.save_project()

    @QtCore.pyqtSlot(name="")
    def on_action_save_as_triggered(self):
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
            dialog_options = QtWidgets.QFileDialog.Options()
            dialog_options |= QtWidgets.QFileDialog.DontUseNativeDialog
            filename, nonsense = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                                                                       caption="Choose a name for the savefiles",
                                                                       directory=self._prodir,
                                                                       options=dialog_options)
            if filename:
                self._my_storage.save_project_as(filename)
                self.update_project()
                self.save_project()

    @QtCore.pyqtSlot(name="")
    def on_action_load_connector_map_triggered(self):
        """
        This method is called if you click on *File->Load connector map*.
        
        Loads a connector map given as a .csv file.
        
        Delegates the loading to :func:`load_connector_map`.
        
        """
        dialog_options = QtWidgets.QFileDialog.Options()
        dialog_options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, nonsense = QtWidgets.QFileDialog.getOpenFileName(parent=None,
                                                                   caption="Load the connector file",
                                                                   directory=self._prodir,
                                                                   options=dialog_options)
        try:
            self.load_connector_map(filename)
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Loading error", "The connector map could not be loaded!")

    @QtCore.pyqtSlot(name="")
    def on_action_export_to_csv_triggered(self):
        """
        This method is called if you click on *File->Export to csv*.

        Exports the virtual unit mappings to a csv file.

        """
        dialog_options = QtWidgets.QFileDialog.Options()
        dialog_options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, nonsense = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                                                                   caption="Save .csv file...",
                                                                   directory=self._prodir,
                                                                   options=dialog_options)
        if filename:
            try:
                if not filename.endswith(".csv"):
                    filename += ".csv"
                Export.export_csv(filename, self._my_storage.get_mappings())
            except IOError:
                QtWidgets.QMessageBox.critical(None, "Export error", "The virtual unit maps could not be exported")

    @QtCore.pyqtSlot(name="")
    def on_action_export_to_odml_triggered(self):
        """
        This method is called if you click on *File->Export to odML*.

        Exports the virtual unit mappings to an odML file.

        """
        dialog_options = QtWidgets.QFileDialog.Options()
        dialog_options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, nonsense = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                                                                   caption="Save .odml file...",
                                                                   directory=self._prodir,
                                                                   options=dialog_options)
        if filename:
            try:
                if not filename.endswith(".odml"):
                    filename += ".odml"
                Export.export_odml(filename, self._my_storage.get_mappings())
            except IOError:
                QtWidgets.QMessageBox.critical(None, "Export error", "The virtual unit maps could not be exported")

    @QtCore.pyqtSlot(name="")
    def on_action_quit_triggered(self, event):
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

    @QtCore.pyqtSlot(name="")
    def on_action_recalculate_mapping_triggered(self):
        """
        This method is called if you click on *Edit->Recalculate mapping*.
        
        Delegates the calculating to another class. Updates the overview.
        
        See :func:`src.mystorage.MyStorage.recalculate`.
        
        """
        if self._my_storage.has_project():

            implementations = ["SWAN Implementation",
                               "Old Implementation"]

            dialog = QtWidgets.QInputDialog(self)
            answer, okay = dialog.getItem(dialog,
                                          "Recalculate mapping",
                                          "WARNING! This will irreversibly change the current mapping!"
                                          "\n\nChoose the mapping algorithm to implement:",
                                          implementations,
                                          0, editable=False
                                          )

            if answer and okay:
                mapping = implementations.index(answer)

                QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                self._my_storage.recalculate(mapping, parent=self)
                self._current_dirty = True
                self._global_dirty = True
                self.plots.set_all_for_update()
                self.plot_all()
                self.plots.set_tooltips(self._my_storage.get_tooltips())
                QtWidgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(name="")
    def on_action_revert_mapping_triggered(self):
        """
        This method is called if you click on *Edit->Revert mapping*.
        
        Delegates the reverting to another class. Updates the overview.
        
        See :func:`src.mystorage.MyStorage.revert`.
        
        """
        if self._my_storage.has_project():
            answer = QtWidgets.QMessageBox.question(None, "Revert mapping", "Are you sure you want to do this?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    defaultButton=QtWidgets.QMessageBox.No)

            if answer == QtWidgets.QMessageBox.Yes:
                self._my_storage.revert()
                self.reset_current_dirty()
                self.plots.set_all_for_update()
                self.plot_all()
                self.plots.set_tooltips(self._my_storage.get_tooltips())

    @QtCore.pyqtSlot(name="")
    def on_action_swap_triggered(self):
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
            plot_1.set_for_update()
            plot_2.set_for_update()
            session = plot_1.pos[0]
            unit_id_1 = plot_1.pos[1]
            unit_id_2 = plot_2.pos[1]

            # swapping
            self._my_storage.swap(session, unit_id_1, unit_id_2)
            self.plot_all()
            self.plots.reset_selection()

            # setting tooltips
            self.plots.swap_tooltips(plot_1, plot_2)

            self._current_dirty = True
            self._global_dirty = True

    @QtCore.pyqtSlot(name="")
    def on_action_zoom_in_triggered(self):
        """
        This method is called if you click on *Edit->Zoom in*.
        
        Zooms the overview in. The zoom step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.zoom_in(self._preferences["zinStep"])

    @QtCore.pyqtSlot(name="")
    def on_action_zoom_out_triggered(self):
        """
        This method is called if you click on *Edit->Zoom out*.
        
        Zooms the overview out. The zoom step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.zoom_out(self._preferences["zoutStep"])

    @QtCore.pyqtSlot(name="")
    def on_action_expand_overview_triggered(self):
        """
        This method is called if you click on *Edit->Expand overview*.
        
        Increases the y range of the plots in the overview.
        The step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.expand(self._preferences["expandStep"])

    @QtCore.pyqtSlot(name="")
    def on_action_collapse_overview_triggered(self):
        """
        This method is called if you click on *Edit->Collapse overview*.
        
        Decreases the y range of the plots in the overview.
        The step can be set in the preferences.
        
        See :class:`src.preferences_dialog.Preferences_Dialog`.
        
        """
        self.plots.collapse(self._preferences["collapseStep"])

    @QtCore.pyqtSlot(name="")
    def on_action_preferences_triggered(self):
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
            self._my_storage.set_cache_dir(pref["cacheDir"])

    @QtCore.pyqtSlot(name="")
    def on_action_tutorials_triggered(self):
        """
        This method is called if you click on *Help->Tutorials*.
        
        Shows you tutorials and help for this application.
        
        """
        p = os.path.join(self._program_dir, "doc", "build", "html", "tutorial.html")
        d = "file://" + p
        web.open_new_tab(d)

    @QtCore.pyqtSlot(name="")
    def on_action_about_triggered(self):
        """
        This method is called if you click on *Help->About*.
        
        Shows you information about the application.
        
        """
        QtWidgets.QMessageBox.information(None, "About", about)

    @QtCore.pyqtSlot(name="")
    def on_action_revert_state_triggered(self):
        """
        This method is called if you click on *View->Revert GUI State*.
        
        Restores the GUI to it's default configuration.
        """

        self.restoreState(self._default_gui_state)

    @QtCore.pyqtSlot(name="")
    def on_action_restore_state_triggered(self):
        """
        This method is called if you click on *View->Restore GUI State*.

        Restores the GUI to the previously saved configuration. Restores to default
        configuration if no saves were performed.
        """

        self.restoreState(self.saved_gui_state)

    @QtCore.pyqtSlot(name="")
    def on_action_save_state_triggered(self):
        """
        This method is called if you click on *View->Save GUI State*.

        Saves the current configuration of the GUI to be restored later.
        """

        self.saved_gui_state = self.saveState()

    def do_channel(self, channel, lastchannel, automatic_mapping=0):
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
        if self._my_storage.has_project() and not self._my_storage.is_loading():
            # initialize the progress bar
            self.progress_bar.setValue(0)
            self.progress_bar.show()

            self.check_cache()

            # let the user know that loading can be take some time
            self.memorytask.stop_timer()
            self.set_status("Loading... This may take a while...", 0)

            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            # checking if the last channel's mapping was dirty
            if self._current_dirty:
                self.selector.set_dirty(lastchannel, True)

            self._current_dirty = self.selector.get_item(channel).dirty

            # loading
            (n, m) = self._my_storage.load_channel(channel)

            # plotting
            self.plots.reset_selection()
            data = self._my_storage.get_data()
            self.plots.make_plots(n, m, data.get_dates())

            if any(data.total_units_per_block):
                min0, max0 = data.get_yscale()
            else:
                min0, max0 = [-100, 100]
            self.plots.set_yranges(min0, max0)

            self.plot_all()

            self.ui.set_program_title(self, self._preferences["projectName"] + " | " + "Channel " + str(
                channel) + " | " + title)

            # setting tooltips
            self.plots.set_tooltips(self._my_storage.get_tooltips())

            self.progress_bar.hide()
            QtWidgets.QApplication.restoreOverrideCursor()
            self.memorytask.start_timer()
            return True

        elif self._my_storage.is_loading():
            self.selector.select_only(self._my_storage.get_channel())
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
        if self._my_storage.has_project():
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            vum = self._my_storage.get_map()
            data = self._my_storage.get_data()
            vum_all = self._my_storage.get_mappings()

            if i is not None and j is not None:
                vum.set_visible(i, j, visible)

            self.doPlot.emit(vum, data)
            if vum_all:
                self.virtual_units_view.do_plot(vum_all, data)

            QtWidgets.QApplication.restoreOverrideCursor()

    def refresh_views(self):

        if self._my_storage.has_project():
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            vum = self._my_storage.get_map()
            data = self._my_storage.get_data()

            # plotting
            self.plots.do_plot(vum, data)
            for view in self.views:
                view.do_plot(vum, data)

            QtWidgets.QApplication.restoreOverrideCursor()

    def set_progress(self, i):
        """
        Sets the progress in the status bar.

        **Arguments**
                
            *i* (integer):
                The value to be set.
        
        """
        self.progress_bar.setValue(i)

    def show_progress_bar(self, show):
        """
        Shows or hides the progress bar.

        **Arguments**
                
            *show* (boolean):
                Whether or not the progress bar should be shown.
        
        """
        if show:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

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

    def dirty_project(self):
        """
        Lets you save your project before losing your progress.
        
        Shows you a confirmation dialog and if you accept, the project
        will be saved.
        
        """
        if self._global_dirty:
            answer = QtWidgets.QMessageBox.question(

                self, "Confirmation",
                "There are unsaved changes.\nDo you want to save your project first?",
                buttons=QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                defaultButton=QtWidgets.QMessageBox.Yes

            )
            if answer == QtWidgets.QMessageBox.Yes:
                self.save_project()
                return True
            elif answer == QtWidgets.QMessageBox.No:
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
        if self._my_storage.has_project():
            (prodir, proname) = split(self._my_storage.get_project_path())
            vumname = basename(self._my_storage.get_map_path())

    def check_project(self):
        """
        Checks if there is currently a project loaded.
         
            **Returns**: boolean
                Whether or not there is a project loaded.
         
        """
        if not self._my_storage.has_project():
            QtWidgets.QMessageBox.warning(self, "Error", "No project loaded.")
            return False
        else:
            return True

    def save_project(self):
        """
        Saves the project.
        
        See :func:`src.mystorage.MyStorage.save_project`.
        
        """
        self._my_storage.save_project()
        self.reset_dirty()
        self.find_saved()
        self.set_status("Saved project successfully")

    def reset_dirty(self):
        """
        Resets the project to a not dirty state.
        
        """
        self._current_dirty = False
        self._global_dirty = False
        self.selector.reset_dirty()

    def find_saved(self):
        vum_all = self._my_storage.get_mappings()
        self.selector.find_saved(vum_all)

    def reset_current_dirty(self):
        """
        Resets the current channel.

        """
        self._current_dirty = False
        self.selector.set_dirty(self._my_storage.get_channel(), False)
        if len(self.selector.get_dirty_channels()) == 0:
            self._global_dirty = False

    def check_dirs(self):
        """
        Creates all necessary directories.
        No error is raised if they exist.
        
        """
        data_dir = join(self._CACHEDIR, "data")
        # if not isdir(data_dir):
        #     mkdir(data_dir)
        pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
        self.check_cache()

    def check_cache(self):
        """
        Creates cache directory.
        If it exists, no error is raised.
        
        """
        # if not isdir(self._preferences["cacheDir"]):
        #     mkdir(self._preferences["cacheDir"])
        pathlib.Path(self._preferences["cacheDir"]).mkdir(parents=True, exist_ok=True)

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

                self.selector.select_only(self._my_storage.get_channel())
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
