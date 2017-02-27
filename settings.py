# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_settings(object):
    def setupUi(self, settings):
        settings.setObjectName(_fromUtf8("settings"))
        settings.resize(391, 334)
        self.gridLayout = QtGui.QGridLayout(settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.nameEdit = QtGui.QLineEdit(settings)
        self.nameEdit.setObjectName(_fromUtf8("nameEdit"))
        self.verticalLayout.addWidget(self.nameEdit)
        self.tableWidget = QtGui.QTableWidget(settings)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        self.rowButton = QtGui.QPushButton(settings)
        self.rowButton.setObjectName(_fromUtf8("rowButton"))
        self.verticalLayout.addWidget(self.rowButton)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.newButton = QtGui.QPushButton(settings)
        self.newButton.setObjectName(_fromUtf8("newButton"))
        self.horizontalLayout.addWidget(self.newButton)
        self.openButton = QtGui.QPushButton(settings)
        self.openButton.setObjectName(_fromUtf8("openButton"))
        self.horizontalLayout.addWidget(self.openButton)
        self.saveButton = QtGui.QPushButton(settings)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout.addWidget(self.saveButton)
        self.saveAsButton = QtGui.QPushButton(settings)
        self.saveAsButton.setObjectName(_fromUtf8("saveAsButton"))
        self.horizontalLayout.addWidget(self.saveAsButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(settings)
        QtCore.QMetaObject.connectSlotsByName(settings)

    def retranslateUi(self, settings):
        settings.setWindowTitle(_translate("settings", "settings", None))
        self.nameEdit.setText(_translate("settings", "Name", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("settings", "Parameter", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("settings", "Value", None))
        self.rowButton.setText(_translate("settings", "add Row", None))
        self.newButton.setText(_translate("settings", "New", None))
        self.openButton.setText(_translate("settings", "Open", None))
        self.saveButton.setText(_translate("settings", "Save", None))
        self.saveAsButton.setText(_translate("settings", "Save as...", None))

