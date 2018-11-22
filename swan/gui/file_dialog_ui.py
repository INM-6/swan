# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_dialog_ui.ui'
#
# Created: Wed Feb  5 09:29:49 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_File_Dialog(object):
    def setupUi(self, file_dialog):
        file_dialog.setObjectName(_fromUtf8("file_dialog"))
        file_dialog.resize(557, 605)
        self.verticalLayout = QtGui.QVBoxLayout(file_dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(file_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.pathEdit = QtGui.QLineEdit(self.groupBox)
        self.pathEdit.setReadOnly(True)
        self.pathEdit.setObjectName(_fromUtf8("pathEdit"))
        self.horizontalLayout.addWidget(self.pathEdit)
        self.pathBtn = QtGui.QPushButton(self.groupBox)
        self.pathBtn.setObjectName(_fromUtf8("pathBtn"))
        self.horizontalLayout.addWidget(self.pathBtn)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(file_dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.groupBox_2.setStyleSheet('QGroupBox:title {'
                                      'text-align: center;'
                                      'subcontrol-origin: content;'
                                      'subcontrol-position: top center; }')
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.selectList = QtGui.QListWidget(self.groupBox_2)
        self.selectList.setObjectName(_fromUtf8("selectList"))
        self.horizontalLayout_2.addWidget(self.selectList)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.addBtn = QtGui.QPushButton(self.groupBox_2)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self.verticalLayout_2.addWidget(self.addBtn)
        self.removeBtn = QtGui.QPushButton(self.groupBox_2)
        self.removeBtn.setObjectName(_fromUtf8("removeBtn"))
        self.verticalLayout_2.addWidget(self.removeBtn)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.selectionList = QtGui.QListWidget(self.groupBox_2)
        self.selectionList.setObjectName(_fromUtf8("selectionList"))
        self.horizontalLayout_2.addWidget(self.selectionList)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.btnBox = QtGui.QDialogButtonBox(file_dialog)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName(_fromUtf8("btnBox"))
        self.verticalLayout.addWidget(self.btnBox)
        self.label.setBuddy(self.pathEdit)

        self.retranslateUi(file_dialog)
        QtCore.QMetaObject.connectSlotsByName(file_dialog)

    def retranslateUi(self, file_dialog):
        file_dialog.setWindowTitle(QtGui.QApplication.translate("File_Dialog",
                                                                "File selection",
                                                                None))

        self.groupBox.setTitle(QtGui.QApplication.translate("File_Dialog",
                                                            "Select the parent folder of your data",
                                                            None))

        self.label.setText(QtGui.QApplication.translate("File_Dialog",
                                                        "Path:",
                                                        None))

        self.pathBtn.setText(QtGui.QApplication.translate("File_Dialog",
                                                          "Browse...",
                                                          None))

        self.groupBox_2.setTitle(QtGui.QApplication.translate("File_Dialog",
                                                              "Choose files and add them to (or remove them from) the"
                                                              " list on the right",
                                                              None))

        self.addBtn.setText(QtGui.QApplication.translate("File_Dialog",
                                                         "Add",
                                                         None))

        self.removeBtn.setText(QtGui.QApplication.translate("File_Dialog",
                                                            "Remove",
                                                            None))
