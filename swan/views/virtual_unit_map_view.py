'''
Created on Jun 10, 2014

@author: gollan
'''
import sys
from os.path import curdir, split

p = sys.path[0]
p = split(p)[0]
if not p:
    p = curdir
sys.path.insert(1, p)

try:
    import cPickle as pickle
except ImportError:
    import pickle

from PyQt4 import QtGui
from gui.vumv_ui import Ui_VumV


class VumV(QtGui.QWidget):
    """
    A viewer for Virtual Unit Maps.
    
    """
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_VumV()
        self.ui.setupUi(self)
        
        #properties {
        self.vum = None
        #}
        
        #connect button click
        self.ui.browseBtn.clicked.connect(self.browse)
        #connect path edit
        self.ui.pathEdit.textChanged.connect(self.pathChange)        
        #connect channel selection
        self.ui.channelBox.currentIndexChanged.connect(self.channelChange)


    def browse(self):
        """
        Shows a dialog to choose a file.
        
        """
        path = QtGui.QFileDialog.getOpenFileName(self, "Open file")
        if path:
            self.ui.pathEdit.setText(path)

    def pathChange(self, path):
        """
        Checks the path in the pathEdit and loads the file if it was correct.
        
        Args:
            path (str):
                The path to the file.
        
        """
        if path:
            path = str(path)
            if not path.endswith(".vum"):
                QtGui.QMessageBox.warning(self, "Error", "Not a .vum file!")
            else:
                try:
                    with open(path, "rb") as fn:
                        vum = pickle.load(fn)
                        self._load(vum)
                except:
                    QtGui.QMessageBox.warning(self, "Error", "Could not read {}!".format(path))
                    
    def channelChange(self, i):
        """
        Changes the selected channel.
        
        """
        text = str(self.ui.channelBox.itemText(i))
        if text == "":
            return
        self.ui.details.item(0, 0).setText(str(self.vum[text]["channel"]))
        
        self.ui.content.clear()
        
        files = self.vum["files"]
        mapping = self.vum[text]
        keys = [k for k in mapping.keys() if k != "channel"]
        values = mapping.values()

        self.ui.content.setColumnCount(len(files))        
        self.ui.content.setRowCount(len(keys))
        
        for i, f in enumerate(files):
            item = QtGui.QTableWidgetItem(f)
            self.ui.content.setHorizontalHeaderItem(i, item)
        
        for i, k in enumerate(keys):
            item = QtGui.QTableWidgetItem(str(k))
            self.ui.content.setVerticalHeaderItem(i, item)
            
            for j, t in enumerate(mapping[k]):
                if t[1]:
                    t = str(t[1])
                else:
                    t = ""
                item = QtGui.QTableWidgetItem(t)
                self.ui.content.setItem(i, j, item)
            

    def _load(self, vum):
        """
        Loads the content of the vum file.
        
        """
        self.vum = vum
        self.ui.channelBox.clear()
        files = vum["files"]
        self.ui.details.item(1, 0).setText("\n".join(files))
        keys = [k for k in vum.keys() if k != "files"]
        self.ui.channelBox.addItems(keys)
        


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    vumv = VumV()
    vumv.show()
    sys.exit(app.exec_())