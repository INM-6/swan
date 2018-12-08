"""
Created on Apr 15, 2014

@author: Christoph Gollan

In this module you can find the :class:`Preferences_Dialog` which shows
the preferences for this application and lets the user change them.
And of course the user inputs will be checked.
"""
import re
from PyQt5 import QtGui, QtWidgets
from swan.gui.preferences_dialog_ui import Ui_Preferences


class Preferences_Dialog(QtWidgets.QDialog):
    """
    The class for showing, changing and checking preferences.
    
    The UI consists of two parts, one list on the left where you can
    choose the category and the grouped settings on the right which
    belong to the category.
    
    
    The following settings can be made:
    
    ======================  ======================  ======================
    Settings name           Dictionary key           Valid value(s)
    ======================  ======================  ======================
    Default project name    defaultProName          File name
    Cache location          cacheDir                Existing directory
    Zoom in step            zinStep                 1 - 200
    Zoom out step           zoutStep                1 - 200
    Expand step             expandStep              1 - 500
    Collapse step           collapseStep            1 - 500
    ======================  ======================  ======================

    .. warning::
    
        The keys have to exist in both the preferences 
        and the PREFS dictionary.
    
    **Arguments**
    
        *preferences* (dictionary):
            The current preferences given as (key, value) pares.
        *PREFS* (dictionary):
            The default preferences given as (key, value) pares.
            These are needed to restore the defaults.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QDialog`.
    
    """

    def __init__(self, preferences, PREFS, *args, **kwargs):
        """
        **Properties**
        
            *_preferences* (dictionary):
                The current preferences given as (key, value) pares.
            *_PREFS* (dictionary):
                The default preferences given as (key, value) pares.
            *_options* (dictionary):
                A dictionary to map the :class:`PyQt4.QtGui.QListWidgetItem`
                to an index from the :class:`PyQt4.QtGui.QStackedWidget`.
        
        """
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        
        #properties{
        self._preferences = preferences
        self._PREFS = PREFS
        self._options = {}
        #}
        
        self.ui.optionsList.itemSelectionChanged.connect(self.itemChanged)
        self.ui.defaultBtn.clicked.connect(self.onRestoreDefault)
        #option: General
        self.ui.projectNameEdit.textChanged.connect(self.checkName)
        self.ui.cacheDirEdit.textChanged.connect(self.checkCache)
        self.ui.cacheDirBtn.clicked.connect(self.onCacheDir)
        #option: Overview
        self.ui.zinStepEdit.textChanged.connect(self.checkZoomInStep)
        self.ui.zoutStepEdit.textChanged.connect(self.checkZoomOutStep)
        self.ui.expandStepEdit.textChanged.connect(self.checkExpandStep)
        self.ui.collapseStepEdit.textChanged.connect(self.checkCollapseStep)
        
        self.setup()
    
    
    #### signal handler ####
    
    def itemChanged(self):
        """
        Shows the settings which belong to the currently 
        selected category.
        
        """
        item = self.ui.optionsList.selectedItems()[0]
        i = self._options[str(item)]
        self.ui.optionsView.setCurrentIndex(i)
    
    def onRestoreDefault(self):
        """
        This method is called if you click on *Restore default*.
        
        Restores the default settings. You will be asked to confirm
        this decision.
        
        """
        if QtGui.QMessageBox.question(self, "Restore default preferences", "Are you sure?", 
                                      buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
                                      defaultButton=QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self._preferences = self._PREFS
            self._set_preferences(self._preferences)
        
    def accept(self):
        """
        This method is called if you click on *Ok*.
    
        Closes the dialog but only if the inputs are correct.
        If not, the dialog will stay open and you get a message.

        """
        self.checkAll()
        if str(self.ui.errorLabel.text()):
            QtGui.QMessageBox.critical(self, "Error", "There are still wrong inputs")
        else:
            QtGui.QDialog.accept(self)
    
    def checkName(self, name):
        """
        Checks if the default project name is correct.
        If so, the name will be set.
        
        **Arguments**
        
            *name* (:class:`PyQt4.QtCore.QString`):
                The current input value for the default project name.
        
        """
        result = re.match('^[a-zA-Z]+\w*.txt', name)
        if not result:
            self.ui.errorLabel.setText("There are wrong input values")
        else:
            self._preferences["projectName"] = str(name)
            self.ui.errorLabel.setText("")
            
    def checkCache(self, dirname):
        """
        Checks if the cache location is correct.
        If so, the location will be set.
        
        **Arguments**
        
            *dirname* (:class:`PyQt4.QtCore.QString`):
                The current input value for the cache location.
        
        """
        self._preferences["cacheDir"] = str(dirname)
        
    def onCacheDir(self):
        """
        This method is called if you click on *browse...* next to the
        cache location label.
        
        Asks you for an existing directory.
        
        """
        text = str(QtGui.QFileDialog.getExistingDirectory(self, "Cache location"))
        if text:
            self.ui.cacheDirEdit.setText(text)
        
    def checkZoomInStep(self, step):
        """
        Checks if the zoom in step is correct.
        If so, the step will be set.
        Checking is made by :func:`checkZoomStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the zoom in step.
        
        """
        try:
            self.checkZoomStep(step)
            self._preferences["zinStep"] = int(step)
            self.ui.errorLabel.setText("")
        except ValueError:
            self.ui.errorLabel.setText("There are wrong input values")
    
    def checkZoomOutStep(self, step):
        """
        Checks if the zoom out step is correct.
        If so, the step will be set.
        Checking is made by :func:`checkZoomStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the zoom out step.
        
        """
        try:
            self.checkZoomStep(step)
            self._preferences["zoutStep"] = int(step)
            self.ui.errorLabel.setText("")
        except ValueError:
            self.ui.errorLabel.setText("There are wrong input values")
        
    def checkZoomStep(self, step):
        """
        Checks if the zoom step is correct.
        
        Is used by :func:`checkZoomOutStep` and :func:`checkZoomInStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the zoom step.
                
            **Raises**: ValueError
                If the input value is incorrect.
        
        """
        try:
            step = int(step)
            if step < 1 or step > 200:
                raise ValueError
        except:
            raise ValueError
    
    def checkExpandStep(self, step):
        """
        Checks if the expand step is correct.
        If so, the step will be set.
        Checking is made by :func:`checkRangeStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the expand step.
                
        """
        try:
            self.checkRangeStep(step)
            self._preferences["expandStep"] = int(step)
            self.ui.errorLabel.setText("")
        except ValueError:
            self.ui.errorLabel.setText("There are wrong input values")
    
    def checkCollapseStep(self, step):
        """
        Checks if the collapse step is correct.
        If so, the step will be set.
        Checking is made by :func:`checkRangeStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the collapse step.
                
        """
        try:
            self.checkRangeStep(step)
            self._preferences["collapseStep"] = int(step)
            self.ui.errorLabel.setText("")
        except ValueError:
            self.ui.errorLabel.setText("There are wrong input values")
        
    def checkRangeStep(self, step):
        """
        Checks if the expand/collapse step is correct.
        
        Is used by :func:`checkExpandStep` and :func:`checkCollapseStep`.
        
        **Arguments**
        
            *step* (:class:`PyQt4.QtCore.QString`):
                The current input value for the expand/collapse step.
                
            **Raises**: ValueError
                If the input value is incorrect.
        
        """
        try:
            step = int(step)
            if step < 1 or step > 500:
                raise ValueError
        except:
            raise ValueError
        
    def checkAll(self):
        """
        Checks all input values for correctness.
        
        """
        try:
            self.checkName(self.ui.projectNameEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkCache(self.ui.cacheDirEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkZoomInStep(self.ui.zinStepEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkZoomOutStep(self.ui.zoutStepEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkExpandStep(self.ui.expandStepEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkCollapseStep(self.ui.collapseStepEdit.text())
            if str(self.ui.errorLabel.text()):
                return
        except:
            self.ui.errorLabel.setText("There are wrong input values")
        
    
    #### general methods ####
    
    def setup(self):
        """
        Sets up the dialog.
        
        """
        #getting a map for the options
        for i in range(self.ui.optionsList.count()):
            item = self.ui.optionsList.item(i)
            self._options[str(item)] = i
        self._set_preferences(self._preferences)
        
    def _set_preferences(self, pref):
        """
        Sets the preferences.
        
        **Arguments**
        
            *pref* (dictionary):
                The preferences given as (key, value) pares.
        
        """
        #setting up the given preferences
        #option: general
        self.ui.projectNameEdit.setText(pref["projectName"])
        self.ui.cacheDirEdit.setText(pref["cacheDir"])
        #option: overview
        self.ui.zinStepEdit.setText(str(pref["zinStep"]))
        self.ui.zoutStepEdit.setText(str(pref["zoutStep"]))
        self.ui.expandStepEdit.setText(str(pref["expandStep"]))
        self.ui.collapseStepEdit.setText(str(pref["collapseStep"]))
        
    def get_preferences(self):
        """
        Gets the preferences.
        
            **Returns**: dictionary
                The preferences given as (key, value) pares.
        
        """
        return self._preferences
        
