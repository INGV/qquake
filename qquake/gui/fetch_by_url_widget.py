# -*- coding: utf-8 -*-
"""
Fetch results by URL widget
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
from qgis.PyQt.QtCore import (
    pyqtSignal,
    QDir,
    QUrl
)
from qgis.PyQt.QtGui import QFontMetrics
from qgis.PyQt.QtWidgets import (
    QWidget,
    QFileDialog
)
from qgis.core import (
    QgsUnitTypes
)

from qquake.gui.base_filter_widget import BaseFilterWidget
from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('fetch_by_url_widget.ui'))


class FetchByUrlWidget(QWidget, FORM_CLASS, BaseFilterWidget):
    """
    Fetch results by URL widget
    """
    changed = pyqtSignal()

    def __init__(self, iface,  # pylint: disable=unused-argument
                 service_type: str, parent=None):
        """Constructor."""
        QWidget.__init__(self, parent)

        self.setupUi(self)

        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollArea > QWidget > QScrollBar { background: 1; }
        """)

        fm = QFontMetrics(self.url_edit.font())
        self.url_edit.setMaximumHeight(fm.lineSpacing() * 6)

        self.import_file_button.clicked.connect(self._import_from_file)

        if service_type == SERVICE_MANAGER.FDSNSTATION:
            self.label_import_file.setText(self.tr('Or import a local StationXML file'))

        self.service_type = None
        self.service_id = None
        self.set_service_type(service_type)
        self.service_config = {}

        self.url_edit.textChanged.connect(self.changed)

        self.output_table_options_widget.enable_basic_option(False)

    def is_valid(self) -> bool:
        return bool(self.url_edit.toPlainText())

    def set_service_type(self, service_type: str):
        self.service_type = service_type

        self.output_table_options_widget.set_service_type(service_type)

    def set_service_id(self, service_id: str):
        self.service_id = service_id

        self.output_table_options_widget.set_service_id(service_id)

        self.service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

    def restore_settings(self, prefix: str):
        self.output_table_options_widget.restore_settings(prefix, 'single')

    def save_settings(self, prefix: str):
        self.output_table_options_widget.save_settings(prefix, 'single')

    def _import_from_file(self):
        """
        Triggers importing QuakeML file
        """
        file, _ = QFileDialog.getOpenFileName(self, self.tr('Import QuakeML File'), QDir.homePath(), self.tr(
            'Supported Files (*.xml *.XML *.qml *.QML);;XML Files (*.xml *.XML);;QuakeML Files (*.qml *.QML);;All Files (*.*)'))
        if file:
            self.url_edit.setPlainText(QUrl.fromLocalFile(file).toString())

    def output_type(self) -> str:
        return self.output_table_options_widget.output_type()

    def output_fields(self) -> Optional[List[str]]:
        return self.output_table_options_widget.output_fields

    def convert_negative_depths(self) -> bool:
        return self.output_options_widget.convert_negative_depths()

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        return self.output_options_widget.depth_unit()

    def url(self) -> str:
        """
        Returns the current URL
        """
        return self.url_edit.toPlainText().strip()

    def selected_styles(self) -> Dict[str, str]:
        return self.output_table_options_widget.selected_styles()
