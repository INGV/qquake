# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\filter_by_id_widget_base.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_filter_by_id_widget_base(object):
    def setupUi(self, filter_by_id_widget_base):
        filter_by_id_widget_base.setObjectName("filter_by_id_widget_base")
        filter_by_id_widget_base.resize(564, 453)
        self.verticalLayout = QtWidgets.QVBoxLayout(filter_by_id_widget_base)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll_area = QtWidgets.QScrollArea(filter_by_id_widget_base)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 564, 453))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, -1, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.radio_single_event = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_single_event.setChecked(True)
        self.radio_single_event.setObjectName("radio_single_event")
        self.buttonGroup = QtWidgets.QButtonGroup(filter_by_id_widget_base)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radio_single_event)
        self.gridLayout.addWidget(self.radio_single_event, 0, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.label_event_id = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_event_id.setObjectName("label_event_id")
        self.gridLayout.addWidget(self.label_event_id, 1, 1, 1, 1)
        self.edit_event_id = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.edit_event_id.setObjectName("edit_event_id")
        self.gridLayout.addWidget(self.edit_event_id, 1, 2, 1, 1)
        self.radio_multiple_events = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_multiple_events.setChecked(False)
        self.radio_multiple_events.setObjectName("radio_multiple_events")
        self.buttonGroup.addButton(self.radio_multiple_events)
        self.gridLayout.addWidget(self.radio_multiple_events, 2, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.multi_event_widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.multi_event_widget.setObjectName("multi_event_widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.multi_event_widget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtWidgets.QLabel(self.multi_event_widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.button_import_from_file = QtWidgets.QPushButton(self.multi_event_widget)
        self.button_import_from_file.setObjectName("button_import_from_file")
        self.gridLayout_3.addWidget(self.button_import_from_file, 2, 1, 1, 1)
        self.event_ids_edit = QtWidgets.QPlainTextEdit(self.multi_event_widget)
        self.event_ids_edit.setObjectName("event_ids_edit")
        self.gridLayout_3.addWidget(self.event_ids_edit, 1, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.multi_event_widget)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.multi_event_widget, 3, 1, 1, 2)
        self.radio_contributor = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_contributor.setObjectName("radio_contributor")
        self.buttonGroup.addButton(self.radio_contributor)
        self.gridLayout.addWidget(self.radio_contributor, 4, 0, 1, 2)
        self.label_contributor_id = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_contributor_id.setObjectName("label_contributor_id")
        self.gridLayout.addWidget(self.label_contributor_id, 5, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.edit_contributor_id = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.edit_contributor_id.setEditable(True)
        self.edit_contributor_id.setObjectName("edit_contributor_id")
        self.horizontalLayout.addWidget(self.edit_contributor_id)
        self.button_refresh_contributors = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.button_refresh_contributors.setObjectName("button_refresh_contributors")
        self.horizontalLayout.addWidget(self.button_refresh_contributors)
        self.horizontalLayout.setStretch(0, 1)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 2, 1, 1)
        self.output_options_widget = OutputOptionsWidget(self.scrollAreaWidgetContents)
        self.output_options_widget.setObjectName("output_options_widget")
        self.gridLayout.addWidget(self.output_options_widget, 6, 0, 1, 3)
        self.output_table_options_widget = OutputTableOptionsWidget(self.scrollAreaWidgetContents)
        self.output_table_options_widget.setObjectName("output_table_options_widget")
        self.gridLayout.addWidget(self.output_table_options_widget, 7, 0, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 8, 0, 1, 1)
        self.scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scroll_area)

        self.retranslateUi(filter_by_id_widget_base)
        QtCore.QMetaObject.connectSlotsByName(filter_by_id_widget_base)

    def retranslateUi(self, filter_by_id_widget_base):
        _translate = QtCore.QCoreApplication.translate
        filter_by_id_widget_base.setWindowTitle(_translate("filter_by_id_widget_base", "Form"))
        self.radio_single_event.setText(_translate("filter_by_id_widget_base", "Single event"))
        self.label_event_id.setText(_translate("filter_by_id_widget_base", "Event ID"))
        self.radio_multiple_events.setText(_translate("filter_by_id_widget_base", "Multiple events"))
        self.label_2.setText(_translate("filter_by_id_widget_base", "Or import a text file containing Event IDs"))
        self.button_import_from_file.setText(_translate("filter_by_id_widget_base", "Import from File…"))
        self.label.setText(_translate("filter_by_id_widget_base", "Enter a list of Event IDs separated by commas or line breaks"))
        self.radio_contributor.setText(_translate("filter_by_id_widget_base", "Contributor"))
        self.label_contributor_id.setText(_translate("filter_by_id_widget_base", "Contributor ID"))
        self.button_refresh_contributors.setText(_translate("filter_by_id_widget_base", "Refresh"))
from qquake.gui.output_options_widget import OutputOptionsWidget
from qquake.gui.output_table_options_widget import OutputTableOptionsWidget
