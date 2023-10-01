# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\output_table_options.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(596, 539)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.button_box = QtWidgets.QDialogButtonBox(Form)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.gridLayout_2.addWidget(self.button_box, 3, 0, 1, 2)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.check_all_button = QtWidgets.QPushButton(self.groupBox)
        self.check_all_button.setObjectName("check_all_button")
        self.gridLayout.addWidget(self.check_all_button, 3, 1, 1, 1)
        self.fields_tree_view = QtWidgets.QTreeView(self.groupBox)
        self.fields_tree_view.setObjectName("fields_tree_view")
        self.gridLayout.addWidget(self.fields_tree_view, 1, 0, 1, 4)
        self.reset_fields_button = QtWidgets.QPushButton(self.groupBox)
        self.reset_fields_button.setObjectName("reset_fields_button")
        self.gridLayout.addWidget(self.reset_fields_button, 3, 3, 1, 1)
        self.uncheck_all_button = QtWidgets.QPushButton(self.groupBox)
        self.uncheck_all_button.setObjectName("uncheck_all_button")
        self.gridLayout.addWidget(self.uncheck_all_button, 3, 2, 1, 1)
        self.check_include_event_params_in_mdp = QtWidgets.QCheckBox(self.groupBox)
        self.check_include_event_params_in_mdp.setChecked(True)
        self.check_include_event_params_in_mdp.setObjectName("check_include_event_params_in_mdp")
        self.gridLayout.addWidget(self.check_include_event_params_in_mdp, 0, 0, 1, 4)
        self.gridLayout_2.addWidget(self.groupBox, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.output_features_group_box = QtWidgets.QGroupBox(Form)
        self.output_features_group_box.setObjectName("output_features_group_box")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.output_features_group_box)
        self.verticalLayout_2.setContentsMargins(-1, -1, 33, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.output_preferred_origins_only_check = QtWidgets.QCheckBox(self.output_features_group_box)
        self.output_preferred_origins_only_check.setObjectName("output_preferred_origins_only_check")
        self.verticalLayout_2.addWidget(self.output_preferred_origins_only_check)
        self.output_preferred_magnitudes_only_check = QtWidgets.QCheckBox(self.output_features_group_box)
        self.output_preferred_magnitudes_only_check.setObjectName("output_preferred_magnitudes_only_check")
        self.verticalLayout_2.addWidget(self.output_preferred_magnitudes_only_check)
        self.output_preferred_mdp_only_check = QtWidgets.QCheckBox(self.output_features_group_box)
        self.output_preferred_mdp_only_check.setObjectName("output_preferred_mdp_only_check")
        self.verticalLayout_2.addWidget(self.output_preferred_mdp_only_check)
        self.horizontalLayout.addWidget(self.output_features_group_box)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radio_short_fields = QtWidgets.QRadioButton(self.groupBox_3)
        self.radio_short_fields.setObjectName("radio_short_fields")
        self.gridLayout_3.addWidget(self.radio_short_fields, 0, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 4, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 2)
        self.radio_long_fields = QtWidgets.QRadioButton(self.groupBox_3)
        self.radio_long_fields.setObjectName("radio_long_fields")
        self.gridLayout_3.addWidget(self.radio_long_fields, 3, 0, 1, 2)
        self.horizontalLayout.addWidget(self.groupBox_3)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.gridLayout_2.setRowStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Output Table Fields"))
        self.check_all_button.setText(_translate("Form", "Check All"))
        self.reset_fields_button.setText(_translate("Form", "Reset to Defaults"))
        self.uncheck_all_button.setText(_translate("Form", "Uncheck All"))
        self.check_include_event_params_in_mdp.setText(_translate("Form", "Include earthquake parameters in MDP layer"))
        self.output_features_group_box.setTitle(_translate("Form", "Output Features"))
        self.output_preferred_origins_only_check.setText(_translate("Form", "Only preferred origins"))
        self.output_preferred_magnitudes_only_check.setText(_translate("Form", "Only preferred magnitudes"))
        self.output_preferred_mdp_only_check.setText(_translate("Form", "Only preferred MDP set"))
        self.groupBox_3.setTitle(_translate("Form", "Field Names"))
        self.radio_short_fields.setText(_translate("Form", "Short (max 10 characters)"))
        self.label_2.setText(_translate("Form", "<i>Not compatible with ESRI ShapeFiles</i>"))
        self.label.setText(_translate("Form", "<i>Compatible with ESRI ShapeFiles</i>"))
        self.radio_long_fields.setText(_translate("Form", "Long (no character limit)"))