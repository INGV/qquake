# -*- coding: utf-8 -*-
"""
CQL builder widget
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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox
)
from qgis.gui import (
    QgsGui,
)

from qquake.gui.gui_utils import GuiUtils

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('cql_filter_builder.ui'))


class CqlBuilderWidget(QWidget, FORM_CLASS):
    """
    CQL builder widget
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

    def cql(self) -> str:
        """
        Returns the current CQL string
        """
        return self.sql_editor_widget.text()

    def set_cql(self, cql: str):
        """
        Sets the current CQL string
        """
        self.sql_editor_widget.setText(cql)


class CqlBuilderDialog(QDialog):
    """
    CQL builder dialog
    """

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setWindowTitle(self.tr('Add Data Filters'))

        QgsGui.enableAutoGeometryRestore(self)

        self.widget = CqlBuilderWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):  # pylint: disable=missing-function-docstring
        super().accept()

    def cql(self) -> str:
        """
        Returns the current CQL string
        """
        return self.widget.cql()

    def set_cql(self, cql: str):
        """
        Sets the current CQL string
        """
        self.widget.set_cql(cql)
