# -*- coding: utf-8 -*-
"""
OGC service options widget
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

import urllib.parse
from copy import deepcopy
from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, Qt
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer
)

from qquake.gui.cql_builder_widget import CqlBuilderDialog
from qquake.gui.gui_utils import GuiUtils
from qquake.gui.simple_node_model import SimpleNodeModel, ModelNode
from qquake.services import SERVICE_MANAGER
from qquake.style_utils import StyleUtils

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('ogc_service_widget.ui'))


class OgcServiceWidget(QWidget, FORM_CLASS):
    """
    OGC service options widget
    """

    def __init__(self, iface, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.layer_model = None
        self.service_type = None
        self.service_id = None
        self.service_config = None

        self.use_advanced_cql = False
        self.cql = None
        self.simple_cql = []

        self.button_set_filter.clicked.connect(self._set_filter)

    def restore_settings(self):
        """
        Restores widget settings
        """

    def save_settings(self):
        """
        Saves widget settings
        """

    def set_service(self, service_id: str, service_type: str):
        """
        Sets the service details
        """
        self.service_type = service_type
        self.service_id = service_id
        self.service_config = SERVICE_MANAGER.service_details(service_type, service_id)
        layers = self.service_config['default']['layers']

        cql_available = self.service_config.get('settings', {}).get('queryCQL', False)
        if not cql_available:
            self.cql = None
            self.simple_cql = []
            self.cql_filter_label.setText('')
        self.button_set_filter.setEnabled(cql_available)

        nodes = []
        for layer in layers:
            if layer.get('styles'):
                parent_node = ModelNode([layer['layername']])
                checked_styles = layer.get('checked_styles', None)
                for style in layer['styles']:
                    checked = True if checked_styles is None else style in checked_styles
                    parent_node.addChild(
                        ModelNode(['checked', style], checked))
            else:
                if self.service_type == SERVICE_MANAGER.WFS:
                    style = layer.get('style', {}).get('wfs', {}).get('style', None)
                elif self.service_type == SERVICE_MANAGER.WCS:
                    style = layer.get('style', {}).get('wcs', {}).get('style', None)
                parent_node = ModelNode(['checked', layer['layername']], True, {'style': style})

            nodes.append(parent_node)

        self.layer_model = SimpleNodeModel(nodes, headers=[self.tr('Selected'), self.tr('Style Name')])
        self.layers_tree_view.setModel(self.layer_model)
        self.layers_tree_view.expandAll()

        for r in range(self.layer_model.rowCount(QModelIndex())):
            if self.layer_model.flags(self.layer_model.index(r, 0, QModelIndex())) & Qt.ItemIsUserCheckable:
                continue

            self.layers_tree_view.setFirstColumnSpanned(r, QModelIndex(), True)

    def add_selected_layers(self):
        """
        Adds all selected layers to the project
        """

        def add_layer(layer_name, style=None, preset_style=None):
            cql = self.get_cql_query()
            if self.service_type == SERVICE_MANAGER.WFS:
                end_point = self.service_config['endpointurl']
                if cql:
                    if not end_point.endswith('?'):
                        end_point += '?'

                    end_point += 'CQL_FILTER=' + urllib.parse.quote(cql)

                uri = "pagingEnabled='true'"
                if not cql:
                    uri += " restrictToRequestBBOX='1'"

                uri += " srsname='{}' typename='{}' url='{}' version='auto'".format(
                    self.service_config['srs'],
                    layer_name,
                    end_point)
                vl = QgsVectorLayer(uri, layer_name, 'WFS')

                if preset_style.get('style') and preset_style['style'] in SERVICE_MANAGER.PRESET_STYLES:
                    style_url = SERVICE_MANAGER.PRESET_STYLES[preset_style['style']]['url']
                    StyleUtils.fetch_and_apply_style(vl, style_url)

                layers_to_add.append(vl)
            elif self.service_type == SERVICE_MANAGER.WMS:
                base_uri = 'contextualWMSLegend=0&crs={}&dpiMode=7&format=image/png&layers={}'.format(
                    self.service_config['srs'],
                    layer_name
                )

                if style:
                    uri = base_uri + "&styles={}".format(
                        style
                    )
                    layer_name += ' ({})'.format(style)
                else:
                    uri = base_uri + "&styles"

                uri += "&url={}".format(
                    self.service_config['endpointurl']
                )

                if cql:
                    uri += 'CQL_FILTER=' + urllib.parse.quote(cql)
                    uri = 'IgnoreGetMapUrl=1&' + uri

                rl = QgsRasterLayer(uri, layer_name, 'wms')
                layers_to_add.append(rl)
            elif self.service_type == SERVICE_MANAGER.WCS:
                base_uri = "cache=PreferNetwork&crs={}&dpiMode=7&format=GeoTIFF&identifier={}&url={} version='auto'".format(
                    self.service_config['srs'],
                    layer_name,
                    self.service_config['endpointurl'])
                
                if style:
                    uri = base_uri + "&styles={}".format(
                        style
                    )
                    layer_name += ' ({})'.format(style)
                else:
                    uri = base_uri + "&styles"
                
                rl = QgsRasterLayer(uri, layer_name, 'wcs')

                if preset_style.get('style') and preset_style['style'] in SERVICE_MANAGER.PRESET_STYLES:
                    style_url = SERVICE_MANAGER.PRESET_STYLES[preset_style['style']]['url']
                    StyleUtils.fetch_and_apply_style(rl, style_url)

                layers_to_add.append(rl)

        layers_to_add = []
        for r in range(self.layer_model.rowCount(QModelIndex())):
            parent = self.layer_model.index(r, 0, QModelIndex())

            if self.layer_model.flags(parent) & Qt.ItemIsUserCheckable:
                layer_name = self.layer_model.data(self.layer_model.index(r, 1, QModelIndex()), Qt.DisplayRole)
                preset_style = self.layer_model.data(self.layer_model.index(r, 1, QModelIndex()), Qt.UserRole)
                add_layer(layer_name, preset_style=preset_style)
            else:
                layer_name = self.layer_model.data(parent, Qt.DisplayRole)
                for rc in range(self.layer_model.rowCount(parent)):
                    style = self.layer_model.data(self.layer_model.index(rc, 1, parent), Qt.DisplayRole)
                    checked = self.layer_model.data(self.layer_model.index(rc, 0, parent), Qt.CheckStateRole)
                    if not checked:
                        continue
                    add_layer(layer_name, style)

        QgsProject.instance().addMapLayers(layers_to_add)

    def selected_layer_names(self) -> List[str]:
        """
        Returns a list of selected layer names
        """
        layers = []
        for r in range(self.layer_model.rowCount(QModelIndex())):
            parent = self.layer_model.index(r, 0, QModelIndex())

            if self.layer_model.flags(parent) & Qt.ItemIsUserCheckable:
                layer_name = self.layer_model.data(self.layer_model.index(r, 1, QModelIndex()), Qt.DisplayRole)
                layers.append(layer_name)
            else:
                layer_name = self.layer_model.data(parent, Qt.DisplayRole)
                layers.append(layer_name)

        return layers

    def is_style_selected(self, layer, style) -> bool:
        """
        Returns True if a style entry is selected
        """
        for r in range(self.layer_model.rowCount(QModelIndex())):
            parent = self.layer_model.index(r, 0, QModelIndex())

            if self.layer_model.flags(parent) & Qt.ItemIsUserCheckable:
                continue

            if self.layer_model.data(parent, Qt.DisplayRole) == layer:
                for rc in range(self.layer_model.rowCount(parent)):
                    row_style = self.layer_model.data(self.layer_model.index(rc, 1, parent), Qt.DisplayRole)
                    if style == row_style:
                        return self.layer_model.data(self.layer_model.index(rc, 0, parent), Qt.CheckStateRole)
        return False

    def to_service_definition(self) -> dict:
        """
        Converts the dialog settings to a service definition
        """
        base_config = deepcopy(SERVICE_MANAGER.service_details(self.service_type, self.service_id))

        defaults = base_config.get('default', {})

        for layer in defaults.get('layers', []):
            selected_styles = []
            for style in layer.get('styles', []):
                if self.is_style_selected(layer.get('layername'), style):
                    selected_styles.append(style)
            layer['checked_styles'] = selected_styles

        base_config['default'] = defaults
        return base_config

    def _set_filter(self):
        """
        Sets the CQL filter
        """
        end_point = self.service_config['endpointurl']

        w = CqlBuilderDialog(self)
        w.set_service_uri(end_point, self.selected_layer_names())
        if self.cql:
            w.set_cql(self.cql)
        if self.simple_cql:
            w.set_simple_query_fields(self.simple_cql)
        w.set_use_advanced(self.use_advanced_cql)

        if w.exec_():
            self.cql = w.cql()
            self.simple_cql = w.simple_query_fields()
            self.use_advanced_cql = w.use_advanced_cql()
            self.cql_filter_label.setText(self.get_cql_query())

    def get_cql_query(self) -> str:
        """
        Gets the defined cql query
        """
        if self.use_advanced_cql:
            return self.cql

        parts = []
        for name, operator, value in self.simple_cql:
            try:
                field_value = str(float(value))
            except ValueError:
                field_value = "'{}'".format(value)

            part = name + operator + field_value
            parts.append(part)
        return ' AND '.join(parts)
