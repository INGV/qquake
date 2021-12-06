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
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import (
    QgsSettings,
    QgsUnitTypes
)

from qquake.gui.gui_utils import GuiUtils
from qquake.gui.base_filter_widget import BaseFilterWidget

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

        self.output_table_options_widget.changed.connect(self._enable_widgets)

        self._enable_widgets()

        self.service_type = None
        self.service_id = None
        self.set_service_type(service_type)

        self.edit_network_code.textChanged.connect(self.changed)
        self.edit_station_code.textChanged.connect(self.changed)
        self.edit_location_code.textChanged.connect(self.changed)
        self.output_table_options_widget.changed.connect(self.changed)

    def is_valid(self) -> bool:
        return bool(self.edit_network_code.text() or self.edit_station_code.text() or self.edit_location_code.text())

    def set_service_type(self, service_type: str):
        self.service_type = service_type

        self.output_table_options_widget.set_service_type(service_type)

    def set_service_id(self, service_id: str):
        self.service_id = service_id

        self.output_table_options_widget.set_service_id(service_id)

    def restore_settings(self, prefix: str):
        s = QgsSettings()
        self.edit_network_code.setText(s.value('/plugins/qquake/{}_network_code'.format(prefix), '', str))
        self.edit_station_code.setText(s.value('/plugins/qquake/{}_station_code'.format(prefix), '', str))
        self.edit_location_code.setText(s.value('/plugins/qquake/{}_location_code'.format(prefix), '', str))

        self.output_table_options_widget.restore_settings(prefix, 'single')

    def save_settings(self, prefix: str):
        s = QgsSettings()
        s.setValue('/plugins/qquake/{}_network_code'.format(prefix), self.edit_network_code.text())
        s.setValue('/plugins/qquake/{}_station_code'.format(prefix), self.edit_station_code.text())
        s.setValue('/plugins/qquake/{}_location_code'.format(prefix), self.edit_location_code.text())

        self.output_table_options_widget.save_settings(prefix, 'single')

    def _enable_widgets(self):
        """
        Selectively enables widgets
        """

    def network_codes(self) -> Optional[str]:
        """
        Returns the entered network codes
        """
        return self.edit_network_code.text().strip() or None

    def station_codes(self) -> Optional[str]:
        """
        Returns the entered station codes
        """
        return self.edit_station_code.text().strip() or None

    def locations(self) -> Optional[str]:
        """
        Returns the entered location codes
        """
        return self.edit_location_code.text().strip() or None

    def output_fields(self) -> Optional[List[str]]:
        return self.output_table_options_widget.output_fields

    def selected_styles(self) -> Dict[str, str]:
        return self.output_table_options_widget.selected_styles()

    def output_type(self) -> str:
        return self.output_table_options_widget.output_type()

    def convert_negative_depths(self) -> bool:
        return False

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        return QgsUnitTypes.DistanceKilometers
