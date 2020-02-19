#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 15:48:48 2018

@author: sridhar
"""
from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph import ComboBox


class RpOptionsUi(QtWidgets.QWidget):
    
    def __init__(self, parent, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.setupUi(parent)
        
    def setupUi(self, rate_profile_widget):
        
        #self.ggl = QtWidgets.QGridLayout(self)
        self.ggl = rate_profile_widget.toolbar.options_layout
        l1 = QtWidgets.QLabel("Choose trigger event:")
        l2 = QtWidgets.QLabel("T-pre (ms): ")
        l3 = QtWidgets.QLabel("T-post (ms): ")
        l4 = QtWidgets.QLabel("Sampling Period (ms): ")
        l5 = QtWidgets.QLabel("Kernel Width (ms): ")
        self.errorLabel = QtWidgets.QLabel()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
        
        self.eventDropDown = ComboBox()
        self.eventDropDown.activated[str].connect(rate_profile_widget.change_trigger_event)
        
        self.timePre = QtWidgets.QLineEdit()
        self.timePre.setMinimumWidth(30)
        self.timePre.setText(str(rate_profile_widget.time_pre))
        self.timePost = QtWidgets.QLineEdit()
        self.timePost.setMinimumWidth(30)
        self.timePost.setText(str(rate_profile_widget.time_post))
        self.samplingPeriod = QtWidgets.QLineEdit()
        self.samplingPeriod.setMinimumWidth(50)
        self.samplingPeriod.setText(str(rate_profile_widget.sampling_period))
        self.kernelWidth = QtWidgets.QLineEdit()
        self.kernelWidth.setMinimumWidth(50)
        self.kernelWidth.setText(str(rate_profile_widget.kernel_width))
        
        self.ggl.addWidget(l1, 0, 0, 1, 3)
        self.ggl.addWidget(self.eventDropDown, 0, 3, 1, 1)
        self.ggl.addWidget(l2, 0, 5, 1, 2)
        self.ggl.addWidget(self.timePre, 1, 5, 1, 2)
        self.ggl.addWidget(l3, 2, 5, 1, 2)
        self.ggl.addWidget(self.timePost, 3, 5, 1, 2)
        self.ggl.addWidget(l4, 0, 7, 1, 3)
        self.ggl.addWidget(self.samplingPeriod, 1, 7, 1, 3)
        self.ggl.addWidget(l5, 2, 7, 1, 3)
        self.ggl.addWidget(self.kernelWidth, 3, 7, 1, 3)
        self.ggl.addWidget(self.errorLabel, 1, 0, 1, 3)
        
        rate_profile_widget.toolbar.options_layout.addWidget(self)
        
        self.timePre.textChanged.connect(rate_profile_widget.on_time_pre_changed)
        self.timePost.textChanged.connect(rate_profile_widget.on_time_post_changed)
        self.samplingPeriod.textChanged.connect(rate_profile_widget.on_sampling_period_changed)
        self.kernelWidth.textChanged.connect(rate_profile_widget.on_kernel_width_changed)
        self.timePre.returnPressed.connect(rate_profile_widget.on_enter)
        self.timePost.returnPressed.connect(rate_profile_widget.on_enter)
        self.samplingPeriod.returnPressed.connect(rate_profile_widget.on_enter)
        self.kernelWidth.returnPressed.connect(rate_profile_widget.on_enter)
        
        self.ggl.setContentsMargins(0, 0, 0, 0)
        self.ggl.setHorizontalSpacing(20)
        
        rate_profile_widget.toolbar.collapsible_widget.set_content_layout(rate_profile_widget.toolbar.grid_layout)
        rate_profile_widget.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)
        rate_profile_widget.toolbar.main_grid_layout.setSpacing(0)