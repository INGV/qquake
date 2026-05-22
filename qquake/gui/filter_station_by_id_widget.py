# -*- coding: utf-8 -*-
"""
A widget for filtering stations by ID
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

from typing import Optional, List, Dict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, QUrl, QSignalBlocker
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtWidgets import QWidget, QComboBox
from qgis.core import (
    QgsSettings,
    QgsUnitTypes,
    QgsNetworkAccessManager,
)

from qquake.gui.gui_utils import GuiUtils
from qquake.gui.base_filter_widget import BaseFilterWidget
from qquake.services import SERVICE_MANAGER
from qquake.qt_compat import (
    QGS_DISTANCE_KILOMETERS,
    QT_COMBOBOX_NO_INSERT,
    set_request_follow_redirects,
)

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('filter_station_by_id_widget_base.ui'))


class FilterStationByIdWidget(QWidget, FORM_CLASS, BaseFilterWidget):
    """
    A widget for filtering stations by ID
    """
    changed = pyqtSignal()

    def __init__(self, iface, service_type, parent=None):  # pylint: disable=unused-argument
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)
        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 0)

        self.output_table_options_widget.changed.connect(self._enable_widgets)

        self.service_type = None
        self.service_id = None
        self.service_config = {}
        self._pending_network_request_service_id = None
        self._pending_station_request = None

        self.edit_network_code.setEditable(True)
        self.edit_network_code.setInsertPolicy(QT_COMBOBOX_NO_INSERT)
        self.edit_station_code.setEditable(True)
        self.edit_station_code.setInsertPolicy(QT_COMBOBOX_NO_INSERT)

        if self.edit_network_code.lineEdit():
            self.edit_network_code.lineEdit().editingFinished.connect(self._network_editing_finished)
        if self.edit_station_code.lineEdit():
            self.edit_station_code.lineEdit().editingFinished.connect(self.changed)

        self.edit_network_code.currentTextChanged.connect(self._network_text_changed)
        self.edit_station_code.currentTextChanged.connect(self.changed)
        self.edit_location_code.textChanged.connect(self.changed)
        self.output_table_options_widget.changed.connect(self.changed)

        self.edit_network_code.currentIndexChanged.connect(self._network_selection_changed)
        self.button_refresh_networks.clicked.connect(self._refresh_networks)

        self._enable_widgets()
        self.set_service_type(service_type)

    def is_valid(self) -> bool:
        return bool(self.network_codes() or self.station_codes() or self.edit_location_code.text().strip())

    def set_service_type(self, service_type: str):
        self.service_type = service_type
        self.output_table_options_widget.set_service_type(service_type)

    def set_service_id(self, service_id: str):
        service_changed = service_id != self.service_id
        self.service_id = service_id
        self.output_table_options_widget.set_service_id(service_id)
        self.service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)
        self.button_refresh_networks.setEnabled(bool(self.service_id))

        if service_changed:
            with QSignalBlocker(self.edit_network_code):
                self.edit_network_code.setCurrentText('')
            self._clear_stations()

        cached_networks = SERVICE_MANAGER.get_station_networks(self.service_type, self.service_id)
        current_network_text = '' if service_changed else self.edit_network_code.currentText()
        if cached_networks:
            self._populate_networks(cached_networks, preserve_text=current_network_text)
        else:
            self._populate_networks([], preserve_text=current_network_text)
            self._refresh_networks()

        self.changed.emit()

    def restore_settings(self, prefix: str):
        s = QgsSettings()
        self.edit_network_code.setCurrentText(s.value('/plugins/qquake/{}_network_code'.format(prefix), '', str))
        self.edit_station_code.setCurrentText(s.value('/plugins/qquake/{}_station_code'.format(prefix), '', str))
        self.edit_location_code.setText(s.value('/plugins/qquake/{}_location_code'.format(prefix), '', str))

        self.output_table_options_widget.restore_settings(prefix, 'single')
        self._handle_network_text_changed(emit_changed=False)

    def save_settings(self, prefix: str):
        s = QgsSettings()
        s.setValue('/plugins/qquake/{}_network_code'.format(prefix), self.network_codes() or '')
        s.setValue('/plugins/qquake/{}_station_code'.format(prefix), self.station_codes() or '')
        s.setValue('/plugins/qquake/{}_location_code'.format(prefix), self.edit_location_code.text())

        self.output_table_options_widget.save_settings(prefix, 'single')

    def _enable_widgets(self):
        """
        Selectively enables widgets
        """
        self.edit_network_code.setEnabled(True)
        self.button_refresh_networks.setEnabled(bool(self.service_id))
        self.edit_station_code.setEnabled(self._station_code_enabled())

    def _station_code_enabled(self) -> bool:
        network_codes = self.network_codes()
        return bool(network_codes) and ',' not in network_codes

    def _handle_network_text_changed(self, emit_changed: bool = True):
        if not self._station_code_enabled():
            self._clear_stations()
        else:
            self._enable_widgets()

        if emit_changed:
            self.changed.emit()

    def _network_text_changed(self, text: str):  # pylint: disable=unused-argument
        self._handle_network_text_changed()

    @staticmethod
    def _combo_selected_code(combo: QComboBox) -> Optional[str]:
        text = combo.currentText().strip()
        if not text:
            return None

        index = combo.currentIndex()
        if index >= 0:
            item_text = combo.itemText(index).strip()
            item_code = combo.itemData(index)
            if item_code and text == item_text:
                return str(item_code).strip()

        if ',' not in text and ' - ' in text:
            text = text.split(' - ', 1)[0].strip()

        return text.replace(' ', '') or None

    @staticmethod
    def _compose_endpoint_url(base_url: str, extra_query: str) -> str:
        if not base_url:
            return ''
        separator = ''
        if not base_url.endswith('?') and not base_url.endswith('&'):
            separator = '&' if '?' in base_url else '?'
        return '{}{}{}'.format(base_url, separator, extra_query)

    @staticmethod
    def _parse_text_rows(content: str) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        if not content:
            return rows

        header = None
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if header is None:
                header = [part.lstrip('#').strip() for part in line.split('|')]
                continue

            parts = [part.strip() for part in line.split('|')]
            if not any(parts):
                continue

            if len(parts) < len(header):
                parts.extend([''] * (len(header) - len(parts)))
            rows.append(dict(zip(header, parts)))

        return rows

    def _populate_networks(self, networks: List[Dict[str, str]], preserve_text: Optional[str] = None):
        current_text = preserve_text if preserve_text is not None else self.edit_network_code.currentText()
        with QSignalBlocker(self.edit_network_code):
            self.edit_network_code.clear()
            for network in networks:
                code = network.get('code', '').strip()
                if not code:
                    continue
                description = network.get('description', '').strip()
                label = '{} - {}'.format(code, description) if description else code
                self.edit_network_code.addItem(label, code)
            self.edit_network_code.setCurrentText(current_text or '')

        if not current_text or not self._station_code_enabled():
            self._clear_stations()
        else:
            self._enable_widgets()

    def _clear_stations(self):
        with QSignalBlocker(self.edit_station_code):
            self.edit_station_code.clear()
        self._enable_widgets()

    def _populate_stations(self, stations: List[Dict[str, str]], preserve_text: Optional[str] = None):
        current_text = preserve_text if preserve_text is not None else self.edit_station_code.currentText()
        with QSignalBlocker(self.edit_station_code):
            self.edit_station_code.clear()
            for station in stations:
                code = station.get('code', '').strip()
                if not code:
                    continue
                site_name = station.get('site_name', '').strip()
                label = '{} - {}'.format(code, site_name) if site_name else code
                self.edit_station_code.addItem(label, code)
            self.edit_station_code.setCurrentText(current_text or '')

        self._enable_widgets()

    def _refresh_networks(self):
        if not self.service_id:
            return

        self._pending_network_request_service_id = self.service_id
        self.button_refresh_networks.setEnabled(False)

        url = self._compose_endpoint_url(
            self.service_config.get('endpointurl', ''),
            'level=network&format=text')
        if not url:
            self.button_refresh_networks.setEnabled(True)
            return

        request = QNetworkRequest(QUrl(url))
        set_request_follow_redirects(request)
        reply = QgsNetworkAccessManager.instance().get(request)
        reply.finished.connect(lambda r=reply, sid=self.service_id: self._network_reply_finished(r, sid))

    def _network_reply_finished(self, reply: QNetworkReply, requested_service_id: str):
        self.button_refresh_networks.setEnabled(bool(self.service_id))

        try:
            if requested_service_id != self.service_id:
                return

            content = bytes(reply.readAll()).decode('utf-8', errors='replace')
            rows = self._parse_text_rows(content)
            networks = []
            for row in rows:
                code = (row.get('Network') or row.get('network') or '').strip()
                if not code:
                    continue
                description = (row.get('Description') or row.get('description') or '').strip()
                networks.append({
                    'code': code,
                    'description': description,
                })

            SERVICE_MANAGER.set_station_networks(self.service_type, self.service_id, networks)
            self._populate_networks(networks)
        finally:
            reply.deleteLater()
            self.changed.emit()

    def _refresh_stations_for_current_network(self):
        network_code = self.network_codes()
        self._clear_stations()
        self.changed.emit()
        if not self.service_id or not network_code:
            return
        if ',' in network_code or '*' in network_code or '?' in network_code:
            return

        self._pending_station_request = (self.service_id, network_code)
        url = self._compose_endpoint_url(
            self.service_config.get('endpointurl', ''),
            'network={}&level=station&format=text'.format(network_code))
        if not url:
            return

        request = QNetworkRequest(QUrl(url))
        set_request_follow_redirects(request)
        reply = QgsNetworkAccessManager.instance().get(request)
        reply.finished.connect(
            lambda r=reply, sid=self.service_id, ncode=network_code: self._station_reply_finished(r, sid, ncode))

    def _station_reply_finished(self, reply: QNetworkReply, requested_service_id: str, requested_network: str):
        try:
            if requested_service_id != self.service_id:
                return
            if requested_network != (self.network_codes() or ''):
                return

            content = bytes(reply.readAll()).decode('utf-8', errors='replace')
            rows = self._parse_text_rows(content)
            stations = []
            for row in rows:
                code = (row.get('Station') or row.get('station') or '').strip()
                if not code:
                    continue
                site_name = (row.get('SiteName') or row.get('Sitename') or row.get('site_name') or '').strip()
                stations.append({
                    'code': code,
                    'site_name': site_name,
                })
            self._populate_stations(stations)
        finally:
            reply.deleteLater()
            self.changed.emit()

    def _network_selection_changed(self, index: int):
        if index < 0:
            return
        self._refresh_stations_for_current_network()

    def _network_editing_finished(self):
        self._refresh_stations_for_current_network()
        self.changed.emit()

    def network_codes(self) -> Optional[str]:
        """
        Returns the entered network codes
        """
        return self._combo_selected_code(self.edit_network_code)

    def station_codes(self) -> Optional[str]:
        """
        Returns the entered station codes
        """
        if not self.edit_station_code.isEnabled():
            return None
        return self._combo_selected_code(self.edit_station_code)

    def locations(self) -> Optional[str]:
        """
        Returns the entered location codes
        """
        return self.edit_location_code.text().strip().replace(" ", "") or None

    def output_fields(self) -> Optional[List[str]]:
        return self.output_table_options_widget.output_fields

    def selected_styles(self) -> Dict[str, str]:
        return self.output_table_options_widget.selected_styles()

    def output_type(self) -> str:
        return self.output_table_options_widget.output_type()

    def convert_negative_depths(self) -> bool:
        return False

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        return QGS_DISTANCE_KILOMETERS
