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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import (
    QNetworkRequest,
    QNetworkReply
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QTreeWidgetItem
)
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
        self.field_list.itemDoubleClicked.connect(self._field_double_clicked)
        self.button_add.clicked.connect(self._add_field)

        self.service_uri = None
        self.layer_names = []

        self.layers_def = {}
        self.layer_combo.currentIndexChanged.connect(self._layer_combo_changed)

    def set_service_uri(self, uri: str, layer_names: List[str]):
        """
        Sets the service URI
        """
        self.service_uri = uri
        self.layer_names = layer_names

        self._fetch_fields()

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
            self.label_fields.setText(self.tr('List of fields'))
            res = json.load(BytesIO(_reply.readAll().data()))

            self.layers_def = {}

            for _type in res['featureTypes']:
                type_name = _type['typeName']
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

    def _field_double_clicked(self, item, _):
        """
        Triggered when a field is double clicked
        """
        if self.tab_widget.currentIndex() == 1:

            self.sql_editor_widget.insertText(item.text(0))
        else:
            pass

    def _add_field(self):
        """
        Adds the current field
        """
        item = self.field_list.currentItem()
        self._field_double_clicked(item, 0)


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

    def accept(self):  # pylint: disable=missing-function-docstring
        super().accept()

    def cql(self) -> str:
        """
        Returns the current CQL string
        """
        return self.widget.cql()

    def set_cql(self, cql: str):
        """
        Sets the current CQL string
        """
        self.widget.set_cql(cql)

    def set_service_uri(self, uri: str, layer_names: List[str]):
        """
        Sets the service URI
        """
        self.widget.set_service_uri(uri, layer_names)
