# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\giorg\AppData\Roaming\QGIS\QGIS3\profiles\qquake\python\plugins\qquake\ui\fetch_by_url_widget.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_fetch_by_url_widget_base(object):
    def setupUi(self, fetch_by_url_widget_base):
        fetch_by_url_widget_base.setObjectName("fetch_by_url_widget_base")
        fetch_by_url_widget_base.resize(441, 499)
        self.verticalLayout = QtWidgets.QVBoxLayout(fetch_by_url_widget_base)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll_area = QtWidgets.QScrollArea(fetch_by_url_widget_base)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 441, 499))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_event_id = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_event_id.setObjectName("label_event_id")
        self.verticalLayout_2.addWidget(self.label_event_id)
        self.url_edit = QtWidgets.QPlainTextEdit(self.scrollAreaWidgetContents)
        self.url_edit.setObjectName("url_edit")
        self.verticalLayout_2.addWidget(self.url_edit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_import_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_import_file.setObjectName("label_import_file")
        self.horizontalLayout.addWidget(self.label_import_file)
        self.import_file_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.import_file_button.setObjectName("import_file_button")
        self.horizontalLayout.addWidget(self.import_file_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.multi_event_widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.multi_event_widget.setObjectName("multi_event_widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.multi_event_widget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_2.addWidget(self.multi_event_widget)
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.output_options_widget = OutputOptionsWidget(self.scrollAreaWidgetContents)
        self.output_options_widget.setObjectName("output_options_widget")
        self.verticalLayout_2.addWidget(self.output_options_widget)
        self.output_table_options_widget = OutputTableOptionsWidget(self.scrollAreaWidgetContents)
        self.output_table_options_widget.setObjectName("output_table_options_widget")
        self.verticalLayout_2.addWidget(self.output_table_options_widget)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scroll_area)

        self.retranslateUi(fetch_by_url_widget_base)
        QtCore.QMetaObject.connectSlotsByName(fetch_by_url_widget_base)

    def retranslateUi(self, fetch_by_url_widget_base):
        _translate = QtCore.QCoreApplication.translate
        fetch_by_url_widget_base.setWindowTitle(_translate("fetch_by_url_widget_base", "Form"))
        self.label_event_id.setText(_translate("fetch_by_url_widget_base", "URL"))
        self.label_import_file.setText(_translate("fetch_by_url_widget_base", "Or import a local QuakeML file"))
        self.import_file_button.setText(_translate("fetch_by_url_widget_base", "Import from File…"))
from qquake.gui.output_options_widget import OutputOptionsWidget
from qquake.gui.output_table_options_widget import OutputTableOptionsWidget
