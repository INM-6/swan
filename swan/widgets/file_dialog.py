"""
Created on Oct 24, 2013

@author: Christoph Gollan

In this module you can find the :class:`File_Dialog` which lets
you choose files from one directory.
"""
import os
from os import curdir
from pyqtgraph.Qt import QtGui, QtWidgets

try:
    from pyqtgraph.Qt.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = str

from swan.gui.file_dialog_ui import Ui_File_Dialog


class File_Dialog(QtWidgets.QDialog):
    """
    A file dialog which can be used to choose a directory and 
    after that you can choose specific files in this directory.
    
    You can give the file extension to search for as an argument.  
    After clicking *Ok* you can get the chosen files with :func:`get_files()`.
    
    **Arguments**
    
        *fileext* (string):
            The file extension that should be searched for.
            Default: .nev
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QDialog`.
    
    """

    def __init__(self, fileext=".nev", *args, **kwargs):
        """
        **Properties**
        
            *_path* (string):
                The (absolute) directory path.
            *_files* (list of string):
                The absolute path to the files without extension.
                Will be filled after clicking *Ok*.
            *_fileext* (string):
                The file extension that should be searched for.
                Default: .nev
            *_extlength* (integer)
                The length of the file extension.
                Is necessary for removing the extension 
                from found files.
        
        """
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.ui = Ui_File_Dialog()
        self.ui.setupUi(self)
        
        #properties{
        self._path = None
        self._files = []
        self._fileext = fileext
        self._extlength = len(self._fileext)
        #}
        
        self.ui.selectList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ui.selectionList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.ui.btnBox.accepted.connect(self.accept)
        self.ui.btnBox.rejected.connect(self.reject)
        self.ui.addBtn.clicked.connect(self.add)
        self.ui.removeBtn.clicked.connect(self.remove)
        self.ui.pathBtn.clicked.connect(self.browse)
        self.ui.pathEdit.textChanged.connect(self.pathChangeEvent)
                
    #### button handler ####
        
    def accept(self):
        """
        This method is called if you click on *Ok*.
        
        Sets the files and closes the dialog.
        
        """
        files = self._get_files(self.ui.selectionList)
        self._files = [os.path.join(self._path, str(f)) for f in files]
        QtGui.QDialog.accept(self)
    
    def reject(self):
        """
        This method is called if you click on *Cancel*.
        
        Closes the dialog without setting the files.
        
        """
        QtGui.QDialog.reject(self)
        
    def add(self):
        """
        This method is called if you click on *Add*.
        
        Adds the selected files from the left to the right list.
        
        """
        selection = self.ui.selectList.selectedItems()
        self.updateSelectionList(selection)
    
    def remove(self):
        """
        This method is called if you click on *Remove*.
        
        Removes the selected files from the right list.
        
        """
        selection = self.ui.selectionList.selectedItems()
        self.updateSelectionList(selection, True)
    
    def browse(self):
        """
        This method is called if you click on *Browse...*.
        
        Asks you for an existing directory.
        
        """
        self.ui.pathEdit.setText(QtGui.QFileDialog.getExistingDirectory(self, str("Choose a directory"), str(curdir)))
        
        
    #### event handler ####
        
    def pathChangeEvent(self, newpath):
        """
        Searches the directory for files with the file extension
        that was set in the constructor and shows the file names.
        
        **Arguments**
        
            *newpath* (:class:`PyQt5.QtCore.QString`):
                The directory that was selected.
        
        """
        #path = str(self.ui.pathEdit.text())
        path = str(newpath)
        
        self._path = path
        self.ui.selectList.clear()
        files = []
        #for p, dirs, files in os.walk(path):
        #    for f in files:
        if path:
            for f in os.listdir(path):
                if f.endswith(self._fileext):
                    files.append(f)
                    
            self.fillSelectList(files)
    
    #### general methods ####
        
    def fillSelectList(self, files):
        """
        Fills the list on the left side.
        
        **Arguments**
            
            *files* (list of string):
                The file names to fill the list with.
                The extension will be cut off.
        
        """
        files.sort()
        file_list = []
        for f in files:
            file_list.append(f[:-self._extlength])
        self.ui.selectList.addItems(file_list)
            
    def updateSelectionList(self, selection, remove=False):
        """
        Updates the list on the right side.
        
        **Arguments**
        
            *selection* (list of :class:`PyQt5.QtGui.QListWidgetItem`)
                The selected items.
            *remove* (boolean):
                Whether or not you want to remove the selected items
                from the list or add them.
                Default: False.
        
        """
        old_files = self._get_files(self.ui.selectionList)
        files = []
        if not remove:
            for item in selection:
                text = item.text()
                if text not in old_files:
                    files.append(text)
            self.ui.selectionList.addItems(files)
        else:
            for item in selection:
                text = item.text()
                i = old_files.index(text)
                old_files.remove(text)
                self.ui.selectionList.takeItem(i)
            
    def _get_files(self, listWidget):
        """
        Getter for the files.
        
        **Arguments**
        
            *listWidget* (:class:`PyQt5.QtGui.QListWidgetItem`):
                The list widget you want the file names from.
                
            **Returns**: list of string
                The file names.
        
        """
        files = []
        for i in range(listWidget.count()):
            files.append(listWidget.item(i).text())
        return files
    
    def get_files(self):
        """
        Getter for the files.
        
            **Returns**: list of string
                The file names.
        
        """
        return self._files

        
        
