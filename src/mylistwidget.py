"""
Created on Dec 5, 2013

@author: Christoph Gollan

In this module you can find the :class:`MyListWidget` which aggregates
a :class:`PyQt5.QtGui.QListWidget` extended with some functions.

Is used as a base class to get further extensions.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from gui.mylistwidget_ui import Ui_Form


class MyListWidget(QtWidgets.QWidget):
    """
    This class is a base class for other widgets but it
    offers functions to add items to a list and getting them back.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtGui.QListWidget`.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_checkableitems* (boolean):
                Whether or not the items on this widget should be checkable.
        
        """
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.list.itemChanged.connect(self.item_changed)
        
        #properties{
        self._checkableitems = False
        #}
        
        
    #### general methods ####    
        
    def add_items(self, labels, checkable=False, checkState=QtCore.Qt.Unchecked):
        """
        Adds items to this widget.
        
        **Arguments**
        
            *labels* (list of string):
                The labels to use for the items.
            *checkable* (boolean):
                Whether or not the items should be checkable.
                Default: False
            *checkState* (PyQt check state):
                If checkable, the initial check state of the items.
                Default: PyQt5.QtCore.Qt.Unchecked
        
        """
        self.ui.list.clear()
        items = []
        self._checkableitems = checkable
        for label in labels:
            item = QtGui.QListWidgetItem(label)
            if checkable:
                item.setCheckState(checkState)
            self.ui.list.addItem(item)
            items.append(item)
        return items
        
    def get_items(self):
        """
        Getter for the items on the list.
        
            **Returns**: list of :class:`PyQt5.QtGui.QListWidgetItem`
                The list of items from this widget.
        
        """
        item_list = []
        for i in xrange(self.ui.list.count()):
            item_list.append(self.ui.list.item(i))
        return item_list
    
    def get_labels(self, checkState=QtCore.Qt.Checked):
        """
        Getter for the labels of the items on the list.
        
        **Arguments**
        
            *checkState* (PyQt check state):
                The check state the items should have.
        
            **Returns**: list of string
                The labels of the items with the given check state or
                a list containing all labels if the items are not
                checkable.
        
        """
        items = self.get_items()
        if not self._checkableitems: 
            return [str(it.text()) for it in items]
        selection = []
        for it in items:
            if it.checkState() == checkState:
                selection.append(str(it.text()))
        return selection
    
    
    #### signal handler ####
    
    def item_changed(self, item):
        """
        Does nothing. Can be overwritten.

        **Arguments**
        
            *item* (:class:`PyQt5.QtGui.QListWidgetItem`):
                The item that was changed.
        
        """
        pass
