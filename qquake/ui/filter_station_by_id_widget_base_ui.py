# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filter_station_by_id_widget_base.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtWidgets


class Ui_filter_stations_by_id_widget_base(object):
    def setupUi(self, filter_stations_by_id_widget_base):
        filter_stations_by_id_widget_base.setObjectName("filter_stations_by_id_widget_base")
        filter_stations_by_id_widget_base.resize(640, 361)
        self.gridLayout = QtWidgets.QGridLayout(filter_stations_by_id_widget_base)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.edit_network_code = QtWidgets.QComboBox(filter_stations_by_id_widget_base)
        sizePolicy = QtWidgets.QSizePolicy(QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_FIXED)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_network_code.sizePolicy().hasHeightForWidth())
        self.edit_network_code.setSizePolicy(sizePolicy)
        self.edit_network_code.setEditable(True)
        self.edit_network_code.setInsertPolicy(QT_COMBOBOX_NO_INSERT)
        self.edit_network_code.setObjectName("edit_network_code")
        self.gridLayout.addWidget(self.edit_network_code, 0, 1, 1, 1)
        self.button_refresh_networks = QtWidgets.QToolButton(filter_stations_by_id_widget_base)
        self.button_refresh_networks.setObjectName("button_refresh_networks")
        self.gridLayout.addWidget(self.button_refresh_networks, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.edit_station_code = QtWidgets.QComboBox(filter_stations_by_id_widget_base)
        sizePolicy = QtWidgets.QSizePolicy(QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_FIXED)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_station_code.sizePolicy().hasHeightForWidth())
        self.edit_station_code.setSizePolicy(sizePolicy)
        self.edit_station_code.setEditable(True)
        self.edit_station_code.setInsertPolicy(QT_COMBOBOX_NO_INSERT)
        self.edit_station_code.setObjectName("edit_station_code")
        self.gridLayout.addWidget(self.edit_station_code, 1, 1, 1, 2)
        self.label_4 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.edit_location_code = QtWidgets.QLineEdit(filter_stations_by_id_widget_base)
        sizePolicy = QtWidgets.QSizePolicy(QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_FIXED)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_location_code.sizePolicy().hasHeightForWidth())
        self.edit_location_code.setSizePolicy(sizePolicy)
        self.edit_location_code.setObjectName("edit_location_code")
        self.gridLayout.addWidget(self.edit_location_code, 2, 1, 1, 2)
        self.label = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 1, 1, 2)
        self.output_table_options_widget = OutputTableOptionsWidget(filter_stations_by_id_widget_base)
        self.output_table_options_widget.setObjectName("output_table_options_widget")
        self.gridLayout.addWidget(self.output_table_options_widget, 7, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_EXPANDING)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 3)
        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 0)

        self.retranslateUi(filter_stations_by_id_widget_base)
        QtCore.QMetaObject.connectSlotsByName(filter_stations_by_id_widget_base)

    def retranslateUi(self, filter_stations_by_id_widget_base):
        _translate = QtCore.QCoreApplication.translate
        filter_stations_by_id_widget_base.setWindowTitle(_translate("filter_stations_by_id_widget_base", "Form"))
        self.label_2.setText(_translate("filter_stations_by_id_widget_base", "Network code"))
        self.button_refresh_networks.setText(_translate("filter_stations_by_id_widget_base", "Refresh"))
        self.label_3.setText(_translate("filter_stations_by_id_widget_base", "Station code"))
        self.label_4.setText(_translate("filter_stations_by_id_widget_base", "Location"))
        self.label.setText(_translate("filter_stations_by_id_widget_base", "Select from the list or type manually. Multiple IDs can be separated by a comma (\",\"). Wildcard characters (*) are also supported."))


from qquake.gui.output_table_options_widget import OutputTableOptionsWidget
from qquake.qt_compat import (
    QT_COMBOBOX_NO_INSERT,
    QT_SIZE_POLICY_EXPANDING,
    QT_SIZE_POLICY_FIXED,
    QT_SIZE_POLICY_MINIMUM,
)
