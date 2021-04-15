"""
In this module you can find the :class:`FileDialog` which lets
you choose files from one directory.
"""
import os
from os import curdir
from pyqtgraph.Qt import QtWidgets

from swan.gui.file_dialog_ui import FileDialogUI


class FileDialog(QtWidgets.QDialog):
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

    def __init__(self, fileext=".pkl", *args, **kwargs):
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
        super(FileDialog, self).__init__(*args, **kwargs)
        self.ui = FileDialogUI(self)

        self._path = None
        self._files = []
        self._fileext = fileext
        
        self.ui.selectList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.selectionList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.ui.btnBox.accepted.connect(self.accept)
        self.ui.btnBox.rejected.connect(self.reject)
        self.ui.addBtn.clicked.connect(self.add)
        self.ui.removeBtn.clicked.connect(self.remove)
        self.ui.pathBtn.clicked.connect(self.browse)
        self.ui.pathEdit.textChanged.connect(self.pathChangeEvent)
        
    def accept(self):
        """
        This method is called if you click on *Ok*.
        
        Sets the files and closes the dialog.
        
        """
        files = self._get_files()
        self._files = [os.path.join(self._path, str(f)) for f in files]
        QtWidgets.QDialog.accept(self)
    
    def reject(self):
        """
        This method is called if you click on *Cancel*.
        
        Closes the dialog without setting the files.
        
        """
        QtWidgets.QDialog.reject(self)
        
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
        self.ui.pathEdit.setText(
            QtWidgets.QFileDialog.getExistingDirectory(self, str("Choose a directory"), str(curdir))
        )
        
    def pathChangeEvent(self, newpath):
        """
        Searches the directory for files with the file extension
        that was set in the constructor and shows the file names.
        
        **Arguments**
        
            *newpath* (:class:`PyQt5.QtCore.QString`):
                The directory that was selected.
        
        """
        path = str(newpath)
        
        self._path = path
        self.ui.selectList.clear()
        files = []
        if path:
            for f in os.listdir(path):
                if f.endswith(self._fileext):
                    files.append(f)
                    
            self.fillSelectList(files)
        
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
            file_list.append(f)
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
        old_files = self._get_files()
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

    def _get_files(self):
        """
        Getter for the files.
                
            **Returns**: list of string
                The file names.
        
        """
        files = []
        for i in range(self.ui.selectionList.count()):
            files.append(self.ui.selectionList.item(i).text())
        return files
    
    def get_files(self):
        """
        Getter for the files.
        
            **Returns**: list of string
                The file names.
        
        """
        return self._files
