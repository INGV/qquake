# -*- coding: utf-8 -*-
"""
A widget for configuring output layer options
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

from functools import partial
from typing import Dict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsSettings

from qquake.fetcher import Fetcher
from qquake.gui.gui_utils import GuiUtils
from qquake.gui.output_table_options_dialog import OutputTableOptionsDialog
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('table_options_widget_base.ui'))


class OutputTableOptionsWidget(QWidget, FORM_CLASS):
    """
    A widget for configuring output layer options
    """

    changed = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.output_fields = None
        self.service_type = None
        self.service_id = None
        self.allow_basic_output = True

        self.radio_basic_output.toggled.connect(self.changed)
        self.radio_extended_output.toggled.connect(self.changed)

        self.radio_basic_output.toggled.connect(self._enable_widgets)
        self.radio_extended_output.toggled.connect(self._enable_widgets)

        self.output_table_options_button.clicked.connect(self._output_table_options)

        self.block_style_changes = False

        self.update_style_combos()

    def update_style_combos(self):
        """
        Refreshes the entries in style combo boxes
        """

        def _populate_style_combo(combo, service_type: str):
            """
            Populates a style combo with matching styles of the specified type
            """
            prev_entry = combo.currentText()
            combo.clear()
            styles = SERVICE_MANAGER.styles_for_service_type(service_type)
            for s in styles:
                combo.addItem(SERVICE_MANAGER.get_style(s)['label'], s)

            prev_index = combo.findData(prev_entry)
            if prev_index >= 0:
                combo.setCurrentIndex(prev_index)
            else:
                combo.setCurrentIndex(0)

        self.block_style_changes = True

        _populate_style_combo(self.combo_style_epicentres, SERVICE_MANAGER.FDSNEVENT)
        _populate_style_combo(self.combo_style_macro, SERVICE_MANAGER.MACROSEISMIC)
        _populate_style_combo(self.combo_style_stations, SERVICE_MANAGER.FDSNSTATION)

        self.block_style_changes = False

        self.combo_style_epicentres.currentIndexChanged.connect(
            partial(self._style_changed, self.combo_style_epicentres))
        self.combo_style_macro.currentIndexChanged.connect(
            partial(self._style_changed, self.combo_style_macro))
        self.combo_style_stations.currentIndexChanged.connect(
            partial(self._style_changed, self.combo_style_stations))

    def _style_changed(self, combo):
        """
        Called when a style combo box entry is changed
        """
        if self.block_style_changes:
            return

        s = QgsSettings()
        if combo == self.combo_style_epicentres:
            s.setValue('/plugins/qquake/last_event_style_{}_{}'.format(self.service_type, self.service_id),
                       self.combo_style_epicentres.currentData())
        if combo == self.combo_style_macro:
            s.setValue('/plugins/qquake/last_mdp_style_{}_{}'.format(self.service_type, self.service_id),
                       self.combo_style_macro.currentData())
        if combo == self.combo_style_stations:
            s.setValue('/plugins/qquake/last_station_style_{}_{}'.format(self.service_type, self.service_id),
                       self.combo_style_stations.currentData())

    def restore_settings(self, prefix: str, suffix: str):
        """
        Restores widget state from settings
        """
        s = QgsSettings()

        if self.service_id:
            service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)
        else:
            service_config = None

        if not service_config or service_config['settings'].get('outputtext', False):
            if self.allow_basic_output:
                self.radio_basic_output.setChecked(
                    s.value('/plugins/qquake/{}_{}_event_basic_checked'.format(prefix, suffix), True, bool))
            else:
                self.radio_extended_output.setChecked(True)

        if not service_config or service_config['settings'].get('outputxml', False):
            self.radio_extended_output.setChecked(
                s.value('/plugins/qquake/{}_{}_event_extended_checked'.format(prefix, suffix), False, bool))

    def save_settings(self, prefix: str, suffix: str):
        """
        Saves widget state to settings
        """
        s = QgsSettings()

        s.setValue('/plugins/qquake/{}_{}_event_basic_checked'.format(prefix, suffix),
                   self.radio_basic_output.isChecked())
        s.setValue('/plugins/qquake/{}_{}_event_extended_checked'.format(prefix, suffix),
                   self.radio_extended_output.isChecked())

    def enable_basic_option(self, enabled: bool):
        """
        Enables the basic output option
        """
        self.allow_basic_output = enabled
        self.radio_basic_output.setEnabled(self.allow_basic_output)
        if not self.allow_basic_output and self.radio_basic_output.isChecked():
            self.radio_extended_output.setChecked(True)

    def set_service_type(self, service_type: str):
        """
        Sets the associated service type
        """
        self.service_type = service_type

        self.label_style_epicentres.setVisible(
            self.service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))
        self.combo_style_epicentres.setVisible(
            self.service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC))

        self.label_style_macro.setVisible(self.service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.combo_style_macro.setVisible(self.service_type == SERVICE_MANAGER.MACROSEISMIC)

        self.label_style_stations.setVisible(self.service_type == SERVICE_MANAGER.FDSNSTATION)
        self.combo_style_stations.setVisible(self.service_type == SERVICE_MANAGER.FDSNSTATION)

    def set_service_id(self, service_id: str):  # pylint:disable=too-many-branches
        """
        Sets the associated service ID
        """
        self.service_id = service_id

        service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

        if 'fields' in service_config['default']:
            self.output_fields = service_config['default']['fields']

        if not service_config['settings'].get('outputtext', False):
            if self.radio_basic_output.isChecked():
                self.radio_extended_output.setChecked(True)
            self.radio_basic_output.setEnabled(False)
        else:
            self.radio_basic_output.setEnabled(self.allow_basic_output)

        if not service_config['settings'].get('outputxml', False):
            if self.radio_extended_output.isChecked():
                self.radio_basic_output.setChecked(True)
            self.radio_extended_output.setEnabled(False)
        else:
            self.radio_extended_output.setEnabled(True)

        self.block_style_changes = True

        s = QgsSettings()
        prev_event_style = s.value('/plugins/qquake/last_event_style_{}_{}'.format(self.service_type, self.service_id),
                                   '', str)
        prev_mdp_style = s.value('/plugins/qquake/last_mdp_style_{}_{}'.format(self.service_type, self.service_id),
                                 '', str)
        prev_station_style = s.value(
            '/plugins/qquake/last_station_style_{}_{}'.format(self.service_type, self.service_id),
            '', str)

        default_style_index = self.combo_style_macro.findText(prev_mdp_style)
        if prev_mdp_style and default_style_index >= 0:
            self.combo_style_macro.setCurrentIndex(default_style_index)
        elif isinstance(service_config['default'].get('style'), dict) and 'mdp' in service_config['default']['style']:
            default_style_index = self.combo_style_macro.findText(
                service_config['default']['style']['mdp'].get('style', ''))
            if default_style_index >= 0:
                self.combo_style_macro.setCurrentIndex(default_style_index)

        default_style_index = self.combo_style_epicentres.findText(prev_event_style)
        if prev_event_style and default_style_index >= 0:
            self.combo_style_epicentres.setCurrentIndex(default_style_index)
        elif isinstance(service_config['default']['style'], dict) and 'events' in service_config['default']['style']:
            default_style_index = self.combo_style_epicentres.findText(
                service_config['default']['style']['events'].get('style', ''))
            if default_style_index >= 0:
                self.combo_style_epicentres.setCurrentIndex(default_style_index)

        default_style_index = self.combo_style_stations.findText(prev_station_style)
        if prev_station_style and default_style_index >= 0:
            self.combo_style_stations.setCurrentIndex(default_style_index)
        elif isinstance(service_config['default']['style'], dict) and 'stations' in service_config['default']['style']:
            default_style_index = self.combo_style_stations.findText(
                service_config['default']['style']['stations'].get('style', ''))
            if default_style_index >= 0:
                self.combo_style_stations.setCurrentIndex(default_style_index)

        self.block_style_changes = False

    def _enable_widgets(self):
        """
        Selectively enables widgets based on overall state
        """
        self.output_table_options_button.setEnabled(self.radio_extended_output.isChecked())

    def _output_table_options(self):
        """
        Triggers the output table options dialog
        """
        dlg = OutputTableOptionsDialog(self.service_type, self.service_id, self.output_fields, self)
        if dlg.exec_():
            self.output_fields = dlg.selected_fields()
            self.changed.emit()

    def output_type(self) -> str:
        """
        Returns the output table type
        """
        return Fetcher.BASIC if self.radio_basic_output.isChecked() else Fetcher.EXTENDED

    def selected_styles(self) -> Dict[str, str]:
        """
        Returns a dictionary of the selected styles for the results
        """
        res = {}

        if self.service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC):
            res[SERVICE_MANAGER.FDSNEVENT] = self.combo_style_epicentres.currentData()

        if self.service_type == SERVICE_MANAGER.MACROSEISMIC:
            res[SERVICE_MANAGER.MACROSEISMIC] = self.combo_style_macro.currentData()

        if self.service_type == SERVICE_MANAGER.FDSNSTATION:
            res[SERVICE_MANAGER.FDSNSTATION] = self.combo_style_stations.currentData()

        return res
