# -*- coding: utf-8 -*-
"""
A widget for filtering results by ID
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

import re
from typing import List, Optional, Dict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QDir,
    QUrl,
    pyqtSignal
)
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtWidgets import QWidget, QFileDialog
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsSettings,
    QgsNetworkAccessManager,
    QgsUnitTypes
)

from qquake.gui.base_filter_widget import BaseFilterWidget
from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('filter_by_id_widget_base.ui'))


class FilterByIdWidget(QWidget, FORM_CLASS, BaseFilterWidget):
    """
    A widget for filtering results by ID
    """
    changed = pyqtSignal()

    def __init__(self, iface, service_type: str, parent: Optional[QWidget] = None):  # pylint: disable=unused-argument
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollArea > QWidget > QScrollBar { background: 1; }
        """)

        self.radio_single_event.toggled.connect(self._enable_widgets)
        self.radio_multiple_events.toggled.connect(self._enable_widgets)
        self.output_table_options_widget.changed.connect(self._enable_widgets)
        self.radio_contributor.toggled.connect(self._enable_widgets)

        self.button_refresh_contributors.clicked.connect(self._refresh_contributors)

        self._enable_widgets()

        self.service_type = None
        self.service_id = None
        self.set_service_type(service_type)
        self.service_config = {}

        self.radio_single_event.toggled.connect(self.changed)
        self.edit_event_id.textChanged.connect(self.changed)
        self.event_ids_edit.textChanged.connect(self.changed)
        self.output_table_options_widget.changed.connect(self.changed)
        self.radio_contributor.toggled.connect(self.changed)
        self.edit_contributor_id.currentTextChanged.connect(self.changed)
        self.button_import_from_file.clicked.connect(self.load_from_file)

    def is_valid(self) -> bool:
        if self.radio_single_event.isChecked():
            res = bool(self.edit_event_id.text())
        elif self.radio_multiple_events.isChecked():
            res = bool(self.event_ids_edit.toPlainText())
        elif self.radio_contributor.isChecked():
            res = bool(self.edit_contributor_id.currentText())
        else:
            res = False
        return res

    def set_service_type(self, service_type: str):
        self.service_type = service_type

        self.output_table_options_widget.set_service_type(service_type)

    def set_service_id(self, service_id: str):
        self.service_id = service_id

        self.output_table_options_widget.set_service_id(service_id)

        self.service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

        if not self.service_config['settings'].get('querycontributorid'):
            if self.radio_contributor.isChecked():
                self.radio_single_event.setChecked(True)
            self.radio_contributor.setEnabled(False)
        else:
            self.radio_contributor.setEnabled(True)

        if self.radio_contributor.isChecked() and self.service_config['settings'].get('querycontributor'):
            self.button_refresh_contributors.setEnabled(True)
        else:
            self.button_refresh_contributors.setEnabled(False)

        self._update_contributor_list(SERVICE_MANAGER.get_contributors(self.service_type, self.service_id))

    def restore_settings(self, prefix: str):
        s = QgsSettings()

        self.edit_event_id.setText(s.value('/plugins/qquake/{}_single_event_id'.format(prefix), '', str))
        self.edit_contributor_id.setCurrentText(s.value('/plugins/qquake/{}_contributor_id'.format(prefix), '', str))
        if s.value('/plugins/qquake/{}_single_event_checked'.format(prefix), True, bool):
            self.radio_single_event.setChecked(True)
        if s.value('/plugins/qquake/{}_multi_event_checked'.format(prefix), True, bool):
            self.radio_multiple_events.setChecked(True)
        if s.value('/plugins/qquake/{}_contributor_checked'.format(prefix), True, bool):
            if self.radio_contributor.isEnabled():
                self.radio_contributor.setChecked(True)
            else:
                self.radio_single_event.setChecked(True)

        self.output_table_options_widget.restore_settings(prefix, 'single')

    def save_settings(self, prefix: str):
        s = QgsSettings()
        s.setValue('/plugins/qquake/{}_single_event_id'.format(prefix), self.edit_event_id.text())
        s.setValue('/plugins/qquake/{}_single_event_checked'.format(prefix), self.radio_single_event.isChecked())
        s.setValue('/plugins/qquake/{}_multi_event_checked'.format(prefix), self.radio_multiple_events.isChecked())
        s.setValue('/plugins/qquake/{}_contributor_checked'.format(prefix), self.radio_contributor.isChecked())
        s.setValue('/plugins/qquake/{}_contributor_id'.format(prefix), self.edit_contributor_id.currentText())

        self.output_table_options_widget.save_settings(prefix, 'single')

    def _enable_widgets(self):
        """
        Selectively enables widgets based on dialog state
        """
        for w in [self.label_event_id,
                  self.edit_event_id]:
            w.setEnabled(self.radio_single_event.isChecked())

        for w in [self.multi_event_widget]:
            w.setEnabled(self.radio_multiple_events.isChecked())

        for w in [self.edit_contributor_id, self.label_contributor_id]:
            w.setEnabled(self.radio_contributor.isChecked())

        if self.radio_contributor.isChecked() and self.service_config['settings'].get('querycontributor'):
            self.button_refresh_contributors.setEnabled(True)
        else:
            self.button_refresh_contributors.setEnabled(False)

    def contributor_id(self) -> Optional[str]:
        """
        Returns the selected contributor ID
        """
        return self.edit_contributor_id.currentText() if self.radio_contributor.isChecked() else None

    def ids(self) -> Optional[List[str]]:
        """
        Returns a list of target IDs
        """
        if self.radio_multiple_events.isChecked():
            id_text = self.event_ids_edit.toPlainText()
            res = self.parse_multi_input(id_text)
        elif self.radio_contributor.isChecked():
            res = None
        else:
            res = [self.edit_event_id.text()]
        return res

    @staticmethod
    def parse_multi_input(text: str) -> List[str]:
        """
        Parses a multicomponent input string to component parts
        """
        return [part.strip() for part in re.split(r'[,\n]', text) if part.strip()]

    def load_from_file(self):
        """
        Triggers loading event IDs from a text file
        """
        file, _ = QFileDialog.getOpenFileName(self, self.tr('Import Event IDs from File'), QDir.homePath(),
                                              'Text Files (*.*)')
        if not file:
            return

        with open(file, 'rt', encoding='utf8') as f:
            text = '\n'.join(f.readlines())
            self.event_ids_edit.setPlainText('\n'.join(self.parse_multi_input(text)))

    def output_type(self) -> str:
        return self.output_table_options_widget.output_type()

    def output_fields(self) -> Optional[List[str]]:
        return self.output_table_options_widget.output_fields

    def convert_negative_depths(self) -> bool:
        return self.output_options_widget.convert_negative_depths()

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        return self.output_options_widget.depth_unit()

    def selected_styles(self) -> Dict[str, str]:
        return self.output_table_options_widget.selected_styles()

    def _refresh_contributors(self):
        """
        Refreshes the list of contributors from the service
        """
        self.edit_contributor_id.clear()
        url = SERVICE_MANAGER.get_contributor_endpoint(self.service_type, self.service_id)
        if not url:
            return

        self.button_refresh_contributors.setEnabled(False)
        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))

    def _reply_finished(self, reply: QNetworkReply):
        """
        Triggered when a reply is finished
        """
        self.button_refresh_contributors.setEnabled(True)

        content = reply.readAll()
        if not content:
            return

        doc = QDomDocument()
        doc.setContent(content)
        contributor_elements = doc.elementsByTagName('Contributor')

        contributors = []
        for e in range(contributor_elements.length()):
            contributor_element = contributor_elements.at(e).toElement()
            contributors.append(contributor_element.text())

        SERVICE_MANAGER.set_contributors(self.service_type, self.service_id, contributors)
        self._update_contributor_list(contributors)

    def _update_contributor_list(self, contributors: List[str]):
        """
        Updates the contributors list
        """
        self.edit_contributor_id.clear()
        for c in contributors:
            self.edit_contributor_id.addItem(c)
