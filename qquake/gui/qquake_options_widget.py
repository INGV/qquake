# -*- coding: utf-8 -*-
"""
A widget for configuring general QQuake options
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

from copy import deepcopy

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.gui import (
    QgsOptionsPageWidget
)

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('qquake_options.ui'))


class QQuakeOptionsWidget(FORM_CLASS, QgsOptionsPageWidget):
    """
    A widget for configuring general QQuake options
    """

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.button_add_style.setIcon(GuiUtils.get_icon('add.svg'))
        self.button_remove_style.setIcon(GuiUtils.get_icon('remove.svg'))

        self.style_label_edit.setEnabled(False)
        self.style_type_combo.setEnabled(False)
        self.style_url_edit.setEnabled(False)
        self.button_remove_style.setEnabled(False)

        self.style_type_combo.addItem(self.tr('Events'), SERVICE_MANAGER.FDSNEVENT)
        self.style_type_combo.addItem(self.tr('Macroseismic'), SERVICE_MANAGER.MACROSEISMIC)
        self.style_type_combo.addItem(self.tr('Stations'), SERVICE_MANAGER.FDSNSTATION)

        self.button_add_style.clicked.connect(self._add_style)
        self.button_remove_style.clicked.connect(self._remove_style)

        self._user_styles = deepcopy(SERVICE_MANAGER._user_styles)
        self._refresh_styles_list()

        self.styles_list.currentItemChanged.connect(self._current_style_changed)
        self.style_label_edit.textEdited.connect(self._style_name_changed)
        self.style_url_edit.textEdited.connect(self._style_url_changed)
        self.style_type_combo.currentIndexChanged.connect(self._style_type_changed)

        self.block_style_updates = False

    def _refresh_styles_list(self):
        """
        Refreshes the list of available styles
        """
        self.styles_list.clear()
        for style, _ in self._user_styles.items():
            self.styles_list.addItem(style)

    def _add_style(self):
        """
        Triggers adding a new style
        """
        self._user_styles[self.tr('Untitled')] = {}
        self._refresh_styles_list()

        new_items = self.styles_list.findItems(self.tr('Untitled'), Qt.MatchExactly)
        if new_items:
            self.styles_list.setCurrentItem(new_items[0])

    def _current_style_changed(self, item, _):
        """
        Triggered when the selected style is changed
        """
        if self.block_style_updates:
            return

        if not item:
            self.style_label_edit.setEnabled(False)
            self.style_type_combo.setEnabled(False)
            self.style_url_edit.setEnabled(False)
            self.button_remove_style.setEnabled(False)
            return

        selected_style = item.text()

        self.block_style_updates = True

        self.style_label_edit.setEnabled(True)
        self.style_label_edit.setText(selected_style)

        self.style_type_combo.setEnabled(True)
        name = self.styles_list.currentItem().text()
        if self._user_styles[name].get('type') == 'events':
            self.style_type_combo.setCurrentIndex(self.style_type_combo.findData(SERVICE_MANAGER.FDSNEVENT))
        elif self._user_styles[name].get('type') == 'macroseismic':
            self.style_type_combo.setCurrentIndex(self.style_type_combo.findData(SERVICE_MANAGER.MACROSEISMIC))
        elif self._user_styles[name].get('type') == 'stations':
            self.style_type_combo.setCurrentIndex(self.style_type_combo.findData(SERVICE_MANAGER.FDSNSTATION))

        self.style_url_edit.setEnabled(True)
        self.style_url_edit.setText(self._user_styles[selected_style].get('url'))

        self.button_remove_style.setEnabled(True)
        self.block_style_updates = False

    def _style_name_changed(self, name: str):
        """
        Triggered when the selected style name is changed
        """
        if self.block_style_updates:
            return

        self.block_style_updates = True

        prev_name = self.styles_list.currentItem().text()
        self._user_styles[name] = deepcopy(self._user_styles[prev_name])
        self._user_styles[name]['label'] = name
        del self._user_styles[prev_name]
        self._refresh_styles_list()

        self.styles_list.setCurrentItem(self.styles_list.findItems(name, Qt.MatchExactly)[0])

        self.block_style_updates = False

    def _style_url_changed(self, url: str):
        """
        Triggered when the selected style URL is changed
        """
        if self.block_style_updates:
            return

        self.block_style_updates = True

        name = self.styles_list.currentItem().text()
        self._user_styles[name]['url'] = url

        self.block_style_updates = False

    def _style_type_changed(self):
        """
        Triggered when the selected style type is changed
        """
        if self.block_style_updates:
            return

        self.block_style_updates = True

        name = self.styles_list.currentItem().text()
        if self.style_type_combo.currentData() == SERVICE_MANAGER.FDSNEVENT:
            self._user_styles[name]['type'] = 'events'
        elif self.style_type_combo.currentData() == SERVICE_MANAGER.MACROSEISMIC:
            self._user_styles[name]['type'] = 'macroseismic'
        elif self.style_type_combo.currentData() == SERVICE_MANAGER.FDSNSTATION:
            self._user_styles[name]['type'] = 'stations'

        self.block_style_updates = False

    def _remove_style(self):
        """
        Removes the selected style
        """
        prev_name = self.styles_list.currentItem().text()
        del self._user_styles[prev_name]
        self._refresh_styles_list()

    def apply(self):  # pylint:disable=missing-docstring
        SERVICE_MANAGER.set_user_styles(self._user_styles)
