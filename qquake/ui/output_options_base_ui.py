# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\output_options_base.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_output_options_base(object):
    def setupUi(self, output_options_base):
        output_options_base.setObjectName("output_options_base")
        output_options_base.resize(479, 106)
        self.verticalLayout = QtWidgets.QVBoxLayout(output_options_base)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(output_options_base)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.depth_values_combo_box = QtWidgets.QComboBox(self.groupBox)
        self.depth_values_combo_box.setObjectName("depth_values_combo_box")
        self.gridLayout.addWidget(self.depth_values_combo_box, 1, 1, 1, 1)
        self.depth_unit_combo_box = QtWidgets.QComboBox(self.groupBox)
        self.depth_unit_combo_box.setObjectName("depth_unit_combo_box")
        self.gridLayout.addWidget(self.depth_unit_combo_box, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(output_options_base)
        QtCore.QMetaObject.connectSlotsByName(output_options_base)

    def retranslateUi(self, output_options_base):
        _translate = QtCore.QCoreApplication.translate
        output_options_base.setWindowTitle(_translate("output_options_base", "QQuake"))
        self.groupBox.setTitle(_translate("output_options_base", "Depth"))
        self.label_2.setText(_translate("output_options_base", "Values"))
        self.label.setText(_translate("output_options_base", "Units"))
