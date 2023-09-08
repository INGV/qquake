# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\ogc_service_widget.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(687, 613)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.layers_tree_view = QtWidgets.QTreeView(self.groupBox)
        self.layers_tree_view.setObjectName("layers_tree_view")
        self.gridLayout.addWidget(self.layers_tree_view, 0, 0, 1, 3)
        self.cql_filter_label = QtWidgets.QLabel(self.groupBox)
        self.cql_filter_label.setText("")
        self.cql_filter_label.setObjectName("cql_filter_label")
        self.gridLayout.addWidget(self.cql_filter_label, 1, 1, 1, 1)
        self.button_check_all = QtWidgets.QPushButton(self.groupBox)
        self.button_check_all.setObjectName("button_check_all")
        self.gridLayout.addWidget(self.button_check_all, 1, 0, 1, 1)
        self.button_check_none = QtWidgets.QPushButton(self.groupBox)
        self.button_check_none.setObjectName("button_check_none")
        self.gridLayout.addWidget(self.button_check_none, 1, 1, 1, 1)
        self.button_set_filter = QtWidgets.QPushButton(self.groupBox)
        self.button_set_filter.setObjectName("button_set_filter")
        self.gridLayout.addWidget(self.button_set_filter, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Available Layers"))
        self.button_check_all.setText(_translate("Form", "Check all"))
        self.button_check_none.setText(_translate("Form", "Uncheck All"))
        self.button_set_filter.setText(_translate("Form", "Set Filter…"))
