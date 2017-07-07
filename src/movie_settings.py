"""
Created on Aug 19, 2014

@author: Christoph Gollan

In this module you can find the :class:`MovieSettings` class which is used
by :class:`src.mplwidgetmovie.MplWidgetMovie` to show a settings dialog.

You can change some settings for the movie tab on the main window here.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.movie_settings_ui import Ui_movieSettings


class MovieSettings(QtWidgets.QDialog):
    """
    A class to show and change movie settings for 
    a :class:`src.mplwidgetmovie.MplWidgetMovie`.
   
    Settings that can be made:

    ====================  ====================  ====================
    Settings name         Dictionary key         Valid value(s)
    ====================  ====================  ====================
    Averaging range       avRange               1 - 1000
    Slide skip            skip                  1 - 1000
    Slides per second     sps                   1, 2, 4, 5
    Title time format     time                  original, s, ms
    ====================  ====================  ====================
    
    .. warning::
   
        The keys have to exist in the settings. 

    **Arguments**
    
        *settings* (dictionary):
            The movie settings given as (key, value) pares.

    """
    
    def __init__(self, settings):
        """
        **Properties**
    
            *_settings* (dictionary):
                The movie settings given as (key, value) pares.
            *_spsItems* (dictionary):
                The sps options mapped to their key in the
                combo box.
            *_timeItems* (dictionary):
                The time format options mapped to their key 
                in the combo box.
        
        """
        QtGui.QDialog.__init__(self)
        self.ui = Ui_movieSettings()
        self.ui.setupUi(self)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        
        #properties{
        self._settings = settings
        self._spsItems = {"1":0,
                          "2":1,
                          "4":2,
                          "5":3}
        self._timeItems = {"original":0,
                           "seconds":1,
                           "milliseconds":2}
        #}
        
        self.ui.rangeEdit.textChanged.connect(self.checkRange)
        self.ui.skipEdit.textChanged.connect(self.checkSkip)
        
        self.setup()
        
        
    def accept(self):
        """
        This method is called if you click on *Ok*.
        
        Closes the dialog and sets all settings if they are correct 
        but if not, a message will be shown and the dialog stays open.
        
        """
        self.checkAll()
        if str(self.ui.errorLabel.text()):
            QtGui.QMessageBox.critical(self, "Error", "There are still wrong inputs")
        else:
            avRange = int(str(self.ui.rangeEdit.text()))
            skip = int(str(self.ui.skipEdit.text()))
            sps = int(str(self.ui.spsCombo.itemText(self.ui.spsCombo.currentIndex())))
            timeU = str(self.ui.timeCombo.itemText(self.ui.timeCombo.currentIndex()))
            self._settings["avRange"] = avRange
            self._settings["skip"] = skip
            self._settings["sps"] = sps
            self._settings["time"] = timeU
            QtGui.QDialog.accept(self)
            
    def reject(self):
        """
        This method is called if you click on *Cancel*.
        
        Closes the dialog without changing the settings.
        
        """
        self.reset()
        QtGui.QDialog.reject(self)
        
    def setup(self):
        """
        Sets up the dialog.
        
        """
        self.reset()
    
    def reset(self):
        """
        Resets all settings.
        
        """
        self.ui.rangeEdit.setText(str(self._settings["avRange"]))
        self.ui.skipEdit.setText(str(self._settings["skip"]))
        self.ui.spsCombo.setCurrentIndex(self._spsItems[str(self._settings["sps"])])
        self.ui.timeCombo.setCurrentIndex(self._timeItems[self._settings["time"]])
        
    def checkRange(self, avRange):
        """
        Checks if the averaging range is correct.
        
        **Arguments**
        
            *avRange* (:class:`PyQt5.QtCore.QString`):
                The current input value for the averaging range.
                
        """
        try:
            self.ui.errorLabel.setText("")
            avRange = int(str(avRange))
            if avRange < 0 or avRange > 1000:
                raise ValueError
        except:
            self.ui.errorLabel.setText("Invalid value(s)")
    
    def checkSkip(self, skip):
        """
        Checks if the slide skip is correct.
        
        **Arguments**
        
            *skip* (:class:`PyQt5.QtCore.QString`):
                The current input value for the slide skip.
                
        """
        try:
            self.ui.errorLabel.setText("")
            skip = int(str(skip))
            if skip < 0 or skip > 1000:
                raise ValueError
        except:
            self.ui.errorLabel.setText("Invalid value(s)")

    def checkAll(self):
        """
        Checks all input values for correctness.
        
        """
        try:
            self.checkRange(self.ui.rangeEdit.text())
            if str(self.ui.errorLabel.text()):
                return
            self.checkSkip(self.ui.skipEdit.text())
            if str(self.ui.errorLabel.text()):
                return
        except:
            self.ui.errorLabel.setText("Invalid value(s)")
