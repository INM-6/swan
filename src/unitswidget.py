"""
Created on Dec 5, 2013

@author: Christoph Gollan

In this module you can find the :class:`UnitsWidget` which inherits
from :class:`src.mylistwidget.MyListWidget`.

It is shown in the units tab on the application and manages the
unit selection.
"""
from PyQt5 import QtCore
from src.mylistwidget import MyListWidget


class UnitsWidget(MyListWidget):
    """
    A list widget that manages the unit selection.
    
    The *args* and *kwargs* are passed to :class:`src.mylistwidget.MyListWidget`.
    
    """
    
    doUnits = QtCore.pyqtSignal(int, bool)
    """
    Signal to emit if a unit was selected.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_units* (dictionary):
                A dictionary containing :class:`PyQt5.QtGui.QListWidgetItem`
                as key and their row index as value.
        
        """
        MyListWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._units = {}
        #}
       
    
    #### general methods ####
        
    def init_units(self, unitnum):
        """
        Initializes the list widget.
        
        **Arguments**
        
            *unitnum* (integer):
                The number of units you want to have.
        
        """
        labels = [str(i) for i in range(1, unitnum+1)]
        items = self.add_items(labels, True, QtCore.Qt.Checked) 
        for i, item in enumerate(items, 1):
            self._units[item] = i
            
    def get_units(self):
        """
        Returs the units ids.
        
            **Returns**: list of integer
                The units ids.
        
        """
        return self._units.values()
        #items = self.get_items()
        #return [int(str(i.text())) for i in items]
            

    #### signal handler ####
    
    def item_changed(self, item):
        """
        Called if a unit was checked or unchecked.
        Emits a signal to the parent widget.
        
        **Arguments**
        
            *item* (:class:`PyQt5.QtGui.QListWidgetItem`):
                The item that was changed.
                    
        """
        i = self._units[item]-1
        visible = (item.checkState() == QtCore.Qt.Checked) 
        self.doUnits.emit(i, visible)
    
    
