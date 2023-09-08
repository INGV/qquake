# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\cql_filter_builder.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(826, 662)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_fields = QtWidgets.QLabel(self.layoutWidget)
        self.label_fields.setObjectName("label_fields")
        self.gridLayout.addWidget(self.label_fields, 1, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.layer_combo = QtWidgets.QComboBox(self.layoutWidget)
        self.layer_combo.setObjectName("layer_combo")
        self.gridLayout.addWidget(self.layer_combo, 0, 1, 1, 1)
        self.field_list = QtWidgets.QTreeWidget(self.layoutWidget)
        self.field_list.setColumnCount(2)
        self.field_list.setObjectName("field_list")
        self.field_list.headerItem().setText(0, "1")
        self.field_list.headerItem().setText(1, "2")
        self.field_list.header().setVisible(True)
        self.gridLayout.addWidget(self.field_list, 2, 0, 1, 2)
        self.button_add = QtWidgets.QPushButton(self.layoutWidget)
        self.button_add.setObjectName("button_add")
        self.gridLayout.addWidget(self.button_add, 3, 0, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.tab_widget = QtWidgets.QTabWidget(self.splitter)
        self.tab_widget.setObjectName("tab_widget")
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.simple_query_list = QtWidgets.QTreeWidget(self.widget)
        self.simple_query_list.setColumnCount(4)
        self.simple_query_list.setObjectName("simple_query_list")
        self.simple_query_list.headerItem().setText(0, "1")
        self.simple_query_list.headerItem().setText(1, "2")
        self.simple_query_list.headerItem().setText(2, "3")
        self.simple_query_list.headerItem().setText(3, "4")
        self.simple_query_list.header().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.simple_query_list)
        self.tab_widget.addTab(self.widget, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.sql_editor_widget = QgsCodeEditorSQL(self.tab_2)
        self.sql_editor_widget.setObjectName("sql_editor_widget")
        self.verticalLayout_3.addWidget(self.sql_editor_widget)
        self.cql_help_button = QtWidgets.QPushButton(self.tab_2)
        self.cql_help_button.setObjectName("cql_help_button")
        self.verticalLayout_3.addWidget(self.cql_help_button)
        self.tab_widget.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Form)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_fields.setText(_translate("Form", "List of fields"))
        self.label.setText(_translate("Form", "Layer"))
        self.button_add.setText(_translate("Form", "Add"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.widget), _translate("Form", "Simple Query"))
        self.cql_help_button.setText(_translate("Form", "Help on how to write a CQL query"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), _translate("Form", "Advanced Query (CQL Editor)"))
from qgis.gui import QgsCodeEditorSQL
