# -*- coding: utf-8 -*-
"""
A widget for defining a service configuration
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
from copy import deepcopy
from functools import partial
from typing import Optional, Tuple, Dict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QDateTime,
    Qt,
    pyqtSignal,
    QUrl
)
from qgis.PyQt.QtNetwork import (
    QNetworkRequest,
    QNetworkReply
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QCheckBox,
    QSpinBox
)
from qgis.core import (
    Qgis,
    QgsNetworkAccessManager
)
from qgis.gui import (
    QgsGui,
)

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER, WadlServiceParser

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('service_configuration_widget_base.ui'))


class ServiceConfigurationWidget(QWidget, FORM_CLASS):
    """
    A widget for defining a service configuration
    """

    WIDGET_MAP = {
        'queryeventid': 'check_filter_by_eventid',
        'queryoriginid': 'check_filter_by_originid',
        'querymagnitudeid': 'check_filter_by_magnitudeid',
        'queryfocalmechanismid': 'check_filter_by_focalmechanismid',
        'queryupdatedafter': 'check_filter_data_updated_after',
        'querycatalog': 'check_filter_by_catalog',
        'querycontributor': 'check_filter_by_contributor',
        'querycontributorid': 'check_filter_by_contributorid',
        'queryeventtype': 'check_filter_by_event_type',
        'querymagnitudetype': 'check_filter_by_magnitude_type',
        'queryincludeallorigins': 'check_can_include_all_origins',
        'queryincludeallmagnitudes': 'check_can_include_all_magnitudes',
        'queryincludeallorigins_multiple': 'check_can_include_all_origins_multiple',
        'queryincludeallmagnitudes_multiple': 'check_can_include_all_magnitudes_multiple',
        'queryincludearrivals': 'check_can_include_arrivals',
        'queryincludeallstationsmagnitudes': 'check_can_include_all_stations_magnitudes',
        'querylimit': 'check_has_limit_of_entries',
        'querylimitmaxentries': 'spin_has_limit_of_entries',
        'querycircular': 'check_can_filter_using_circular_area',
        'querycircularradiuskm': 'check_radius_of_circular_area_is_specified_in_km',
        'querydepth': 'check_can_filter_by_depth',
        'outputtext': 'check_can_output_text',
        'outputxml': 'check_can_output_xml',
        'outputgeojson': 'check_can_output_geojson',
        'outputjson': 'check_can_output_json',
        'outputkml': 'check_can_output_kml',
        'outputxlsx': 'check_can_output_microsoft_xlsx',
        'group': 'group_edit'
    }

    validChanged = pyqtSignal(bool)

    def __init__(self, iface,  # pylint: disable=unused-argument,too-many-branches,too-many-statements
                 service_type: str,
                 service_id: str,
                 parent: Optional[QWidget] = None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.qml_style_name_combo_events.addItem('')
        self.qml_style_name_combo_mdp.addItem('')
        self.qml_style_name_combo_stations.addItem('')

        self.label_qml_events.setVisible(service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))
        self.qml_style_url_edit_events.setVisible(
            service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))
        self.label_preset_style_events.setVisible(
            service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))
        self.qml_style_name_combo_events.setVisible(
            service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))
        self.label_mdp_url.setVisible(service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.qml_style_url_edit_mdp.setVisible(service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.qml_style_name_combo_mdp.setVisible(service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.mdp_preset_label.setVisible(service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.label_stations_url.setVisible(service_type == SERVICE_MANAGER.FDSNSTATION)
        self.qml_style_url_edit_stations.setVisible(service_type == SERVICE_MANAGER.FDSNSTATION)
        self.label_preset_name_stations.setVisible(service_type == SERVICE_MANAGER.FDSNSTATION)
        self.qml_style_name_combo_stations.setVisible(service_type == SERVICE_MANAGER.FDSNSTATION)

        for name in SERVICE_MANAGER.styles_for_service_type(SERVICE_MANAGER.FDSNEVENT):
            self.qml_style_name_combo_events.addItem(SERVICE_MANAGER.get_style(name)['label'], name)

        for name in SERVICE_MANAGER.styles_for_service_type(SERVICE_MANAGER.MACROSEISMIC):
            self.qml_style_name_combo_mdp.addItem(SERVICE_MANAGER.get_style(name)['label'], name)

        for name in SERVICE_MANAGER.styles_for_service_type(SERVICE_MANAGER.FDSNSTATION):
            self.qml_style_name_combo_stations.addItem(SERVICE_MANAGER.get_style(name)['label'], name)

        self.service_type = service_type
        self.service_id = service_id

        self.start_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        if service_id in SERVICE_MANAGER.available_services(service_type):
            config = SERVICE_MANAGER.service_details(service_type, service_id)
        else:
            # this is the default configuration for a newly created service!
            config = {
                'settings': {
                    'outputxml': True,
                    'httpcodenodata': True
                }
            }
        self.set_state_from_config(config)

        self.title_edit.textChanged.connect(self._changed)
        self.web_service_url_edit.textChanged.connect(self._changed)

        self.combo_http_code_nodata.addItem('204', '204')

        for _, w in self.WIDGET_MAP.items():
            widget = getattr(self, w)
            if isinstance(widget, QCheckBox):
                widget.toggled.connect(self._changed)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._changed)
        self.check_http_code_nodata.toggled.connect(self._changed)
        self.combo_http_code_nodata.currentIndexChanged.connect(self._changed)

        if self.service_type in (SERVICE_MANAGER.WMS, SERVICE_MANAGER.WFS, SERVICE_MANAGER.WCS):
            for w in [self.group_capabilities, self.group_bounding_box]:
                w.setEnabled(False)
                w.hide()
        else:
            self.group_ogc_layers.setEnabled(False)
            self.group_ogc_layers.hide()
            self.group_label.hide()
            self.group_edit.hide()

        if self.service_type == SERVICE_MANAGER.FDSNSTATION:
            for w in [self.check_filter_by_eventid,
                      self.check_filter_by_originid,
                      self.check_filter_by_magnitudeid,
                      self.check_filter_by_focalmechanismid,
                      self.check_filter_by_catalog,
                      self.check_filter_by_contributor,
                      self.check_filter_by_contributorid,
                      self.check_filter_by_event_type,
                      self.check_filter_by_magnitude_type,
                      self.check_can_include_all_origins,
                      self.check_can_include_all_magnitudes,
                      self.check_can_include_all_origins_multiple,
                      self.check_can_include_all_magnitudes_multiple,
                      self.check_can_include_arrivals,
                      self.check_can_include_all_stations_magnitudes,
                      self.check_has_limit_of_entries,
                      self.spin_has_limit_of_entries,
                      self.check_can_filter_by_depth]:
                w.setEnabled(False)

        self.button_load_service.clicked.connect(self._load_service)
        self._changed()

    def _changed(self):
        """
        Triggered when the widget state is changed
        """
        self.combo_http_code_nodata.setEnabled(self.check_http_code_nodata.isChecked())
        self.spin_has_limit_of_entries.setEnabled(self.check_has_limit_of_entries.isChecked())

        res, reason = self.is_valid()
        if not res:
            self.message_bar.clearWidgets()
            self.message_bar.pushMessage('', reason, Qgis.Warning, 0)
            self.validChanged.emit(False)
        else:
            self.message_bar.clearWidgets()
            self.validChanged.emit(True)

        self.button_load_service.setEnabled(bool(self.web_service_url_edit.text()))

    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Returns whether the widget state is valid, and an optional error message
        """
        if not self.title_edit.text():
            return False, self.tr('A title must be entered')

        if not self.web_service_url_edit.text():
            return False, self.tr('The web service URL must be entered')

        return True, None

    def set_state_from_config(self, config: dict):  # pylint: disable=too-many-branches,too-many-statements
        """
        Sets the widget state from a service configuration
        """
        self.title_edit.setText(config.get('title'))
        self.service_description_edit.setText(config.get('servicedescription'))
        self.service_description_url_edit.setText(config.get('servicedescriptionurl'))
        self.data_description_edit.setText(config.get('datadescription'))
        self.group_edit.setText(config.get('group'))
        self.data_description_url_edit.setText(config.get('datadescriptionurl'))
        self.publications_text_edit.setPlainText(
            '\n'.join(config.get('publications')) if isinstance(config.get('publications'), list) else str(
                config.get('publications')))
        self.webservice_manual_url_edit.setText(config.get('manualurl'))
        self.data_license_edit.setText(config.get('datalicense'))
        self.data_license_url_edit.setText(config.get('datalicenseurl'))
        self.data_provider_edit.setText(config.get('dataprovider'))
        self.data_provider_url_edit.setText(config.get('dataproviderurl'))
        self.web_service_url_edit.setText(config.get('endpointurl'))

        uri_edit = self.qml_style_url_edit_events if self.service_type != SERVICE_MANAGER.FDSNSTATION else self.qml_style_url_edit_stations
        uri_edit.setText(config.get('styleurl'))

        combo = self.qml_style_name_combo_events if self.service_type != SERVICE_MANAGER.FDSNSTATION else self.qml_style_name_combo_stations
        if isinstance(config.get('default', {}).get('style'), str):
            combo.setCurrentIndex(
                combo.findData(config.get('default', {}).get('style')))
        elif isinstance(config.get('default', {}).get('style'), dict):
            combo.setCurrentIndex(
                combo.findData(config.get('default', {}).get('style', {}).get('style')))

        self.qml_style_url_edit_mdp.setText(config.get('mdpstyleurl'))
        self.qml_style_name_combo_mdp.setCurrentIndex(
            self.qml_style_name_combo_mdp.findData(config.get('default', {}).get('mdp_style')))

        if config.get('datestart'):
            self.start_date_edit.setDateTime(QDateTime.fromString(config.get('datestart'), Qt.ISODate))
        else:
            self.start_date_edit.clear()

        if config.get('dateend'):
            self.end_date_edit.setDateTime(QDateTime.fromString(config.get('dateend'), Qt.ISODate))
        else:
            self.end_date_edit.clear()

        extent = config.get('boundingbox')
        if extent:
            self.min_lat_spin.setValue(extent[1])
            self.max_lat_spin.setValue(extent[3])
            self.min_long_spin.setValue(extent[0])
            self.max_long_spin.setValue(extent[2])
        else:
            self.min_lat_spin.setValue(-90)
            self.max_lat_spin.setValue(90)
            self.min_long_spin.setValue(-180)
            self.max_long_spin.setValue(180)

        for key, w in self.WIDGET_MAP.items():
            widget = getattr(self, w)
            if isinstance(widget, QCheckBox):
                widget.setChecked(config.get('settings', {}).get(key, False))
            elif isinstance(widget, QSpinBox):
                if key in config.get('settings', {}):
                    widget.setValue(int(config.get('settings', {}).get(key)))

        self.check_http_code_nodata.setChecked('httpcodenodata' in config.get('settings', {}))
        self.combo_http_code_nodata.setCurrentIndex(
            self.combo_http_code_nodata.findData(config.get('settings', {}).get('httpcodenodata', '204')))

        if self.group_ogc_layers.isEnabled():
            self.ogc_layers_edit.setText(json.dumps(config.get('default', {}).get('layers', []), indent=4))

    def get_config(self) -> dict:  # pylint: disable=too-many-branches
        """
        Returns the configuration of the service defined in the widget
        """
        if self.service_id in SERVICE_MANAGER.available_services(self.service_type):
            config = deepcopy(SERVICE_MANAGER.service_details(self.service_type, self.service_id))
        else:
            config = {
                'default': {},
                'settings': {}
            }

        config['title'] = self.title_edit.text()
        config['group'] = self.group_edit.text()
        config['servicedescription'] = self.service_description_edit.text()
        config['servicedescriptionurl'] = self.service_description_url_edit.text()
        config['datadescription'] = self.data_description_edit.text()
        config['datadescriptionurl'] = self.data_description_url_edit.text()
        config[
            'publications'] = [] if not self.publications_text_edit.toPlainText() else self.publications_text_edit.toPlainText().split(
            '\n')
        config['manualurl'] = self.webservice_manual_url_edit.text()
        config['datalicense'] = self.data_license_edit.text()
        config['datalicenseurl'] = self.data_license_url_edit.text()
        config['dataprovider'] = self.data_provider_edit.text()
        config['dataproviderurl'] = self.data_provider_url_edit.text()
        config['endpointurl'] = self.web_service_url_edit.text()

        uri_edit = self.qml_style_url_edit_events if self.service_type != SERVICE_MANAGER.FDSNSTATION else self.qml_style_url_edit_stations
        combo = self.qml_style_name_combo_events if self.service_type != SERVICE_MANAGER.FDSNSTATION else self.qml_style_name_combo_stations
        config['styleurl'] = uri_edit.text()
        config['default']['style'] = combo.currentData()

        config['mdpstyleurl'] = self.qml_style_url_edit_mdp.text()
        config['default']['mdp_style'] = self.qml_style_name_combo_mdp.currentData()

        if self.start_date_edit.dateTime().isValid():
            config['datestart'] = self.start_date_edit.dateTime().toString(Qt.ISODate)
        else:
            config['datestart'] = ''

        if self.end_date_edit.dateTime().isValid():
            config['dateend'] = self.end_date_edit.dateTime().toString(Qt.ISODate)
        else:
            config['dateend'] = ''

        if self.group_bounding_box.isEnabled():
            bounding_box = [self.min_long_spin.value(),
                            self.min_lat_spin.value(),
                            self.max_long_spin.value(),
                            self.max_lat_spin.value()]
            config['boundingbox'] = bounding_box

        if self.group_capabilities.isEnabled():
            settings = {}
            for key, w in self.WIDGET_MAP.items():
                widget = getattr(self, w)
                if not widget.isEnabled():
                    continue

                if isinstance(widget, QCheckBox):
                    settings[key] = widget.isChecked()
                elif isinstance(widget, QSpinBox):
                    settings[key] = widget.value()

            if self.check_http_code_nodata.isChecked():
                settings['httpcodenodata'] = self.combo_http_code_nodata.currentData()

            config['settings'] = settings

        if self.group_ogc_layers.isEnabled():
            config['default']['layers'] = json.loads(self.ogc_layers_edit.text())

        return config

    def save_changes(self):
        """
        Saves the changes made in the widget
        """
        config = self.get_config()
        SERVICE_MANAGER.save_service(self.service_type, self.service_id, config)

    def _load_service(self):
        """
        Attempts to defined the service via WADL
        """
        url = self.web_service_url_edit.text().strip()
        url = WadlServiceParser.find_url(url)

        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        reply = QgsNetworkAccessManager.instance().get(request)

        def response_finished(_reply: QNetworkReply):
            """
            Triggered when the response is finished
            """
            self.button_load_service.setEnabled(True)
            self.button_load_service.setText(self.tr('Load Web Service Capabilities'))

            content = _reply.readAll()
            try:
                self._set_state_from_wadl(WadlServiceParser.parse_wadl(content, self.service_type, url))
            except AssertionError:
                self.message_bar.pushMessage('', self.tr('Could not load web service capabilities from {}'.format(url)),
                                             Qgis.Critical, 0)

        self.button_load_service.setEnabled(False)
        self.button_load_service.setText(self.tr('Loading'))
        reply.finished.connect(partial(response_finished, reply))

    def _set_state_from_wadl(self, config: Dict):
        """
        Sets the widget state from a WADL configuration
        """
        self.web_service_url_edit.setText(config.get('endpointurl'))

        extent = config.get('boundingbox')
        if extent:
            self.min_lat_spin.setValue(extent[1])
            self.max_lat_spin.setValue(extent[3])
            self.min_long_spin.setValue(extent[0])
            self.max_long_spin.setValue(extent[2])

        for setting in config.get('settings', {}):
            widget = getattr(self, self.WIDGET_MAP.get(setting))
            if not isinstance(widget, QCheckBox):
                continue

            widget.setChecked(config['settings'][setting])


class ServiceConfigurationDialog(QDialog):
    """
    A dialog for configuring a service
    """

    def __init__(self, iface, service_type: str, service_id: str, parent: Optional[QWidget]):
        super().__init__(parent)
        self.setObjectName('ServiceConfigurationDialog')

        QgsGui.enableAutoGeometryRestore(self)

        self.setWindowTitle(self.tr('Edit Service {}').format(service_id))

        self.config_widget = ServiceConfigurationWidget(iface, service_type, service_id)
        layout = QVBoxLayout()
        layout.addWidget(self.config_widget, 1)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        self.config_widget.validChanged.connect(self.valid_changed)
        self.valid_changed(self.config_widget.is_valid()[0])

    def valid_changed(self, is_valid: bool):
        """
        Triggered when the widget valid state is changed
        """
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(is_valid)

    def accept(self):  # pylint: disable=missing-function-docstring
        self.config_widget.save_changes()
        super().accept()
