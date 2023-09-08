# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\qquake_options.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_qquake_options_widget_base(object):
    def setupUi(self, qquake_options_widget_base):
        qquake_options_widget_base.setObjectName("qquake_options_widget_base")
        qquake_options_widget_base.resize(629, 501)
        self.verticalLayout = QtWidgets.QVBoxLayout(qquake_options_widget_base)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(qquake_options_widget_base)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.style_label_edit = QtWidgets.QLineEdit(self.groupBox)
        self.style_label_edit.setObjectName("style_label_edit")
        self.gridLayout.addWidget(self.style_label_edit, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.style_type_combo = QtWidgets.QComboBox(self.groupBox)
        self.style_type_combo.setObjectName("style_type_combo")
        self.gridLayout.addWidget(self.style_type_combo, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.style_url_edit = QtWidgets.QLineEdit(self.groupBox)
        self.style_url_edit.setObjectName("style_url_edit")
        self.gridLayout.addWidget(self.style_url_edit, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 2, 1, 1)
        self.styles_list = QtWidgets.QListWidget(self.groupBox)
        self.styles_list.setObjectName("styles_list")
        self.gridLayout_2.addWidget(self.styles_list, 0, 0, 2, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.button_add_style = QtWidgets.QToolButton(self.groupBox)
        self.button_add_style.setObjectName("button_add_style")
        self.verticalLayout_2.addWidget(self.button_add_style)
        self.button_remove_style = QtWidgets.QToolButton(self.groupBox)
        self.button_remove_style.setObjectName("button_remove_style")
        self.verticalLayout_2.addWidget(self.button_remove_style)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 1, 2, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(qquake_options_widget_base)
        QtCore.QMetaObject.connectSlotsByName(qquake_options_widget_base)

    def retranslateUi(self, qquake_options_widget_base):
        _translate = QtCore.QCoreApplication.translate
        qquake_options_widget_base.setWindowTitle(_translate("qquake_options_widget_base", "Form"))
        self.groupBox.setTitle(_translate("qquake_options_widget_base", "Styles"))
        self.label.setText(_translate("qquake_options_widget_base", "Label"))
        self.label_2.setText(_translate("qquake_options_widget_base", "Type"))
        self.label_3.setText(_translate("qquake_options_widget_base", "URL"))
        self.button_add_style.setText(_translate("qquake_options_widget_base", "..."))
        self.button_remove_style.setText(_translate("qquake_options_widget_base", "..."))
