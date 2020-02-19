# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectorwidget_ui.ui'
#
# Created: Thu Nov 28 14:39:22 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.setMinimumWidth(300)
        Form.setMaximumWidth(400)
        Form.setAutoFillBackground(True)
        Form.setStyleSheet(_fromUtf8("background: rgb(255, 255, 255)"))
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        
        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        Form.setSizePolicy(self.sizePolicy)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None))

