"""
Created on Dec 5, 2013

@author: Christoph Gollan

In this module you can find the :class:`LayerWidget` which inherits
from :class:`src.mylistwidget.MyListWidget`.

It is shown in the layer tab on the application and manages the
layer selection.
"""
from pyqtgraph.Qt import QtCore
from src.mylistwidget import MyListWidget


class LayerWidget(MyListWidget):
    """
    A list widget that manages the layer selection.
    
    The *args* and *kwargs* are passed to :class:`src.mylistwidget.MyListWidget`.
    
    """
    
    doLayer = QtCore.pyqtSignal()
    """
    Signal to emit if a layer was selected.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_layers* (dictionary):
                A dictionary containing :class:`PyQt5.QtGui.QListWidgetItem`
                as key and their row index as value.
        
        """
        MyListWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._layers = {}
        #}
        self._init_layers()
        
        
    def _init_layers(self):
        """
        Initializes the layer widget.
        
        """
        #names = ["average", "all", "standard deviation"]
        names = ["average", "standard deviation", "units", "sessions"]
        items = self.add_items(names, True)
        for item in items:
            text = str(item.text())
            self._layers[text] = item
            
    def get_checked_layers(self, layers=None):
        """
        Returns the checked layers.
        
        **Arguments**
        
            *layers* (list of string or None):
                The list of layer names to search in.
                If set to None, all layers are taken.
                Default: None
        
            **Returns**: list of string:
                The names of the checked layers.
        
        """
        checked = []
        if layers is not None:
            for l in layers:
                item = [item for item in self._layers.values() if str(item.text()) == l][0]
                if item.checkState() == QtCore.Qt.Checked:
                    checked.append(str(item.text()))
        else:
            for item in self._layers.values():
                if item.checkState() == QtCore.Qt.Checked:
                    checked.append(str(item.text()))
        return checked
    
    def get_layers(self):
        """
        Getter for the layers.
        
            **Returns**: list of string
                The layer names.
        
        """
        return self._layers.keys()
    
    def _get_layers(self):
        """
        Getter for the layers.
        
            **Returns**: list of :class:`PyQt5.QtGui.QListWidgetItem`
                The items of this widget.
        
        """
        return self._layers.values()
    
    def enable_layers(self, enable, layers):
        """
        Enables or disables layers on the widget.
        
        **Arguments**
        
            *enable* (boolean):
                Whether or not the items should be enabled.
            *layers* (list of string):
                The layers to enable/disable.
        
        """
        for l in layers:
            items = [item for key, item in self._layers.items() if key == l]
            items = items[0]
            items.setHidden(not enable)

    
    #### signal handler ####
    
    def item_changed(self, item):
        """
        Called if a layer was checked or unchecked.
        Emits a signal to the parent widget.
        
        **Arguments**
        
            *item* (:class:`PyQt5.QtGui.QListWidgetItem`):
                The item that was changed. Unused.
                    
        """
        self.doLayer.emit()
        
        
        
        
        
        