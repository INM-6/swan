"""
Created on Nov 28, 2013

@author: Christoph Gollan

In this module you can find the :class:`SelectorWidget`.
It is used to represent a connector map.

The electrodes on this map are represented by 
the :class:`SelectorItem`.
"""
from PyQt5 import QtGui, QtCore, QtWidgets
from swan.gui.selector_widget_ui import Ui_Form


class SelectorWidget(QtWidgets.QWidget):
    """
    A widget that is used to represent an electrode connector map.
    
    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QWidget`.
    
    """
    
    doChannel = QtCore.pyqtSignal(int, int)
    """
    Signal to emit if there was a channel selection.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_items* (list of :class:`SelectorItem`):
                A list which contains all items this widget manages.
            *_dirty_items* (list of :class:`SelectorItem`):
                A list containing all items with the dirty property set to True.
            *_sel* (:class:`SelectorItem`):
                The currently selected item.
                Is None at program start.
            *lastchannel* (integer):
                The last selected channel.
            *currentchannel* (integer):
                The currently selected channel.
        
        """
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        #properties{
        self._items = []
        self._dirty_items = []
        self._sel = None
        self.lastchannel = 1
        self.currentchannel = 1
        #}
        self.make_grid()
        

    #### general methods ####
        
    def make_grid(self, rows=10, cols=10):
        """
        Creates a grid of widgets which represent the electrodes.
        
        **Arguments**
        
            *rows* (integer):
                The number of rows.
                Default: 10.
            *cols* (integer):
                The number of cols.
                Default: 10.
        
        """
        for i in range(rows):
            for j in range(cols):
                s = SelectorItem(self)
                s.selectChannel.connect(self.select_channel)
                s.pos = (i, j)
                self._items.append(s)
                self.ui.gridLayout.addWidget(s, i, j)
        self.set_channels()
        
    def set_channels(self, channel_list=None):
        """
        Sets the channels of the widgets.
        
        **Arguments**
        
            channel_list (list of integer or None):
                The channel list which contains the channel ids.
                If None, the default setting will be used.
        
        """
        if channel_list is not None:
            j = 0
            for i in range(9, -1, -1):
                #channels = range(1+j*10, 11+j*10)
                channels = channel_list[(j*10):(11+j*10)]
                items = [s for s in self._items if s.pos[0] == i]
                for k in range(10):
                    items[k].text = str(channels[k])
                    items[k].channel = channels[k]
                    if channels[k] == -1:
                        items[k].selectable = False
                    else:
                        items[k].selectable = True
                j += 1
        else:
            j = 0
            for i in range(9, -1, -1):
                channels = range(1+j*10, 11+j*10)
                items = [s for s in self._items if s.pos[0] == i]
                for k in range(10):
                    items[k].text = str(channels[k])
                    items[k].channel = channels[k]
                j += 1
                
    def get_item(self, channel):
        """
        Returns a :class:`SelectorItem` for the given channel.
        
        **Arguments**
        
            *channel* (integer):
                The channel id of the item.
                
            **Returns**: :class:`SelectorItem` or None
                If found, it returns the item. 
                If not, it returns None.
        
        """
        match = [i for i in self._items if channel == i.channel]
        if match:
            return match[0]
        return None

    def select_channel(self, item, channel):
        """
        Selects a channel and emits the doChannel signal
        which causes the program to change the channel.
        
        **Arguments**
       
            *item* (:class:`SelectorItem`):
                The item that should be selected.
            *channel* (integer):
                The channel id of the item.
        
        """
        self.lastchannel = self.currentchannel
        self.currentchannel = channel
        lastchannel = self.lastchannel
        self.reset_sel()
        self._sel = item
        for item in self._dirty_items:
            item.repaint()
        self.doChannel.emit(channel, lastchannel)
        
    def select_only(self, channel):
        """
        Selects the item with the given channel id but emits no signal.
        
        **Arguments**
        
            *channel* (integer):
                The channel id of the item
                that should be selected.
        
        """
        self.lastchannel = self.currentchannel
        self.currentchannel = channel
        self.reset_sel()
        item = self.get_item(channel)
        item.selected = True
        self._sel = item
        item.repaint()

    def reset_sel(self):
        """
        Resets the selected item.
        
        """
        if self._sel:
            self._sel.selected = False
            self._sel.repaint()
            
    def get_dirty_channels(self):
        """
        Returns the channels that are currently dirty.
        
            **Returns**: list of integer
                Channel ids.
        
        """
        channels = [it.channel for it in self._dirty_items]
        return channels
            
    def set_dirty(self, channel, dirty):
        """
        Sets a item as dirty or not.
        
        **Arguments**
         
            *channel* (integer):
                The channel id of the item.
            *dirty* (boolean):
                Whether or not the item is dirty.
        
        """
        item = self.get_item(channel)
        item.dirty = dirty
        if dirty:
            self._dirty_items.append(item)
        elif item in self._dirty_items:
            self._dirty_items.remove(item)
        item.repaint()
    
    def reset_dirty(self):
        """
        Resets the dirty property for all items.
        
        """
        for item in self._items:
            item.dirty = False
            item.repaint()
        self._dirty_items = []
        
    def sizeHint(self):
        return QtCore.QSize(300, 300)
    
    def heightForWidth(self, width):
        return width


class SelectorItem(QtWidgets.QWidget):
    """
    Is used by the :class:`SelectorWidget`.
    
    Represents a electrode channel.

    The *args* and *kwargs* are passed to :class:`PyQt5.QtWidgets.QWidget`.
    
    """
    
    selectChannel = QtCore.pyqtSignal("PyQt_PyObject", int)
    """
    Signal to emit if this item is selected.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *selected* (boolean):
                Whether or not the widget is selected.
            *selectable* (boolean):
                Whether or not the widget is selectable.
            *dirty* (boolean):
                Whether or not the widget is dirty.
            *text* (string):
                The text that is shown by the widget.
            *channel* (integer):
                The channel that is represented by the widget.
            *pos* (tuple of integer):
                The position in the grid.
                Format: (row, col)
            *inFocus* (boolean):
                Whether or not this widget has a mouse hovering it.
        
        """
        QtWidgets.QWidget.__init__(self, *args, **kwargs)      
        
        self.setMinimumSize(20, 20)
        
        #properties{
        self.selected = False
        self.selectable = True
        self.dirty = False
        self.text = "0"
        self.channel = 0
        self.pos = None
        self.inFocus = False
        #}
        self.setMouseTracking(True)
        
    
    #### event handler ####    
        
    def paintEvent(self, event):
        """
        Paints the text and the background depending on
        the state of the item.
        
        **Arguments**
            
            *event* (:class:`PyQt4.QtCore.QEvent`)
            
        """
        self.setAutoFillBackground(True)
        pal = QtGui.QPalette()
        #white when normal
        pal.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        pal2 = QtGui.QPalette()
        #dark gray when selected
        pal2.setColor(QtGui.QPalette.Background, QtCore.Qt.darkGray)
        pal3 = QtGui.QPalette()
        #black when deactivated
        pal3.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        pal4 = QtGui.QPalette()
        col4 = QtGui.QColor(255, 140, 0)
        #orange when dirty
        pal4.setColor(QtGui.QPalette.Background, col4)
        pal5 = QtGui.QPalette()
        #light gray when mouse hover
        pal5.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
        
        if self.inFocus and self.selectable:
            self.setPalette(pal5)
        else:
            if not self.selectable:
                self.setPalette(pal3)
            else:
                if self.selected:
                    self.setPalette(pal2)
                elif self.dirty:
                    self.setPalette(pal4)
                else:
                    self.setPalette(pal)
            
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()
        
    def drawText(self, event, qp):
        """
        Paints the text.
        
        **Arguments**
            
            *event* (:class:`PyQt4.QtCore.QEvent`)
            
            *qp* (:class:`PyQt4.QtGui.QPainter`):
                The painter that is used to draw the text.
        
        """
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Arial', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)   

    def mousePressEvent(self, event):
        """
        This method is called if you click on this widget.
        
        Only left mouse clicks are accepted if this widget is 
        selectable and not already selected.
        
        **Arguments**
            
            *event* (:class:`PyQt4.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton and self.selectable and not self.selected:
            QtWidgets.QWidget.mousePressEvent(self, event)
            self.selected = True
            self.selectChannel.emit(self, self.channel)
            self.repaint()
            event.accept()
        else:
            event.ignore()
            
    def enterEvent(self, event):
        """
        This method is called if the mouse enters this widget.
        
        Sets this widget in focus.
        
        **Arguments**
            
            *event* (:class:`PyQt4.QtCore.QEvent`)
        
        """
        self.inFocus = True
        self.repaint()
        event.accept()
    
    def leaveEvent(self, event):
        """
        This method is called if the mouse leaves this widget.
        
        Sets this widget out of focus.
        
        **Arguments**
            
            *event* (:class:`PyQt4.QtCore.QEvent`)
        
        """
        self.inFocus = False
        self.repaint()
        event.accept()

        
