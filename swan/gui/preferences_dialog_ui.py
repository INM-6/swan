# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences_dialog_ui.ui'
#
# Created: Tue Apr 22 12:41:27 2014
#      by: PyQt5 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from pyqtgraph.Qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName(_fromUtf8("Preferences"))
        Preferences.resize(532, 390)
        
        self.verticalLayout = QtGui.QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        
        self.optionsList = QtGui.QListWidget(Preferences)
        self.optionsList.setEnabled(True)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.optionsList.sizePolicy().hasHeightForWidth())
        
        self.optionsList.setSizePolicy(sizePolicy)
        self.optionsList.setMaximumSize(QtCore.QSize(100, 16777215))
        self.optionsList.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.optionsList.setProperty("showDropIndicator", True)
        self.optionsList.setObjectName(_fromUtf8("optionsList"))
        
        item = QtGui.QListWidgetItem()
        self.optionsList.addItem(item)
        
        item = QtGui.QListWidgetItem()
        self.optionsList.addItem(item)
        
        self.horizontalLayout_3.addWidget(self.optionsList)
        
        self.optionsView = QtGui.QStackedWidget(Preferences)
        self.optionsView.setObjectName(_fromUtf8("optionsView"))
        
        self.general = QtGui.QWidget()
        self.general.setObjectName(_fromUtf8("general"))
        
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.general)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        
        self.groupBox = QtGui.QGroupBox(self.general)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        
        self.projectNameEdit = QtGui.QLineEdit(self.groupBox)
        self.projectNameEdit.setObjectName(_fromUtf8("projectNameEdit"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.projectNameEdit)
        
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        
        self.verticalLayout_2.addWidget(self.groupBox)
        
        self.groupBox_4 = QtGui.QGroupBox(self.general)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        
        self.gridLayout = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        
        self.cacheDirEdit = QtGui.QLineEdit(self.groupBox_4)
        self.cacheDirEdit.setReadOnly(True)
        self.cacheDirEdit.setObjectName(_fromUtf8("cacheDirEdit"))
        self.gridLayout.addWidget(self.cacheDirEdit, 0, 1, 1, 1)
        
        self.cacheDirBtn = QtGui.QPushButton(self.groupBox_4)
        self.cacheDirBtn.setObjectName(_fromUtf8("cacheDirBtn"))
        self.gridLayout.addWidget(self.cacheDirBtn, 0, 2, 1, 1)
        
        self.label_6 = QtGui.QLabel(self.groupBox_4)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        
        self.verticalLayout_2.addWidget(self.groupBox_4)
        
        self.optionsView.addWidget(self.general)
        
        self.overview = QtGui.QWidget()
        self.overview.setObjectName(_fromUtf8("overview"))
        
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.overview)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        
        self.groupBox_2 = QtGui.QGroupBox(self.overview)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        
        self.formLayout = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        
        self.zinStepEdit = QtGui.QLineEdit(self.groupBox_2)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zinStepEdit.sizePolicy().hasHeightForWidth())
        
        self.zinStepEdit.setSizePolicy(sizePolicy)
        self.zinStepEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.zinStepEdit.setObjectName(_fromUtf8("zinStepEdit"))
        
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.zinStepEdit)
        
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        
        self.zoutStepEdit = QtGui.QLineEdit(self.groupBox_2)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoutStepEdit.sizePolicy().hasHeightForWidth())
        
        self.zoutStepEdit.setSizePolicy(sizePolicy)
        self.zoutStepEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.zoutStepEdit.setObjectName(_fromUtf8("zoutStepEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.zoutStepEdit)
        
        self.verticalLayout_3.addWidget(self.groupBox_2)
        
        self.groupBox_3 = QtGui.QGroupBox(self.overview)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_3)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        
        self.expandStepEdit = QtGui.QLineEdit(self.groupBox_3)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expandStepEdit.sizePolicy().hasHeightForWidth())
        
        self.expandStepEdit.setSizePolicy(sizePolicy)
        self.expandStepEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.expandStepEdit.setObjectName(_fromUtf8("expandStepEdit"))
        
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.expandStepEdit)
        
        self.label_5 = QtGui.QLabel(self.groupBox_3)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_5)
        
        self.collapseStepEdit = QtGui.QLineEdit(self.groupBox_3)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.collapseStepEdit.sizePolicy().hasHeightForWidth())
        
        self.collapseStepEdit.setSizePolicy(sizePolicy)
        self.collapseStepEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.collapseStepEdit.setObjectName(_fromUtf8("collapseStepEdit"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.collapseStepEdit)
        
        self.verticalLayout_3.addWidget(self.groupBox_3)
        
        self.optionsView.addWidget(self.overview)
        
        self.horizontalLayout_3.addWidget(self.optionsView)
        
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        
        self.errorLabel = QtGui.QLabel(Preferences)
        self.errorLabel.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.errorLabel.setText(_fromUtf8(""))
        self.errorLabel.setObjectName(_fromUtf8("errorLabel"))
        self.verticalLayout.addWidget(self.errorLabel)
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        
        self.defaultBtn = QtGui.QPushButton(Preferences)
        self.defaultBtn.setObjectName(_fromUtf8("defaultBtn"))
        self.horizontalLayout.addWidget(self.defaultBtn)
        
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.label.setBuddy(self.projectNameEdit)
        self.label_6.setBuddy(self.cacheDirEdit)
        self.label_2.setBuddy(self.zinStepEdit)
        self.label_3.setBuddy(self.zoutStepEdit)
        self.label_4.setBuddy(self.expandStepEdit)
        self.label_5.setBuddy(self.collapseStepEdit)

        self.retranslateUi(Preferences)
        
        self.optionsList.setCurrentRow(0)
        self.optionsView.setCurrentIndex(0)
        
        self.buttonBox.accepted.connect(Preferences.accept)
        
        self.buttonBox.rejected.connect(Preferences.reject)
        
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None))
        __sortingEnabled = self.optionsList.isSortingEnabled()
        self.optionsList.setSortingEnabled(False)
        item = self.optionsList.item(0)
        item.setText(QtGui.QApplication.translate("Preferences", "General", None))
        item = self.optionsList.item(1)
        item.setText(QtGui.QApplication.translate("Preferences", "Overview", None))
        self.optionsList.setSortingEnabled(__sortingEnabled)
        self.groupBox.setTitle(QtGui.QApplication.translate("Preferences", "Project", None))
        self.label.setText(QtGui.QApplication.translate("Preferences", "Default project name:", None))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Preferences", "Cache", None))
        self.cacheDirBtn.setText(QtGui.QApplication.translate("Preferences", "browse...", None))
        self.label_6.setText(QtGui.QApplication.translate("Preferences", "Location:", None))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Preferences", "Resizing", None))
        self.label_2.setText(QtGui.QApplication.translate("Preferences", "Zoom in step:", None))
        self.label_3.setText(QtGui.QApplication.translate("Preferences", "Zoom out step:", None))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Preferences", "Reranging", None))
        self.label_4.setText(QtGui.QApplication.translate("Preferences", "Expand step:", None))
        self.label_5.setText(QtGui.QApplication.translate("Preferences", "Collapse step:", None))
        self.defaultBtn.setText(QtGui.QApplication.translate("Preferences", "Restore default", None))

