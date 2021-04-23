# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_dialog_ui.ui'
#
# Created: Wed Feb  5 09:29:49 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtWidgets


class FileDialogUI(object):

    def __init__(self, file_dialog):
        file_dialog.resize(557, 605)
        self.verticalLayout = QtWidgets.QVBoxLayout(file_dialog)

        self.groupBox = QtWidgets.QGroupBox("Select the parent folder of your data", file_dialog)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)

        self.label = QtWidgets.QLabel("Path:")
        self.horizontalLayout.addWidget(self.label)

        self.pathEdit = QtWidgets.QLineEdit(self.groupBox)
        self.pathEdit.setReadOnly(True)
        self.horizontalLayout.addWidget(self.pathEdit)

        self.pathBtn = QtWidgets.QPushButton("Browse...", self.groupBox)
        self.horizontalLayout.addWidget(self.pathBtn)

        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QtWidgets.QGroupBox("Choose files and add them to (or remove them from) "
                                              "the list on the right",
                                              file_dialog)
        self.groupBox_2.setStyleSheet('QGroupBox:title {'
                                      'text-align: center;'
                                      'subcontrol-origin: content;'
                                      'subcontrol-position: top center; }')

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)

        self.selectList = QtWidgets.QListWidget(self.groupBox_2)
        self.horizontalLayout_2.addWidget(self.selectList)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout()

        self.addBtn = QtWidgets.QPushButton("Add", self.groupBox_2)
        self.verticalLayout_2.addWidget(self.addBtn)

        self.removeBtn = QtWidgets.QPushButton("Remove", self.groupBox_2)
        self.verticalLayout_2.addWidget(self.removeBtn)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.selectionList = QtWidgets.QListWidget(self.groupBox_2)
        self.horizontalLayout_2.addWidget(self.selectionList)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.btnBox = QtWidgets.QDialogButtonBox(file_dialog)
        self.btnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.btnBox)

        self.label.setBuddy(self.pathEdit)

        file_dialog.setWindowTitle("File selection")
