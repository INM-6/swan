# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vumv_ui.ui'
#
# Created: Tue Jun 10 14:19:32 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_VumV(object):
    def setupUi(self, VumV):
        VumV.setObjectName(_fromUtf8("VumV"))
        VumV.resize(602, 474)
        self.gridLayout_2 = QtGui.QGridLayout(VumV)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pathEdit = QtGui.QLineEdit(VumV)
        self.pathEdit.setReadOnly(True)
        self.pathEdit.setObjectName(_fromUtf8("pathEdit"))
        self.horizontalLayout.addWidget(self.pathEdit)
        self.browseBtn = QtGui.QPushButton(VumV)
        self.browseBtn.setObjectName(_fromUtf8("browseBtn"))
        self.horizontalLayout.addWidget(self.browseBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(VumV)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.channelBox = QtGui.QComboBox(VumV)
        self.channelBox.setObjectName(_fromUtf8("channelBox"))
        self.horizontalLayout_2.addWidget(self.channelBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(VumV)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.details = QtGui.QTableWidget(self.splitter)
        self.details.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.details.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.details.setObjectName(_fromUtf8("details"))
        self.details.setColumnCount(1)
        self.details.setRowCount(2)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.details.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.details.setItem(1, 0, item)
        self.details.horizontalHeader().setStretchLastSection(True)
        self.details.verticalHeader().setStretchLastSection(True)
        self.content = QtGui.QTableWidget(self.splitter)
        self.content.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.content.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.content.setObjectName(_fromUtf8("content"))
        self.content.setColumnCount(1)
        self.content.setRowCount(1)
        item = QtGui.QTableWidgetItem()
        self.content.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.content.setHorizontalHeaderItem(0, item)
        self.content.horizontalHeader().setCascadingSectionResizes(False)
        self.content.horizontalHeader().setDefaultSectionSize(150)
        self.content.verticalHeader().setDefaultSectionSize(30)
        self.gridLayout_2.addWidget(self.splitter, 1, 0, 1, 1)

        self.retranslateUi(VumV)
        QtCore.QMetaObject.connectSlotsByName(VumV)
        VumV.setTabOrder(self.browseBtn, self.pathEdit)
        VumV.setTabOrder(self.pathEdit, self.content)

    def retranslateUi(self, VumV):
        VumV.setWindowTitle(QtGui.QApplication.translate("VumV", "VUM Viewer"))
        self.pathEdit.setPlaceholderText(QtGui.QApplication.translate("VumV", "path to vum"))
        self.browseBtn.setText(QtGui.QApplication.translate("VumV", "browse..."))
        self.label.setText(QtGui.QApplication.translate("VumV", "Electrode:"))
        item = self.details.verticalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("VumV", "Channel"))
        item = self.details.verticalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("VumV", "Files"))
        item = self.details.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("VumV", "Value"))
        __sortingEnabled = self.details.isSortingEnabled()
        self.details.setSortingEnabled(False)
        item = self.details.item(0, 0)
        item.setText(QtGui.QApplication.translate("VumV", "-"))
        item = self.details.item(1, 0)
        item.setText(QtGui.QApplication.translate("VumV", "-"))
        self.details.setSortingEnabled(__sortingEnabled)
        item = self.content.verticalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("VumV", "UNIT"))
        item = self.content.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("VumV", "SESSION"))

