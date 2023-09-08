# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\filter_station_by_id_widget_base.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_filter_stations_by_id_widget_base(object):
    def setupUi(self, filter_stations_by_id_widget_base):
        filter_stations_by_id_widget_base.setObjectName("filter_stations_by_id_widget_base")
        filter_stations_by_id_widget_base.resize(523, 361)
        self.gridLayout = QtWidgets.QGridLayout(filter_stations_by_id_widget_base)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.output_table_options_widget = OutputTableOptionsWidget(filter_stations_by_id_widget_base)
        self.output_table_options_widget.setObjectName("output_table_options_widget")
        self.gridLayout.addWidget(self.output_table_options_widget, 7, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.edit_station_code = QtWidgets.QLineEdit(filter_stations_by_id_widget_base)
        self.edit_station_code.setObjectName("edit_station_code")
        self.gridLayout.addWidget(self.edit_station_code, 1, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 2)
        self.edit_location_code = QtWidgets.QLineEdit(filter_stations_by_id_widget_base)
        self.edit_location_code.setObjectName("edit_location_code")
        self.gridLayout.addWidget(self.edit_location_code, 2, 2, 1, 1)
        self.edit_network_code = QtWidgets.QLineEdit(filter_stations_by_id_widget_base)
        self.edit_network_code.setObjectName("edit_network_code")
        self.gridLayout.addWidget(self.edit_network_code, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(filter_stations_by_id_widget_base)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)

        self.retranslateUi(filter_stations_by_id_widget_base)
        QtCore.QMetaObject.connectSlotsByName(filter_stations_by_id_widget_base)

    def retranslateUi(self, filter_stations_by_id_widget_base):
        _translate = QtCore.QCoreApplication.translate
        filter_stations_by_id_widget_base.setWindowTitle(_translate("filter_stations_by_id_widget_base", "Form"))
        self.label_4.setText(_translate("filter_stations_by_id_widget_base", "Location"))
        self.label.setText(_translate("filter_stations_by_id_widget_base", "Multiple IDs can be separated by a comma (\",\"). Wildcard characters (*) are also supported."))
        self.label_3.setText(_translate("filter_stations_by_id_widget_base", "Station code"))
        self.label_2.setText(_translate("filter_stations_by_id_widget_base", "Network code"))
from qquake.gui.output_table_options_widget import OutputTableOptionsWidget
