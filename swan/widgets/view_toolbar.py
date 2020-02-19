#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 12:20:53 2017

@author: Shashwat Sridhar
"""

from pyqtgraph.Qt import QtCore, QtWidgets


class ViewToolbar(QtWidgets.QWidget):
    
    doLayer = QtCore.pyqtSignal()
    update_view = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, *args, **kwargs):
        
        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)
        
        self.main_grid_layout = QtWidgets.QGridLayout(self)
        self.collapsible_widget = CollapsibleWidget(parent=self, title="Settings", animation_duration=300)
        self.main_grid_layout.addWidget(self.collapsible_widget, 0, 0)
        
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setObjectName("viewToolbarGridLayout")

        self.activate_button = ToggleButton()
        self.activate_button.clicked.connect(self.toggle_view)
        self.grid_layout.addWidget(self.activate_button, 0, 0, 1, 1)
        
        self.layers = QtWidgets.QGroupBox("Layers")
        self.layers.setObjectName("Layers")
        self.layers_layout = QtWidgets.QGridLayout()
        self.layers_layout.setContentsMargins(0, 0, 0, 0)
        self.layers_layout.setSpacing(0)
        self.layers.setLayout(self.layers_layout)
        self.grid_layout.addWidget(self.layers, 1, 0, 1, 2)
        
        self.options = QtWidgets.QGroupBox("Options")
        self.options_layout = QtWidgets.QGridLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(0)
        self.options.setLayout(self.options_layout)
        self.grid_layout.addWidget(self.options, 0, 2, 2, 6)
        
        self.grid_layout.setColumnStretch(1, 2)
        
        self.main_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_grid_layout.setSpacing(0)
        
        self.layer_items = []
    
    def setup_radio_buttons(self, layers):
        for layer in layers:
            radio_button = QtWidgets.QRadioButton(layer)
            radio_button.toggled.connect(self.refresh_layers)
            self.layer_items.append(radio_button)
            
            self.layers_layout.addWidget(radio_button)
            if len(self.layer_items) == 1:
                radio_button.setChecked(True)
    
    def setup_checkboxes(self, layers):
        for l, layer in enumerate(layers):
            checkbox = QtWidgets.QCheckBox(layer)
            checkbox.toggled.connect(self.refresh_layers)
            self.layer_items.append(checkbox)
            
            self.layers_layout.addWidget(checkbox)
            if l == 0:
                checkbox.setChecked(True)
    
    def get_checked_layers(self):
        checked_layers = []
        if self.layer_items:
            for item in self.layer_items:
                if item.isChecked():
                    checked_layers.append(str(item.text()))
        return checked_layers
    
    def refresh_layers(self):
        self.doLayer.emit()

    def toggle_view(self):
        self.doLayer.emit()


class CollapsibleWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, title='', animation_duration=300):
        """
        References:
            # Adapted from the StackOverflow answer
            https://stackoverflow.com/a/37927256/7126611
            
            # which adapted it from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(CollapsibleWidget, self).__init__(parent=parent)

        self.animation_duration = animation_duration
        self.toggle_animation = QtCore.QParallelAnimationGroup()
        self.content_area = QtWidgets.QScrollArea()
        self.header_line = QtWidgets.QFrame()
        self.toggle_button = QtWidgets.QToolButton()
        self.main_layout = QtWidgets.QGridLayout()

        toggle_button = self.toggle_button
        toggle_button.setStyleSheet("QToolButton { border: none; }")
        toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggle_button.setArrowType(QtCore.Qt.RightArrow)
        toggle_button.setText(str(title))
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)

        header_line = self.header_line
        header_line.setFrameShape(QtWidgets.QFrame.HLine)
        header_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        header_line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

        self.content_area.setStyleSheet("QScrollArea {border: none; }")
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        # start out collapsed
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggle_animation = self.toggle_animation
        toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight", self))
        toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight", self))
        toggle_animation.addAnimation(QtCore.QPropertyAnimation(self.content_area, b"minimumHeight", self.content_area))
        toggle_animation.addAnimation(QtCore.QPropertyAnimation(self.content_area, b"maximumHeight", self.content_area))
        # don't waste space
        main_layout = self.main_layout
        main_layout.setContentsMargins(0, 0, 0, 0)
        row = 0
        main_layout.addWidget(self.toggle_button, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        main_layout.addWidget(self.header_line, row, 2, 1, 1)
        row += 1
        main_layout.addWidget(self.content_area, row, 0, 1, 3)
        self.setLayout(self.main_layout)

        def start_animation(checked):
            arrow_type = QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
            direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
            toggle_button.setArrowType(arrow_type)
            self.toggle_animation.setDirection(direction)
            self.toggle_animation.start()

        self.toggle_button.clicked.connect(start_animation)

    def set_content_layout(self, content_layout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.content_area.destroy()
        self.content_area.setLayout(content_layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight() + 1
        content_height = content_layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount() - 1):
            spoiler_animation = self.toggle_animation.animationAt(i)
            spoiler_animation.setDuration(self.animation_duration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)
        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(self.animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class ToggleButton(QtWidgets.QPushButton):
    def __init__(self):
        QtWidgets.QPushButton.__init__(self)
        self.current_state = False
        self.off_stylesheet = "background-color: red"
        self.on_stylesheet = "background-color: green"

        self.setText("off")
        self.setStyleSheet(self.off_stylesheet)

        self.clicked.connect(self.toggle_state)

    def toggle_state(self):
        self.current_state = not self.current_state
        if self.current_state:
            self.setStyleSheet(self.on_stylesheet)
            self.setText("On")
        else:
            self.setStyleSheet(self.off_stylesheet)
            self.setText("Off")