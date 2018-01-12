#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 15:24:54 2017

@author: sridhar
"""

from pyqtgraph.Qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName(_fromUtf8("Preferences"))
        Preferences.resize(532, 390)
        
        self.preferencesVertical = QtGui.QVBoxLayout(Preferences)
        self.preferencesVertical.setObjectName(_fromUtf8("preferencesVertical"))
        
        self.mainHorizontal = QtGui.QHBoxLayout()
        self.mainHorizontal.setObjectName(_fromUtf8("mainHorizontal"))
        
        self.preferencesVertical.addLayout(self.mainHorizontal)
        
        self.optionsList = QtGui.QListWidget(Preferences)
        self.optionsList.setEnabled(True)
        self.optionsList.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.EditKeyPressed)
        self.optionsList.setObjectName(_fromUtf8("optionsList"))
        
        self.mainHorizontal.addWidget(self.optionsList)
        
        self.item_general = QtGui.QListWidgetItem()
        self.item_overview = QtGui.QListWidgetItem()
        
        self.optionsList.addItem(self.item_general)
        self.optionsList.addItem(self.item_overview)
        
        self.optionsWidget = QtGui.QStackedWidget(Preferences)
        self.optionsWidget.setObjectName(_fromUtf8("optionsWidget"))
        
        self.general = QtGui.QWidget()
        self.general.setObjectName(_fromUtf8("general"))
        
        self.generalVertical = QtGui.QVBoxLayout(self.general)
        self.generalVertical.setObjectName(_fromUtf8("generalVerticalLayout"))
        
        self.generalProject = QtGui.QGroupBox(self.general)
        self.generalProject.setObjectName(_fromUtf8("projectGroupBox"))
        
        self.projectForm = QtGui.QFormLayout(self.generalProject)
        self.projectForm.setObjectName(_fromUtf8("projectForm"))
        
        self.projectName = QtGui.QLineEdit(self.generalProject)
        self.projectName.setObjectName(_fromUtf8("projectNameEdit"))
        self.projectForm.addRow(QtGui.QApplication.translate("Preferences", "Default Project Name: ", None), self.projectName)

        self.generalCache = QtGui.QGroupBox(self.general)
        self.generalCache.setObjectName(_fromUtf8("cacheGroupBox"))
        
        self.cacheForm = QtGui.QFormLayout(self.generalCache)
        self.cacheForm.setObjectName(_fromUtf8("cacheForm"))
    							   
        self.cachePath = QtGui.QLineEdit(self.generalCache)
        self.cachePath.setObjectName(_fromUtf8("cachePathEdit"))
        
        self.cacheButton = QtGui.QPushButton(self.generalCache)
        self.cacheButton.setObjectName(_fromUtf8("cacheButton"))
        
        self.cacheHorizontal = QtGui.QHBoxLayout(self.generalCache)
        self.cacheHorizontal.setObjectName(_fromUtf8("cacheHorizontal"))
        
        self.cacheHorizontal.addWidget(self.cachePath)
        self.cacheHorizontal.addWidget(self.cacheButton)
        
        self.cacheForm.addRow(QtGui.QApplication.translate("Preferences", "Location: ", None), self.cacheHorizontal)
        
        self.overview = QtGui.QWidget()
        self.overview.setObjectName(_fromUtf8("overview"))
        
        self.overviewVertical = QtGui.QVBoxLayout(self.overview)
        self.overviewVertical.setObjectName(_fromUtf8("overviewVerticalLayout"))
        
        self.overviewResizing = QtGui.QGroupBox(self.overview)
        self.overviewResizing.setObjectName(_fromUtf8("resizingGroupBox"))
        
        self.resizingForm = QtGui.QFormLayout(self.overviewResizing)
        self.resizingForm.setObjectName(_fromUtf8("resizingForm"))
        
        self.zInStep = QtGui.QLineEdit(self.overviewResizing)
        self.zInStep.setObjectName(_fromUtf8("zoomInStepEdit"))
        
        self.zOutStep = QtGui.QLineEdit(self.overviewResizing)
        self.zOutStep.setObjectName(_fromUtf8("zoomOutStepEdit"))
        
        self.resizingForm.addRow(QtGui.QApplication.translate("Preferences", "Zoom In Step: ", None), self.zInStep)
        self.resizingForm.addRow(QtGui.QApplication.translate("Preferences", "Zoom OUt Step: ", None), self.zOutStep)
        
        self.overviewReranging = QtGui.QGroupBox(self.overview)
        self.overviewReranging.setObjectName(_fromUtf8("rerangingGroupBox"))
        
        self.rerangingForm = QtGui.QFormLayout(self.overviewReranging)
        self.rerangingForm.setObjectName(_fromUtf8("rerangingForm"))
        
        self.expandStep = QtGui.QLineEdit(self.overviewReranging)
        self.expandStep.setObjectName(_fromUtf8("expandStepEdit"))
        
        self.collapseStep = QtGui.QLineEdit(self.overviewReranging)
        self.collapseStep.setObjectName(_fromUtf8("collapseStepEdit"))
        
        self.rerangingForm.addRow(QtGui.QApplication.translate("Preferences", "Expand Step: ", None), self.expandStep)
        self.rerangingForm.addRow(QtGui.QApplication.translate("Preferences", "Collapse Step: ", None), self.collapseStep)
        
        self.optionsWidget.addWidget(self.general)
        self.optionsWidget.addWidget(self.overview)
        
        self.errorLabel = QtGui.QLabel(Preferences)
        self.errorLabel.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.errorLabel.setText(_fromUtf8(""))
        self.errorLabel.setObjectName(_fromUtf8("errorLabel"))
        
        self.defaultButton = QtGui.QPushButton(Preferences)
        self.defaultButton.setObjectName(_fromUtf8("defaultButton"))
        self.generalVertical.addWidget(self.defaultButton)
        
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.generalVertical.addWidget(self.buttonBox)
        
        self.retranslateUi(Preferences)
        
        self.optionsList.setCurrentRow(0)
        self.optionsWidget.setCurrentIndex(0)
        
        self.buttonBox.accepted.connect(Preferences.accept)
        self.buttonBox.rejected.connect(Preferences.reject)
        
        QtCore.QMetaObject.connectSlotsByName(Preferences)
        
    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None))
        
        self.item_general.setText(QtGui.QApplication.translate("Preferences", "General", None))
        self.item_overview.setText(QtGui.QApplication.translate("Preferences", "Overview", None))
        
        self.generalProject.setTitle(QtGui.QApplication.translate("Preferences", "Project", None))
        self.generalCache.setTitle(QtGui.QApplication.translate("Preferences", "Cache", None))
        
        