#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:19:42 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtWidgets, QtCore


class IsiOptionsUi(QtWidgets.QWidget):
    
    def __init__(self, parent, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.setup_ui(parent)
        
    def setup_ui(self, isi_widget):
        
        self.ggl = QtWidgets.QGridLayout(self)
        w = QtWidgets.QWidget()
        y = QtWidgets.QWidget()
        l1 = QtWidgets.QLabel("Bin Max (ms):")
        l2 = QtWidgets.QLabel("Bin Step (ms):")
        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.ghl1 = QtWidgets.QHBoxLayout(w)
        self.ghl2 = QtWidgets.QHBoxLayout(y)
        
        self.binMaxPlusBtn = QtWidgets.QPushButton("+")
        self.binMaxPlusBtn.setMinimumWidth(30)
        self.binMaxPlusBtn.setMaximumWidth(50)
        self.binMaxEdit = QtWidgets.QLineEdit()
        self.binMaxEdit.setMinimumWidth(30)
        self.binMaxEdit.setMaximumWidth(50)
        self.binMaxEdit.setText(str(isi_widget.bin_max))
        self.binMaxMinusBtn = QtWidgets.QPushButton("-")
        self.binMaxMinusBtn.setMinimumWidth(30)
        self.binMaxMinusBtn.setMaximumWidth(50)
        self.binStepPlusBtn = QtWidgets.QPushButton("+")
        self.binStepPlusBtn.setMinimumWidth(30)
        self.binStepPlusBtn.setMaximumWidth(50)
        self.binStepEdit = QtWidgets.QLineEdit()
        self.binStepEdit.setMinimumWidth(30)
        self.binStepEdit.setMaximumWidth(50)
        self.binStepEdit.setText(str(isi_widget.bin_step))
        self.binStepMinusBtn = QtWidgets.QPushButton("-")
        self.binStepMinusBtn.setMinimumWidth(30)
        self.binStepMinusBtn.setMaximumWidth(50)
        self.histStyleCheckbox = QtWidgets.QCheckBox()
        self.histStyleCheckbox.setText("Step Mode")
        self.histStyleCheckbox.setCheckState(QtCore.Qt.Unchecked)
        
        self.ghl1.addWidget(self.binMaxMinusBtn)
        self.ghl1.addWidget(self.binMaxEdit)
        self.ghl1.addWidget(self.binMaxPlusBtn)
        self.ghl2.addWidget(self.binStepMinusBtn)       
        self.ghl2.addWidget(self.binStepEdit)
        self.ghl2.addWidget(self.binStepPlusBtn)        
        
        self.ggl.addWidget(l1, 0, 0, 1, 2)
        self.ggl.addWidget(w, 0, 2, 1, 2)
        self.ggl.addWidget(l2, 1, 0, 1, 2)
        self.ggl.addWidget(y, 1, 2, 1, 2)
        self.ggl.addWidget(self.histStyleCheckbox, 0, 4, 1, 2)
        self.ggl.addWidget(self.error_label, 1, 4, 1, 2)
        
        isi_widget.toolbar.options_layout.addWidget(self)
        
        self.binMaxPlusBtn.clicked.connect(isi_widget.on_max_plus)
        self.binMaxMinusBtn.clicked.connect(isi_widget.on_max_minus)
        self.binStepPlusBtn.clicked.connect(isi_widget.on_step_plus)
        self.binStepMinusBtn.clicked.connect(isi_widget.on_step_minus)
        self.histStyleCheckbox.stateChanged.connect(isi_widget.step_mode_changed)
        
        self.binMaxEdit.textChanged.connect(isi_widget.bin_max_changed)
        self.binStepEdit.textChanged.connect(isi_widget.bin_step_changed)
        self.binMaxEdit.returnPressed.connect(isi_widget.on_enter)
        self.binStepEdit.returnPressed.connect(isi_widget.on_enter)
        
        self.ggl.setContentsMargins(0, 0, 0, 0)
        self.ggl.setSpacing(0)
        
        isi_widget.toolbar.collapsible_widget.set_content_layout(isi_widget.toolbar.grid_layout)
        isi_widget.toolbar.main_grid_layout.setContentsMargins(0, 0, 0, 0)
        isi_widget.toolbar.main_grid_layout.setSpacing(0)