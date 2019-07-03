#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:27:23 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph import mkColor


class IndicatorWidget(QtWidgets.QWidget):
    """
    A class based on QWidget used to indicate the row/column.
    """

    select_indicator = QtCore.pyqtSignal(object)

    def __init__(self, text, indicator_type, position, width=200, height=150, const_dim=60, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.indicator_type = indicator_type

        if self.indicator_type == 'pivot':
            self.row = -1
            self.col = -1
        elif self.indicator_type == 'unit':
            self.row = position
            self.col = -1
        elif self.indicator_type == 'session':
            self.row = -1
            self.col = position
        else:
            raise ValueError("Invalid indicator type requested!")

        self.pos = (self.col, self.row)

        self.default_size = (width, height)
        self.constant_dimension = const_dim
        self.selected = True
        self.responsive = True
        self.in_focus = False

        grid_layout = QtWidgets.QGridLayout(self)
        grid_layout.setObjectName("indicatorGridLayout")
        self.setLayout(grid_layout)

        self.display_text = QtWidgets.QLabel()
        self.display_text.setObjectName("dispText")
        self.display_text.setText(text)
        self.display_text.setIndent(0)
        self.display_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.display_text.setScaledContents(False)
        self.display_text.setWordWrap(True)

        grid_layout.addWidget(self.display_text, 0, 0)

        self.colour_strip = QtWidgets.QLabel()
        self.colour_strip.setObjectName("colourStrip")
        self.colour_strip.setAutoFillBackground(True)
        self.colour_strip.setIndent(0)
        self.colour_strip.setMargin(0)
        self.colour_strip.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        grid_layout.addWidget(self.colour_strip, 0, 1)
        self.colour_strip.hide()

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 0)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        self.set_size()

        self.display_font = self.display_text.font()
        self.set_font_size()

        self.backgrounds = {"deselected": mkColor(0.25), "selected": mkColor('k'), "inFocus": mkColor(0.1)}
        self.default_background = self.backgrounds["selected"]

        self.setAutoFillBackground(True)

        self.set_background(self.default_background)

    def change_size(self, width, height):
        """
        Resizes the plot by the given steps.
        
        **Arguments**
        
            *width* (float):
                The change step percentage for the width.
            *height* (float):
                The change step percentage for the height.
        
        """
        oldw = float(self.size().width())
        oldh = float(self.size().height())

        if self.indicator_type == 'session':
            neww = int(oldw + oldw * (width / 100.0))
            if neww > 0:
                self.setFixedSize(neww, oldh)
        elif self.indicator_type == 'unit':
            newh = int(oldh + oldh * (height / 100.0))
            if newh > 0:
                self.setFixedSize(oldw, newh)

        self.set_font_size()

    def set_size(self):
        if self.indicator_type == 'pivot':
            self.setFixedSize(self.constant_dimension, self.constant_dimension)
        elif self.indicator_type == 'session':
            self.setFixedSize(self.default_size[0], self.constant_dimension)
        elif self.indicator_type == 'unit':
            self.setFixedSize(self.constant_dimension, self.default_size[1])

    def set_background(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    def set_font_size(self):
        if self.indicator_type == 'pivot':
            self.display_font.setPointSize(0.13 * min(self.size().height(), self.size().width()))
            self.display_font.setBold(True)
        elif self.indicator_type == 'unit':
            self.display_font.setPointSize(0.19 * min(self.size().height(), self.size().width()))
        elif self.indicator_type == 'session':
            self.display_font.setPointSize(0.18 * min(self.size().height(), self.size().width()))
        self.display_text.setFont(self.display_font)

    def toggle_colour_strip(self, colour):
        if colour is not None:
            palette = self.colour_strip.palette()
            palette.setColor(self.backgroundRole(), colour)
            self.colour_strip.setPalette(palette)
            self.colour_strip.show()
        else:
            self.colour_strip.hide()

    ### Mouse Interactions ###

    def mousePressEvent(self, event):
        """
        This method is called you click on this widget.
        
        The event will be accepted if you click with the
        left mouse button.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if event.button() == QtCore.Qt.LeftButton and self.responsive:
            self.select_indicator.emit(self)
            self.selected = not self.selected
            if self.selected:
                self.default_background = self.backgrounds["selected"]
            elif not self.selected:
                self.default_background = self.backgrounds["deselected"]

            self.set_background(self.default_background)
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        # super(PlotWidget, self).mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        """
        Overwritten method to avoid strange behavior.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)        
        
        """
        # super(PlotWidget, self).mouseReleaseEvent(event)
        event.accept()

    def enterEvent(self, event):
        """
        This method is called the mouse enters this widget.
        
        Sets this widget in focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if self.responsive:
            self.in_focus = True
            self.set_background(self.backgrounds["inFocus"])
            event.accept()

    def leaveEvent(self, event):
        """
        This method is called the mouse leaves this widget.
        
        Sets this widget out of focus.
        
        **Arguments**
            
            *event* (:class:`PyQt5.QtCore.QEvent`)
        
        """
        if self.responsive:
            self.in_focus = False
            self.set_background(self.default_background)
            event.accept()
