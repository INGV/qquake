# -*- coding: utf-8 -*-
"""
CQL builder widget
"""

# .. note:: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

__author__ = 'Original authors: Mario Locati, Roberto Vallone, Matteo Ghetta, Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Istituto Nazionale di Geofisica e Vulcanologia (INGV)'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import json
from functools import partial
from io import BytesIO
from typing import List

from qgis.PyQt import sip
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl, Qt
from qgis.PyQt.QtNetwork import (
    QNetworkRequest,
    QNetworkReply
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QTreeWidgetItem,
    QComboBox,
    QToolButton
)
from qgis.PyQt.QtGui import QDesktopServices

from qgis.core import (
    QgsNetworkAccessManager
)
from qgis.gui import (
    QgsGui,
)

from qquake.gui.gui_utils import GuiUtils

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('cql_filter_builder.ui'))


class CqlBuilderWidget(QWidget, FORM_CLASS):
    """
    CQL builder widget
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self.field_list.setHeaderLabels([self.tr('Field'), self.tr('Type')])
        self.simple_query_list.setHeaderLabels([self.tr('Field'), self.tr('Operator'), self.tr('Value'), ''])
        self.field_list.itemDoubleClicked.connect(self._field_double_clicked)
        self.button_add.clicked.connect(self._add_field)
        self.cql_help_button.clicked.connect(self._help)

        self.service_uri = None
        self.layer_names = []

        self.layers_def = {}
        self.layer_combo.currentIndexChanged.connect(self._layer_combo_changed)

    def set_service_uri(self, uri: str, layer_names: List[str]):
        """
        Sets the service URI
        """
        self.service_uri = uri
        self.layer_names = [CqlBuilderWidget._clean_layer_name(name) for name in layer_names]

        self._fetch_fields()

    def use_advanced_cql(self) -> bool:
        """
        Returns True if advanced query should be used
        """
        return self.tab_widget.currentIndex() == 1

    def set_use_advanced(self, use: bool):
        """
        Sets whether advanced query should be used
        """
        if use:
            self.tab_widget.setCurrentIndex(1)
        else:
            self.tab_widget.setCurrentIndex(0)

    def cql(self) -> str:
        """
        Returns the current CQL string
        """
        return self.sql_editor_widget.text()

    def set_cql(self, cql: str):
        """
        Sets the current CQL string
        """
        self.sql_editor_widget.setText(cql)

    def simple_query_fields(self) -> List:
        """
        Returns the simple query fields list
        """
        res = []
        for i in range(self.simple_query_list.topLevelItemCount()):
            item = self.simple_query_list.topLevelItem(i)
            field_name = item.text(0)
            field_value = item.text(2)

            operator = self.simple_query_list.itemWidget(item, 1).currentText()

            res.append((field_name, operator, field_value))
        return res

    def set_simple_query_fields(self, fields: List):
        """
        Sets the simple query fields
        """
        self.simple_query_list.clear()
        for f in fields:
            self._add_simple_query_item(*f)

    @staticmethod
    def _clean_layer_name(name: str) -> str:
        """
        Cleans an ogc layer name
        """
        try:
            return name[name.index(':') + 1:]
        except ValueError:
            return name

    def _fetch_fields(self):
        """
        Triggers fetching fields
        """
        if not self.service_uri:
            return

        self.label_fields.setText(self.tr('Fetching fields...'))

        # is_wms = 'wms' in self.service_uri
        # seems this must ALWAYS be WFS!
        url = self.service_uri + 'version=1.3.0&request=describeFeatureType&outputFormat=application/json&service={}'.format(
            'WFS')

        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        reply = QgsNetworkAccessManager.instance().get(request)

        def response_finished(_reply: QNetworkReply):
            """
            Triggered when the response is finished
            """
            if sip.isdeleted(self.label_fields):  # pylint:disable=no-member
                return

            self.label_fields.setText(self.tr('List of fields'))
            res = json.load(BytesIO(_reply.readAll().data()))

            self.layers_def = {}

            for _type in res['featureTypes']:
                type_name = _type['typeName']
                if CqlBuilderWidget._clean_layer_name(type_name) not in self.layer_names:
                    continue

                self.layer_combo.addItem(type_name)
                layer_fields = []
                for prop in _type['properties']:
                    layer_fields.append({'name': prop['name'], 'type': prop['localType']})
                self.layers_def[type_name] = layer_fields

            self._layer_combo_changed()

        reply.finished.connect(partial(response_finished, reply))

    def _layer_combo_changed(self):
        """
        Triggered when the layer combo selection is changed
        """
        current_layer = self.layer_combo.currentText()
        fields = self.layers_def.get(current_layer, [])

        self.field_list.clear()
        items = []
        for f in fields:
            item = QTreeWidgetItem()
            item.setText(0, f['name'])
            item.setText(1, f['type'])
            items.append(item)
        self.field_list.insertTopLevelItems(0, items)

    def _add_simple_query_item(self, field_name: str, operator: str = '=', value=None):
        """
        Adds a simple query item
        """
        combo = QComboBox()
        combo.addItem('=')
        combo.addItem('<')
        combo.addItem('<=')
        combo.addItem('>')
        combo.addItem('>=')
        combo.addItem('<>')
        combo.setCurrentIndex(combo.findText(operator))

        button = QToolButton()
        button.setIcon(GuiUtils.get_icon('remove.svg'))
        button.setAutoRaise(True)

        filter_item = QTreeWidgetItem()
        filter_item.setText(0, field_name)
        filter_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        filter_item.setText(2, value)
        self.simple_query_list.addTopLevelItem(filter_item)
        self.simple_query_list.setItemWidget(filter_item, 1, combo)
        self.simple_query_list.setItemWidget(filter_item, 3, button)

        button.clicked.connect(partial(self._remove_simple_item, filter_item))

    def _remove_simple_item(self, item: QTreeWidgetItem):
        """
        Removes a simple field item
        """
        index = self.simple_query_list.indexOfTopLevelItem(item)
        self.simple_query_list.takeTopLevelItem(index)

    def _field_double_clicked(self, item, _):
        """
        Triggered when a field is double clicked
        """
        if self.tab_widget.currentIndex() == 1:
            self.sql_editor_widget.insertText(item.text(0))
        else:
            self._add_simple_query_item(item.text(0))

    def _add_field(self):
        """
        Adds the current field
        """
        item = self.field_list.currentItem()
        self._field_double_clicked(item, 0)

    def _help(self):
        """
        Opens CQL help
        """
        QDesktopServices.openUrl(QUrl('https://docs.geoserver.org/stable/en/user/tutorials/cql/cql_tutorial.html'))


class CqlBuilderDialog(QDialog):
    """
    CQL builder dialog
    """

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setWindowTitle(self.tr('Add Data Filters'))

        QgsGui.enableAutoGeometryRestore(self)

        self.widget = CqlBuilderWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def cql(self) -> str:
        """
        Returns the current CQL string
        """
        return self.widget.cql()

    def simple_query_fields(self) -> List:
        """
        Returns the simple query fields list
        """
        return self.widget.simple_query_fields()

    def set_cql(self, cql: str):
        """
        Sets the current CQL string
        """
        self.widget.set_cql(cql)

    def set_simple_query_fields(self, fields: List):
        """
        Sets the simple query fields
        """
        self.widget.set_simple_query_fields(fields)

    def set_service_uri(self, uri: str, layer_names: List[str]):
        """
        Sets the service URI
        """
        self.widget.set_service_uri(uri, layer_names)

    def use_advanced_cql(self) -> bool:
        """
        Returns True if advanced query should be used
        """
        return self.widget.use_advanced_cql()

    def set_use_advanced(self, use: bool):
        """
        Sets whether advanced query should be used
        """
        self.widget.set_use_advanced(use)
