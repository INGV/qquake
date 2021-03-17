# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuake, a QGIS Plugin for Loading Seismological Data From Web Services
 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        git sha              : $Format:%H$
        copyright            : Istituto Nazionale di Geofisica e Vulcanologia (INGV)
        email                : mario.locati@ingv.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from copy import deepcopy

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import QModelIndex, Qt

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer
)

from qquake.services import SERVICE_MANAGER
from qquake.style_utils import StyleUtils
from qquake.gui.gui_utils import GuiUtils
from qquake.gui.simple_node_model import SimpleNodeModel, ModelNode

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('ogc_service_widget.ui'))


class OgcServiceWidget(QWidget, FORM_CLASS):

    def __init__(self, iface, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.layer_model = None
        self.service_type = None
        self.service_id = None
        self.service_config = None

        self.add_layers_button.clicked.connect(self.add_selected_layers)

    def set_service(self, service_id, service_type):
        self.service_type = service_type
        self.service_id = service_id
        self.service_config = SERVICE_MANAGER.service_details(service_type, service_id)
        layers = self.service_config['default']['layers']

        nodes = []
        for l in layers:
            if l.get('styles'):
                parent_node = ModelNode([l['layername']])
                checked_styles = l.get('checked_styles', None)
                for style in l['styles']:
                    checked = True if checked_styles is None else style in checked_styles
                    parent_node.addChild(
                        ModelNode(['checked', style], checked))
            else:
                style = l.get('style', {}).get('wfs', {}).get('style', None)
                parent_node = ModelNode(['checked', l['layername']], True, {'style': style})

            nodes.append(parent_node)

        self.layer_model = SimpleNodeModel(nodes, headers=[self.tr('Selected'), self.tr('Style Name')])
        self.layers_tree_view.setModel(self.layer_model)
        self.layers_tree_view.expandAll()

        for r in range(self.layer_model.rowCount(QModelIndex())):
            if self.layer_model.flags(self.layer_model.index(r, 0, QModelIndex())) & Qt.ItemIsUserCheckable:
                continue

            self.layers_tree_view.setFirstColumnSpanned(r, QModelIndex(), True)

    def add_selected_layers(self):
        def add_layer(layer_name, style=None, preset_style=None):
            if self.service_type == SERVICE_MANAGER.WFS:
                uri = "pagingEnabled='true' restrictToRequestBBOX='1' srsname='{}' typename='{}' url='{}' version='auto'".format(
                    self.service_config['srs'],
                    layer_name,
                    self.service_config['endpointurl'])
                vl = QgsVectorLayer(uri, layer_name, 'WFS')

                if preset_style.get('style') and preset_style['style'] in SERVICE_MANAGER.PRESET_STYLES:
                    style_url = SERVICE_MANAGER.PRESET_STYLES[preset_style['style']]['url']
                    StyleUtils.fetch_and_apply_style(vl, style_url)

                layers_to_add.append(vl)
            elif self.service_type == SERVICE_MANAGER.WMS:
                if style:
                    uri = "contextualWMSLegend=0&crs={}&dpiMode=7&format=image/png&layers={}&styles={}&url={}".format(
                        self.service_config['srs'],
                        layer_name,
                        style,
                        self.service_config['endpointurl']
                    )
                    layer_name += ' ({})'.format(style)
                else:
                    uri = "contextualWMSLegend=0&crs={}&dpiMode=7&format=image/png&layers={}&styles&url={}".format(
                        self.service_config['srs'],
                        layer_name,
                        self.service_config['endpointurl']
                    )
                rl = QgsRasterLayer(uri, layer_name, 'wms')
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

    def is_style_selected(self, layer, style):
        for r in range(self.layer_model.rowCount(QModelIndex())):
            parent = self.layer_model.index(r, 0, QModelIndex())

            if self.layer_model.flags(parent) & Qt.ItemIsUserCheckable:
                continue
            else:
                if self.layer_model.data(parent, Qt.DisplayRole) == layer:
                    for rc in range(self.layer_model.rowCount(parent)):
                        row_style = self.layer_model.data(self.layer_model.index(rc, 1, parent), Qt.DisplayRole)
                        if style == row_style:
                            return self.layer_model.data(self.layer_model.index(rc, 0, parent), Qt.CheckStateRole)
        return False

    def to_service_definition(self):
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
