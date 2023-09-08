# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\table_options_widget_base.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_table_options_widget_base(object):
    def setupUi(self, table_options_widget_base):
        table_options_widget_base.setObjectName("table_options_widget_base")
        table_options_widget_base.resize(523, 249)
        self.gridLayout = QtWidgets.QGridLayout(table_options_widget_base)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_4 = QtWidgets.QGroupBox(table_options_widget_base)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.radio_extended_output = QtWidgets.QRadioButton(self.groupBox_4)
        self.radio_extended_output.setObjectName("radio_extended_output")
        self.gridLayout_8.addWidget(self.radio_extended_output, 1, 0, 1, 1)
        self.output_table_options_button = QtWidgets.QPushButton(self.groupBox_4)
        self.output_table_options_button.setObjectName("output_table_options_button")
        self.gridLayout_8.addWidget(self.output_table_options_button, 1, 1, 1, 1)
        self.radio_basic_output = QtWidgets.QRadioButton(self.groupBox_4)
        self.radio_basic_output.setObjectName("radio_basic_output")
        self.gridLayout_8.addWidget(self.radio_basic_output, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox_4, 3, 0, 1, 2)
        self.group_style = QtWidgets.QGroupBox(table_options_widget_base)
        self.group_style.setObjectName("group_style")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.group_style)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_style_epicentres = QtWidgets.QLabel(self.group_style)
        self.label_style_epicentres.setObjectName("label_style_epicentres")
        self.gridLayout_2.addWidget(self.label_style_epicentres, 0, 0, 1, 1)
        self.combo_style_epicentres = QtWidgets.QComboBox(self.group_style)
        self.combo_style_epicentres.setObjectName("combo_style_epicentres")
        self.gridLayout_2.addWidget(self.combo_style_epicentres, 0, 1, 1, 1)
        self.label_style_macro = QtWidgets.QLabel(self.group_style)
        self.label_style_macro.setObjectName("label_style_macro")
        self.gridLayout_2.addWidget(self.label_style_macro, 1, 0, 1, 1)
        self.combo_style_macro = QtWidgets.QComboBox(self.group_style)
        self.combo_style_macro.setObjectName("combo_style_macro")
        self.gridLayout_2.addWidget(self.combo_style_macro, 1, 1, 1, 1)
        self.label_style_stations = QtWidgets.QLabel(self.group_style)
        self.label_style_stations.setObjectName("label_style_stations")
        self.gridLayout_2.addWidget(self.label_style_stations, 2, 0, 1, 1)
        self.combo_style_stations = QtWidgets.QComboBox(self.group_style)
        self.combo_style_stations.setObjectName("combo_style_stations")
        self.gridLayout_2.addWidget(self.combo_style_stations, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.group_style, 4, 0, 1, 2)

        self.retranslateUi(table_options_widget_base)
        QtCore.QMetaObject.connectSlotsByName(table_options_widget_base)

    def retranslateUi(self, table_options_widget_base):
        _translate = QtCore.QCoreApplication.translate
        table_options_widget_base.setWindowTitle(_translate("table_options_widget_base", "Form"))
        self.groupBox_4.setTitle(_translate("table_options_widget_base", "Output Table"))
        self.radio_extended_output.setText(_translate("table_options_widget_base", "Extended (user customizable)"))
        self.output_table_options_button.setText(_translate("table_options_widget_base", "Extended Table Options…"))
        self.radio_basic_output.setText(_translate("table_options_widget_base", "Basic (default FDSN text format)"))
        self.group_style.setTitle(_translate("table_options_widget_base", "Style"))
        self.label_style_epicentres.setText(_translate("table_options_widget_base", "Epicentres"))
        self.label_style_macro.setText(_translate("table_options_widget_base", "Macroseismic data"))
        self.label_style_stations.setText(_translate("table_options_widget_base", "Stations"))
