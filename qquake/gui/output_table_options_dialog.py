# -*- coding: utf-8 -*-
"""
A dialog for configuring output table options
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

from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QModelIndex,
    Qt
)
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsSettings
from qgis.gui import QgsGui

from qquake.gui.gui_utils import GuiUtils
from qquake.gui.simple_node_model import SimpleNodeModel, ModelNode
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('output_table_options.ui'))


class OutputTableOptionsDialog(QDialog, FORM_CLASS):
    """
    A dialog for configuring output table options
    """

    def __init__(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                 service_type: str,
                 service_id: str,
                 initial_fields: List[str],
                 parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self.service_type = service_type
        self.service_id = service_id

        service_config = SERVICE_MANAGER.service_details(service_type, service_id)

        self.setWindowTitle(self.tr('Output Table Options'))

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        QgsGui.enableAutoGeometryRestore(self)
        self.default_fields = None

        s = QgsSettings()

        short_field_names = s.value('/plugins/qquake/output_short_field_names', True, bool)
        if short_field_names:
            self.radio_short_fields.setChecked(True)
        else:
            self.radio_long_fields.setChecked(True)

        self.radio_short_fields.toggled.connect(self.change_field_names)

        nodes = []
        for _, settings in SERVICE_MANAGER.get_field_config(self.service_type)['field_groups'].items():
            if self.service_type != SERVICE_MANAGER.FDSNSTATION and settings['label'] == 'station':
                continue
            if self.service_type == SERVICE_MANAGER.FDSNSTATION and settings['label'] not in ('station', 'general', 'network'):
                continue

            parent_node = ModelNode([settings['label']])
            for f in settings['fields']:
                if f.get('skip'):
                    continue

                if f['source'] is not None:
                    if f['source'].startswith('eventParameters'):
                        path = f['source'][len('eventParameters>event>'):]
                    elif f['source'].startswith('macroseismicParameters'):
                        path = f['source'][len('macroseismicParameters>'):]
                    else:
                        path = f['source'][len('FDSNStationXML>'):]
                else:
                    path = ''

                if initial_fields:
                    checked = f['source'] in initial_fields
                else:
                    checked = s.value('/plugins/qquake/output_field_{}'.format(path.replace('>', '_')), True, bool)

                parent_node.addChild(
                    ModelNode(['checked', f['field_short' if short_field_names else 'field_long'], path], checked,
                              user_data=f))
            nodes.append(parent_node)

        self.field_model = SimpleNodeModel(nodes, headers=[self.tr('Include'), self.tr('Field Name'),
                                                           self.tr(
                                                               'StationML Source') if service_type == SERVICE_MANAGER.FDSNSTATION else self.tr(
                                                               'QuakeML Source')])
        self.fields_tree_view.setModel(self.field_model)
        self.fields_tree_view.expandAll()

        for r in range(self.field_model.rowCount(QModelIndex())):
            self.fields_tree_view.setFirstColumnSpanned(r, QModelIndex(), True)

        self.output_preferred_origins_only_check.setVisible(
            self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT))
        self.output_preferred_origins_only_check.setEnabled(
            service_config['settings'].get('queryincludeallorigins', False))

        self.output_preferred_magnitudes_only_check.setVisible(
            self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT))
        self.output_preferred_magnitudes_only_check.setEnabled(
            service_config['settings'].get('queryincludeallmagnitudes', False))

        self.check_include_event_params_in_mdp.setVisible(
            self.service_type == SERVICE_MANAGER.MACROSEISMIC)
        self.check_include_event_params_in_mdp.setEnabled(self.service_type == SERVICE_MANAGER.MACROSEISMIC)

        self.output_preferred_mdp_only_check.setVisible(self.service_type == SERVICE_MANAGER.MACROSEISMIC)

        self.output_features_group_box.setVisible(
            self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT))

        preferred_origins_only_checked = s.value('/plugins/qquake/output_preferred_origins', True, bool)
        self.output_preferred_origins_only_check.setChecked(preferred_origins_only_checked)
        preferred_magnitudes_only_checked = s.value(
            '/plugins/qquake/output_preferred_magnitude', True, bool)
        self.output_preferred_magnitudes_only_check.setChecked(preferred_magnitudes_only_checked)
        preferred_mdp_only_checked = s.value(
            '/plugins/qquake/output_preferred_mdp', True, bool)
        self.output_preferred_mdp_only_check.setChecked(preferred_mdp_only_checked)

        include_quake_details_in_mdp = s.value('/plugins/qquake/include_quake_details_in_mdp', True, bool)
        self.check_include_event_params_in_mdp.setChecked(include_quake_details_in_mdp)

        self.reset_fields_button.clicked.connect(self.reset_fields)
        self.check_all_button.clicked.connect(lambda: self._check_all(True))
        self.uncheck_all_button.clicked.connect(lambda: self._check_all(False))
        self.reset_fields_button.setVisible(False)

        if 'fields' in SERVICE_MANAGER.service_details(service_type, service_id)['default']:
            self.set_default_fields(SERVICE_MANAGER.service_details(service_type, service_id)['default']['fields'])

    def accept(self):  # pylint: disable=missing-function-docstring
        s = QgsSettings()
        for r in range(self.field_model.rowCount(QModelIndex())):
            parent = self.field_model.index(r, 0, QModelIndex())
            for rc in range(self.field_model.rowCount(parent)):
                path = self.field_model.data(self.field_model.index(rc, 2, parent), Qt.DisplayRole)
                checked = self.field_model.data(self.field_model.index(rc, 0, parent), Qt.CheckStateRole)
                s.setValue('/plugins/qquake/output_field_{}'.format(path.replace('>', '_')), checked)

        s.setValue('/plugins/qquake/output_preferred_origins',
                   self.output_preferred_origins_only_check.isChecked())
        s.setValue('/plugins/qquake/output_preferred_magnitude',
                   self.output_preferred_magnitudes_only_check.isChecked())
        s.setValue('/plugins/qquake/output_preferred_mdp',
                   self.output_preferred_mdp_only_check.isChecked())

        s.setValue('/plugins/qquake/output_short_field_names',
                   self.radio_short_fields.isChecked())

        if self.check_include_event_params_in_mdp.isEnabled():
            s.setValue('/plugins/qquake/include_quake_details_in_mdp',
                       self.check_include_event_params_in_mdp.isChecked())

        super().accept()

    def change_field_names(self):
        """
        Updates field names after the short fields option is toggled
        """
        short_field_names = self.radio_short_fields.isChecked()

        for r in range(self.field_model.rowCount(QModelIndex())):
            parent = self.field_model.index(r, 0, QModelIndex())
            for rc in range(self.field_model.rowCount(parent)):
                index = self.field_model.index(rc, 2, parent)
                data = self.field_model.data(index, Qt.UserRole)
                new_name = data['field_short' if short_field_names else 'field_long']
                index = self.field_model.index(rc, 1, parent)
                self.field_model.setData(index, new_name, Qt.DisplayRole)

    def selected_fields(self) -> List[str]:
        """
        Returns a list of selected fields
        """
        fields = []
        for r in range(self.field_model.rowCount(QModelIndex())):
            parent = self.field_model.index(r, 0, QModelIndex())
            for rc in range(self.field_model.rowCount(parent)):
                path = self.field_model.data(self.field_model.index(rc, 2, parent), Qt.UserRole)['source']
                checked = self.field_model.data(self.field_model.index(rc, 0, parent), Qt.CheckStateRole)
                if checked:
                    fields.append(path)
        return fields

    def reset_fields(self):
        """
        Resets fields to the default set
        """
        if self.default_fields is None:
            return

        for r in range(self.field_model.rowCount(QModelIndex())):
            parent = self.field_model.index(r, 0, QModelIndex())
            for rc in range(self.field_model.rowCount(parent)):
                path = self.field_model.data(self.field_model.index(rc, 2, parent), Qt.UserRole)['source']
                self.field_model.setData(self.field_model.index(rc, 0, parent), path in self.default_fields,
                                         Qt.CheckStateRole)

    def _check_all(self, checked: bool = True):
        """
        Checks all fields
        """
        for r in range(self.field_model.rowCount(QModelIndex())):
            parent = self.field_model.index(r, 0, QModelIndex())
            for rc in range(self.field_model.rowCount(parent)):
                self.field_model.setData(self.field_model.index(rc, 0, parent), checked, Qt.CheckStateRole)

    def set_default_fields(self, fields: List[str]):
        """
        Sets the default fields
        """
        self.default_fields = fields
        self.reset_fields_button.setVisible(True)

    def output_preferred_magnitudes_only(self) -> bool:
        """
        Returns True if the output preferred magnitudes only option is selected
        """
        return self.output_preferred_magnitudes_only_check.isChecked()

    def output_preferred_origins_only(self) -> bool:
        """
        Returns True if the output preferred origins only option is selected
        """
        return self.output_preferred_origins_only_check.isChecked()

    def output_preferred_mdp_only(self) -> bool:
        """
        Returns True if the output preferred MDP only option is selected
        """
        return self.output_preferred_mdp_only_check.isChecked()
