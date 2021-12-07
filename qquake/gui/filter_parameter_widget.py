# -*- coding: utf-8 -*-
"""
Service parameter based filtering widget
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
from typing import Optional, List, Dict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal,
    Qt,
    QDateTime
)
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsSettings,
    QgsUnitTypes,
    QgsRectangle,
    QgsPointXY
)
from qgis.gui import (
    QgsMapToolExtent,
    QgsMapToolEmitPoint,
)

from qquake.gui.base_filter_widget import BaseFilterWidget
from qquake.gui.gui_utils import GuiUtils
from qquake.gui.predefined_areas_dialog import PredefinedAreasDialog
from qquake.quakeml.common import EVENT_TYPES
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('filter_parameter_widget_base.ui'))


class FilterParameterWidget(QWidget, FORM_CLASS, BaseFilterWidget):  # pylint: disable=too-many-public-methods
    """
    Service parameter based filtering widget
    """
    changed = pyqtSignal()

    def __init__(self,  # pylint: disable=too-many-statements
                 iface,
                 service_type: str,
                 parent: Optional[QWidget] = None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollArea > QWidget > QScrollBar { background: 1; }
        """)

        for m in range(1, 13):
            self.earthquake_max_intensity_greater_combo.addItem(str(m), m)

        self.iface = iface
        self.previous_map_tool = None
        self.extent_tool = None
        self.customize_areas_dialog = None

        self.set_extent_from_canvas_extent(self.iface.mapCanvas().extent())
        self.set_center_from_canvas_point(self.iface.mapCanvas().extent().center())

        self.fdsn_event_start_date.dateChanged.connect(self._refresh_date)
        self.min_time_check.toggled.connect(self.changed)
        self.fdsn_event_start_date.dateChanged.connect(self.changed)
        self.max_time_check.toggled.connect(self.changed)
        self.fdsn_event_end_date.dateChanged.connect(self.changed)
        self.min_mag_check.toggled.connect(self.changed)
        self.fdsn_event_min_magnitude.valueChanged.connect(self.changed)
        self.max_mag_check.toggled.connect(self.changed)
        self.fdsn_event_max_magnitude.valueChanged.connect(self.changed)
        self.lat_min_spinbox.valueChanged.connect(self.changed)
        self.lat_max_spinbox.valueChanged.connect(self.changed)
        self.long_min_spinbox.valueChanged.connect(self.changed)
        self.long_max_spinbox.valueChanged.connect(self.changed)
        self.lat_min_checkbox.toggled.connect(self.changed)
        self.lat_max_checkbox.toggled.connect(self.changed)
        self.long_min_checkbox.toggled.connect(self.changed)
        self.long_max_checkbox.toggled.connect(self.changed)
        self.limit_extent_checkbox.toggled.connect(self.changed)
        self.radio_rectangular_area.toggled.connect(self.changed)
        self.radio_circular_area.toggled.connect(self.changed)
        self.radio_predefined_area.toggled.connect(self.changed)
        self.circular_lat_spinbox.valueChanged.connect(self.changed)
        self.circular_long_spinbox.valueChanged.connect(self.changed)
        self.radius_min_checkbox.toggled.connect(self.changed)
        self.radius_max_checkbox.toggled.connect(self.changed)
        self.radius_min_spinbox.valueChanged.connect(self.changed)
        self.radius_max_spinbox.valueChanged.connect(self.changed)
        self.radius_unit_combobox.currentIndexChanged.connect(self.changed)
        self.earthquake_max_intensity_greater_check.toggled.connect(self.changed)
        self.earthquake_max_intensity_greater_combo.currentIndexChanged.connect(self.changed)
        self.earthquake_number_mdps_greater_check.toggled.connect(self.changed)
        self.earthquake_number_mdps_greater_spin.valueChanged.connect(self.changed)
        self.output_table_options_widget.changed.connect(self.changed)
        self.event_type_check.toggled.connect(self.changed)
        self.event_type_combo.currentIndexChanged.connect(self.changed)
        self.events_updated_after_check.toggled.connect(self.changed)
        self.events_updated_after.dateChanged.connect(self.changed)

        self.rect_extent_draw_on_map.clicked.connect(self.draw_rect_on_map)
        self.circle_center_draw_on_map.clicked.connect(self.draw_center_on_map)

        self.radio_rectangular_area.toggled.connect(self._enable_widgets)
        self.radio_circular_area.toggled.connect(self._enable_widgets)
        self.radio_predefined_area.toggled.connect(self._enable_widgets)
        self.limit_extent_checkbox.toggled.connect(self._enable_widgets)
        self.lat_min_checkbox.toggled.connect(self._enable_widgets)
        self.lat_max_checkbox.toggled.connect(self._enable_widgets)
        self.long_min_checkbox.toggled.connect(self._enable_widgets)
        self.long_max_checkbox.toggled.connect(self._enable_widgets)
        self.radius_min_checkbox.toggled.connect(self._enable_widgets)
        self.radius_max_checkbox.toggled.connect(self._enable_widgets)
        self.min_time_check.toggled.connect(self._enable_widgets)
        self.max_time_check.toggled.connect(self._enable_widgets)
        self.min_mag_check.toggled.connect(self._enable_widgets)
        self.max_mag_check.toggled.connect(self._enable_widgets)
        self.output_table_options_widget.changed.connect(self._enable_widgets)
        self.earthquake_max_intensity_greater_check.toggled.connect(self._enable_widgets)
        self.earthquake_number_mdps_greater_check.toggled.connect(self._enable_widgets)
        self._enable_widgets()

        self._populated_predefined_areas()
        SERVICE_MANAGER.areasChanged.connect(self._populated_predefined_areas)
        self.combo_predefined_area.currentIndexChanged.connect(self._use_predefined_area)
        self.radio_predefined_area.toggled.connect(self._use_predefined_area)

        self.button_customize_areas.clicked.connect(self._customize_areas)

        self.event_type_check.toggled.connect(self._enable_widgets)
        for event_type in EVENT_TYPES:
            self.event_type_combo.addItem(event_type, event_type)

        self.events_updated_after_check.toggled.connect(self._enable_widgets)

        self.service_type = None
        self.service_id = None
        self.set_service_type(service_type)

    def is_valid(self) -> bool:
        for check in [self.min_time_check, self.max_time_check, self.min_mag_check, self.max_mag_check,
                      self.limit_extent_checkbox, self.earthquake_max_intensity_greater_check,
                      self.earthquake_number_mdps_greater_check]:
            if check.isChecked():
                return True

        return False

    def set_service_type(self, service_type: str):
        self.service_type = service_type

        self.time_coverage_group.setVisible(
            self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION))
        self.magnitude_group.setVisible(self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT))
        self.macroseismic_data_group.setVisible(self.service_type == SERVICE_MANAGER.MACROSEISMIC)

        self.output_table_options_widget.set_service_type(service_type)

    def set_service_id(self, service_id: str):  # pylint:disable=too-many-branches
        self.service_id = service_id

        service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

        self.output_table_options_widget.set_service_id(service_id)

        if not service_config['settings'].get('querycircular', False):
            if self.radio_circular_area.isChecked():
                self.radio_rectangular_area.setChecked(True)
            self.radio_circular_area.setEnabled(False)
        else:
            self.radio_circular_area.setEnabled(True)

        if not service_config['settings'].get('queryeventtype', False):
            if self.event_type_check.isChecked():
                self.event_type_check.setChecked(False)
            self.event_type_check.setEnabled(False)
        else:
            self.event_type_check.setEnabled(True)

        if not service_config['settings'].get('queryupdatedafter', False):
            if self.events_updated_after_check.isChecked():
                self.events_updated_after_check.setChecked(False)
            self.events_updated_after_check.setEnabled(False)
        else:
            self.events_updated_after_check.setEnabled(True)

        self.radius_unit_combobox.clear()
        self.radius_unit_combobox.addItem(self.tr('Degrees'), QgsUnitTypes.DistanceDegrees)
        if service_config['settings'].get('querycircularradiuskm', False):
            self.radius_unit_combobox.insertItem(0, self.tr('Kilometers'), QgsUnitTypes.DistanceKilometers)
        self.radius_unit_combobox.setCurrentIndex(0)

    def restore_settings(self, prefix: str):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        s = QgsSettings()

        if self.service_id:
            service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)
        else:
            service_config = None

        last_event_start_date = s.value('/plugins/qquake/{}_last_event_start_date'.format(prefix))
        if last_event_start_date is not None:
            self.fdsn_event_start_date.setDateTime(last_event_start_date)
        last_event_end_date = s.value('/plugins/qquake/{}_last_event_end_date'.format(prefix))
        if last_event_end_date is not None:
            self.fdsn_event_end_date.setDateTime(last_event_end_date)
        last_event_min_magnitude = s.value('/plugins/qquake/{}_last_event_min_magnitude'.format(prefix))
        if last_event_min_magnitude is not None:
            self.fdsn_event_min_magnitude.setValue(float(last_event_min_magnitude))
        last_event_max_magnitude = s.value('/plugins/qquake/{}_last_event_max_magnitude'.format(prefix))
        if last_event_max_magnitude is not None:
            self.fdsn_event_max_magnitude.setValue(float(last_event_max_magnitude))
        self.limit_extent_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_extent_enabled2'.format(prefix), False, bool))
        self.radio_predefined_area.setChecked(
            s.value('/plugins/qquake/{}_last_event_extent_named'.format(prefix), False, bool))
        last_area = s.value('/plugins/qquake/{}_last_event_extent_name'.format(prefix), '', str)
        if last_area:
            self.combo_predefined_area.setCurrentIndex(self.combo_predefined_area.findData(last_area))
        self.radio_rectangular_area.setChecked(
            s.value('/plugins/qquake/{}_last_event_extent_rect2'.format(prefix), False, bool))

        if not service_config or service_config['settings'].get('querycircular', False):
            self.radio_circular_area.setChecked(
                s.value('/plugins/qquake/{}_last_event_extent_circle2'.format(prefix), False, bool))
        self.lat_min_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_min_lat_checked2'.format(prefix), False, bool))
        self.lat_max_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_max_lat_checked2'.format(prefix), False, bool))
        self.long_min_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_min_long_checked2'.format(prefix), False, bool))
        self.long_max_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_max_long_checked2'.format(prefix), False, bool))

        self.radius_min_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_circle_radius_min_checked2'.format(prefix), False, bool))
        self.radius_max_checkbox.setChecked(
            s.value('/plugins/qquake/{}_last_event_circle_radius_max_checked2'.format(prefix), False, bool))

        self.radius_unit_combobox.setCurrentIndex(
            max(0, self.radius_unit_combobox.findData(
                s.value('/plugins/qquake/{}_last_event_circle_unit'.format(prefix),
                        int(QgsUnitTypes.DistanceKilometers), int))))

        last_event_min_lat = s.value('/plugins/qquake/{}_last_event_min_lat'.format(prefix))
        if last_event_min_lat is not None:
            self.lat_min_spinbox.setValue(float(last_event_min_lat))
        last_event_max_lat = s.value('/plugins/qquake/{}_last_event_max_lat'.format(prefix))
        if last_event_max_lat is not None:
            self.lat_max_spinbox.setValue(float(last_event_max_lat))
        last_event_min_long = s.value('/plugins/qquake/{}_last_event_min_long'.format(prefix))
        if last_event_min_long is not None:
            self.long_min_spinbox.setValue(float(last_event_min_long))
        last_event_max_long = s.value('/plugins/qquake/{}_last_event_max_long'.format(prefix))
        if last_event_max_long is not None:
            self.long_max_spinbox.setValue(float(last_event_max_long))

        last_event_circle_lat = s.value('/plugins/qquake/{}_last_event_circle_lat'.format(prefix))
        if last_event_circle_lat is not None:
            self.circular_lat_spinbox.setValue(float(last_event_circle_lat))
        last_event_circle_long = s.value('/plugins/qquake/{}_last_event_circle_long'.format(prefix))
        if last_event_circle_long is not None:
            self.circular_long_spinbox.setValue(float(last_event_circle_long))

        last_event_min_radius = s.value('/plugins/qquake/{}_last_event_circle_min_radius'.format(prefix))
        if last_event_min_radius is not None:
            self.radius_min_spinbox.setValue(float(last_event_min_radius))
        last_event_max_radius = s.value('/plugins/qquake/{}_last_event_circle_max_radius'.format(prefix))
        if last_event_max_radius is not None:
            self.radius_max_spinbox.setValue(float(last_event_max_radius))

        self.min_time_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_min_time_checked2'.format(prefix), False, bool))
        self.max_time_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_max_time_checked2'.format(prefix), False, bool))
        self.min_mag_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_min_mag_checked2'.format(prefix), False, bool))
        self.max_mag_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_max_mag_checked2'.format(prefix), False, bool))
        self.earthquake_max_intensity_greater_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_max_intensity_greater_checked2'.format(prefix), False, bool))
        v = s.value('/plugins/qquake/{}_last_event_max_intensity_greater'.format(prefix))
        if v is not None:
            self.earthquake_max_intensity_greater_combo.setCurrentIndex(
                self.earthquake_max_intensity_greater_combo.findData(float(v)))

        self.earthquake_number_mdps_greater_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_mdps_greater_checked2'.format(prefix), False, bool))
        v = s.value('/plugins/qquake/{}_last_event_mdps_greater'.format(prefix))
        if v is not None:
            self.earthquake_number_mdps_greater_spin.setValue(int(v))

        self.output_table_options_widget.restore_settings(prefix, 'last')

        self.event_type_check.setChecked(
            s.value('/plugins/qquake/{}_last_event_type_checked'.format(prefix), False, bool))
        last_event_type = s.value('/plugins/qquake/{}_last_event_type'.format(prefix), '', str)
        if last_event_type is not None:
            self.event_type_combo.setCurrentIndex(self.event_type_combo.findData(last_event_type))

        self.events_updated_after_check.setChecked(
            s.value('/plugins/qquake/{}_events_updated_after_checked'.format(prefix), False, bool))
        last_updated_after_date = s.value('/plugins/qquake/{}_events_updated_after_date'.format(prefix))
        if last_updated_after_date is not None:
            self.events_updated_after.setDateTime(last_updated_after_date)

    def save_settings(self, prefix: str):
        s = QgsSettings()
        s.setValue('/plugins/qquake/{}_last_event_start_date'.format(prefix), self.fdsn_event_start_date.dateTime())
        s.setValue('/plugins/qquake/{}_last_event_end_date'.format(prefix), self.fdsn_event_end_date.dateTime())
        s.setValue('/plugins/qquake/{}_last_event_min_magnitude'.format(prefix), self.fdsn_event_min_magnitude.value())
        s.setValue('/plugins/qquake/{}_last_event_max_magnitude'.format(prefix), self.fdsn_event_max_magnitude.value())

        s.setValue('/plugins/qquake/{}_last_event_extent_enabled2'.format(prefix),
                   self.limit_extent_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_extent_named'.format(prefix), self.radio_predefined_area.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_extent_name'.format(prefix), self.combo_predefined_area.currentData())

        s.setValue('/plugins/qquake/{}_last_event_extent_rect2'.format(prefix), self.radio_rectangular_area.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_extent_circle2'.format(prefix), self.radio_circular_area.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_min_lat_checked2'.format(prefix), self.lat_min_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_min_lat'.format(prefix), self.lat_min_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_max_lat_checked2'.format(prefix), self.lat_max_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_max_lat'.format(prefix), self.lat_max_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_min_long_checked2'.format(prefix), self.long_min_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_min_long'.format(prefix), self.long_min_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_max_long_checked2'.format(prefix), self.long_max_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_max_long'.format(prefix), self.long_max_spinbox.value())

        s.setValue('/plugins/qquake/{}_last_event_circle_long'.format(prefix), self.circular_long_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_circle_lat'.format(prefix), self.circular_lat_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_circle_radius_min_checked2'.format(prefix),
                   self.radius_min_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_circle_radius_max_checked2'.format(prefix),
                   self.radius_max_checkbox.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_circle_min_radius'.format(prefix), self.radius_min_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_circle_max_radius'.format(prefix), self.radius_max_spinbox.value())
        s.setValue('/plugins/qquake/{}_last_event_circle_unit'.format(prefix),
                   int(self.radius_unit_combobox.currentData()))

        s.setValue('/plugins/qquake/{}_last_event_max_intensity_greater_checked2'.format(prefix),
                   self.earthquake_max_intensity_greater_check.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_max_intensity_greater'.format(prefix),
                   self.earthquake_max_intensity_greater_combo.currentData())
        s.setValue('/plugins/qquake/{}_last_event_mdps_greater_checked2'.format(prefix),
                   self.earthquake_number_mdps_greater_check.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_mdps_greater'.format(prefix),
                   self.earthquake_number_mdps_greater_spin.value())

        s.setValue('/plugins/qquake/{}_last_event_min_time_checked2'.format(prefix), self.min_time_check.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_max_time_checked2'.format(prefix), self.max_time_check.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_min_mag_checked2'.format(prefix), self.min_mag_check.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_max_mag_checked2'.format(prefix), self.max_mag_check.isChecked())

        self.output_table_options_widget.save_settings(prefix, 'last')

        s.setValue('/plugins/qquake/{}_last_event_type'.format(prefix), self.event_type_combo.currentData())
        s.setValue('/plugins/qquake/{}_last_event_type_checked'.format(prefix),
                   self.event_type_check.isChecked())

        s.setValue('/plugins/qquake/{}_events_updated_after_date'.format(prefix), self.events_updated_after.dateTime())
        s.setValue('/plugins/qquake/{}_events_updated_after_checked'.format(prefix),
                   self.events_updated_after_check.isChecked())

    def _populated_predefined_areas(self):
        """
        Populates the predefined area choices
        """
        self.combo_predefined_area.clear()
        for name in SERVICE_MANAGER.available_predefined_bounding_boxes():
            extent = SERVICE_MANAGER.predefined_bounding_box(name)
            self.combo_predefined_area.addItem(extent['title'], name)

    def _use_predefined_area(self):
        """
        Retrieves the selected predefined area details and updates the widget state accordingly
        """
        if not self.radio_predefined_area.isChecked():
            return

        selected_extent_id = self.combo_predefined_area.currentData()
        if selected_extent_id not in SERVICE_MANAGER.available_predefined_bounding_boxes():
            return

        extent = SERVICE_MANAGER.predefined_bounding_box(selected_extent_id)['boundingbox']
        self.lat_min_spinbox.setValue(extent[1])
        self.lat_max_spinbox.setValue(extent[3])
        self.long_min_spinbox.setValue(extent[0])
        self.long_max_spinbox.setValue(extent[2])
        self.lat_max_checkbox.setChecked(True)
        self.long_max_checkbox.setChecked(True)
        self.lat_min_checkbox.setChecked(True)
        self.long_min_checkbox.setChecked(True)

    def set_extent_from_canvas_extent(self, rect: QgsRectangle):
        """
        Sets the widget extent from the canvas extent
        """
        ct = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),
                                    QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        try:
            rect = ct.transformBoundingBox(rect)
            self.lat_min_spinbox.setValue(rect.yMinimum())
            self.lat_max_spinbox.setValue(rect.yMaximum())
            self.long_min_spinbox.setValue(rect.xMinimum())
            self.long_max_spinbox.setValue(rect.xMaximum())
        except QgsCsException:
            pass

    def set_center_from_canvas_point(self, point: QgsPointXY):
        """
        Sets the widget center point from a canvas point
        """
        ct = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),
                                    QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        try:
            point = ct.transform(point)
            self.circular_lat_spinbox.setValue(point.y())
            self.circular_long_spinbox.setValue(point.x())
        except QgsCsException:
            pass

    def _enable_widgets(self):
        """
        Selectively enables widgets based on overall state
        """
        for w in [self.lat_min_checkbox,
                  self.lat_max_checkbox,
                  self.long_min_checkbox,
                  self.long_max_checkbox,
                  self.lat_min_spinbox,
                  self.lat_max_spinbox,
                  self.long_min_spinbox,
                  self.long_max_spinbox,
                  self.label_rect_lat,
                  self.label_rect_long,
                  self.rect_extent_draw_on_map]:
            w.setEnabled(self.radio_rectangular_area.isChecked() and self.limit_extent_checkbox.isChecked())
        self.lat_min_spinbox.setEnabled(self.lat_min_spinbox.isEnabled() and self.lat_min_checkbox.isChecked())
        self.lat_max_spinbox.setEnabled(self.lat_max_spinbox.isEnabled() and self.lat_max_checkbox.isChecked())
        self.long_min_spinbox.setEnabled(self.long_min_spinbox.isEnabled() and self.long_min_checkbox.isChecked())
        self.long_max_spinbox.setEnabled(self.long_max_spinbox.isEnabled() and self.long_max_checkbox.isChecked())

        self.combo_predefined_area.setEnabled(self.radio_predefined_area.isChecked())

        for w in [self.circular_lat_spinbox,
                  self.circular_long_spinbox,
                  self.radius_min_checkbox,
                  self.radius_min_spinbox,
                  self.radius_max_checkbox,
                  self.radius_max_spinbox,
                  self.label_circ_center,
                  self.label_circ_radius,
                  self.label_circ_lat,
                  self.label_circ_long,
                  self.circle_center_draw_on_map,
                  self.radius_unit_combobox]:
            w.setEnabled(self.radio_circular_area.isChecked() and self.limit_extent_checkbox.isChecked())
        self.radius_min_spinbox.setEnabled(self.radius_min_spinbox.isEnabled() and self.radius_min_checkbox.isChecked())
        self.radius_max_spinbox.setEnabled(self.radius_max_spinbox.isEnabled() and self.radius_max_checkbox.isChecked())

        self.fdsn_event_start_date.setEnabled(self.min_time_check.isChecked())
        self.fdsn_event_end_date.setEnabled(self.max_time_check.isChecked())
        self.fdsn_event_min_magnitude.setEnabled(self.min_mag_check.isChecked())
        self.fdsn_event_max_magnitude.setEnabled(self.max_mag_check.isChecked())

        self.earthquake_max_intensity_greater_combo.setEnabled(self.earthquake_max_intensity_greater_check.isChecked())
        self.earthquake_number_mdps_greater_spin.setEnabled(self.earthquake_number_mdps_greater_check.isChecked())

        self.event_type_combo.setEnabled(self.event_type_check.isChecked())
        self.events_updated_after.setEnabled(self.events_updated_after_check.isChecked())

    def draw_rect_on_map(self):
        """
        Triggers drawing an extent rectangle on the map
        """
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        if not self.extent_tool:
            self.extent_tool = QgsMapToolExtent(self.iface.mapCanvas())
            self.extent_tool.extentChanged.connect(self.extent_drawn)
            self.extent_tool.deactivated.connect(self.deactivate_tool)
        self.iface.mapCanvas().setMapTool(self.extent_tool)
        self.window().setVisible(False)

    def draw_center_on_map(self):
        """
        Triggers picking a center point from the map
        """
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        if not self.extent_tool:
            self.extent_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
            self.extent_tool.canvasClicked.connect(self.center_picked)
            self.extent_tool.deactivated.connect(self.deactivate_tool)
        self.iface.mapCanvas().setMapTool(self.extent_tool)
        self.window().setVisible(False)

    def extent_drawn(self, extent: QgsRectangle):
        """
        Called after an extent is drawn on the canvas
        """
        self.set_extent_from_canvas_extent(extent)
        self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def center_picked(self, point: QgsPointXY, button):  # pylint: disable=unused-argument
        """
        Called after a center point is picked on the canvas
        """
        self.set_center_from_canvas_point(point)
        self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def deactivate_tool(self):
        """
        Called when the current tool should be deactivated
        """
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def _refresh_date(self):
        """
        Avoids negative date intervals by checking start_date > end_date
        """

        if self.fdsn_event_start_date.dateTime() > self.fdsn_event_end_date.dateTime():
            self.fdsn_event_end_date.setDate(self.fdsn_event_start_date.date())

    def set_date_range_limits(self, date_start: Optional[QDateTime] = None, date_end: Optional[QDateTime] = None):
        """
        Sets the widget date range limits
        """
        if date_start:
            self.fdsn_event_start_date.setMinimumDateTime(date_start)

            self.fdsn_event_start_date.setDateTime(date_start)
            self.min_time_check.setText(
                self.tr("Start (from {})").format(date_start.toString('yyyy-MM-dd')))
        else:
            self.fdsn_event_start_date.clearMinimumDate()

            self.min_time_check.setText(self.tr("Start"))

        if date_end:
            self.fdsn_event_start_date.setMaximumDateTime(date_end)

            self.max_time_check.setText(
                self.tr("End (until {})").format(date_end.toString('yyyy-MM-dd')))
        else:
            self.fdsn_event_start_date.clearMaximumDate()

            self.max_time_check.setText(self.tr("End"))

        if date_start:
            self.fdsn_event_end_date.setMinimumDateTime(date_start)
        else:
            self.fdsn_event_end_date.clearMinimumDate()
        if date_end:
            self.fdsn_event_end_date.setMaximumDateTime(date_end)
        else:
            self.fdsn_event_end_date.clearMaximumDate()

        # just make a week difference from START date
        if date_start:
            self.fdsn_event_end_date.setDateTime(date_start.addDays(7))

    def set_current_date_range(self, date_start: Optional[QDateTime] = None, date_end: Optional[QDateTime] = None):
        """
        Sets the current widget date range
        """
        if date_start is not None:
            self.fdsn_event_start_date.setDateTime(date_start)
            self.min_time_check.setChecked(True)
        else:
            self.min_time_check.setChecked(False)

        if date_end is not None:
            self.fdsn_event_end_date.setDateTime(date_end)
            self.max_time_check.setChecked(True)
        else:
            self.max_time_check.setChecked(False)

    def set_predefined_bounding_box(self, box):
        """
        Sets the current predefined bounding box
        """
        self.radio_predefined_area.setChecked(True)
        self.combo_predefined_area.setCurrentIndex(self.combo_predefined_area.findData(box))

    def set_min_latitude(self, lat: float):
        """
        Sets minimum latitude
        """
        self.radio_rectangular_area.setChecked(True)
        self.lat_min_spinbox.setValue(float(lat))

    def set_max_latitude(self, lat: float):
        """
        Sets maximum latitude
        """
        self.radio_rectangular_area.setChecked(True)
        self.lat_max_spinbox.setValue(float(lat))

    def set_min_longitude(self, long: float):
        """
        Sets minimum longitude
        """
        self.radio_rectangular_area.setChecked(True)
        self.long_min_spinbox.setValue(float(long))

    def set_max_longitude(self, long: float):
        """
        Sets the maximum longitude
        """
        self.radio_rectangular_area.setChecked(True)
        self.long_max_spinbox.setValue(float(long))

    def set_circle_longitude(self, long: float):
        """
        Sets the circle center longitude
        """
        self.radio_circular_area.setChecked(True)
        self.circular_long_spinbox.setValue(float(long))

    def set_circle_latitude(self, lat: float):
        """
        Sets the circle center latitude
        """
        self.radio_circular_area.setChecked(True)
        self.circular_lat_spinbox.setValue(float(lat))

    def set_min_circle_radius(self, radius: float):
        """
        Sets the minimum circle radius
        """
        self.radius_min_checkbox.setChecked(True)
        self.radius_min_spinbox.setValue(float(radius))

    def set_max_circle_radius(self, radius: float):
        """
        Sets the maximum circle radius
        """
        self.radius_max_checkbox.setChecked(True)
        self.radius_max_spinbox.setValue(float(radius))

    def set_min_magnitude(self, mag: Optional[float]):
        """
        Sets the minimum magnitude filter value
        """
        self.min_mag_check.setChecked(mag is not None)
        if mag is not None:
            self.fdsn_event_min_magnitude.setValue(float(mag))

    def set_max_magnitude(self, mag: Optional[float]):
        """
        Sets the maximum magnitude filter value
        """
        self.max_mag_check.setChecked(mag is not None)
        if mag is not None:
            self.fdsn_event_max_magnitude.setValue(float(mag))

    def set_max_intensity_greater(self, intensity: Optional[float]):
        """
        Sets the intensity greater than filter value
        """
        self.earthquake_max_intensity_greater_check.setChecked(intensity is not None)
        if intensity is not None:
            self.earthquake_max_intensity_greater_combo.setCurrentIndex(
                self.earthquake_max_intensity_greater_combo.findData(float(intensity)))

    def set_mdps_greater_than(self, mdps: Optional[float]):
        """
        Sets the MDPs greater than filter value
        """
        self.earthquake_number_mdps_greater_check.setChecked(mdps is not None)
        if mdps is not None:
            self.earthquake_number_mdps_greater_spin.setValue(float(mdps))

    def set_event_type(self, event_type: Optional[str]):
        """
        Sets the event type than filter value
        """
        self.event_type_check.setChecked(event_type is not None)
        if event_type is not None:
            self.event_type_combo.setCurrentIndex(self.event_type_combo.findData(event_type))

    def set_updated_after(self, after: Optional[QDateTime]):
        """
        Sets the updated after date
        """
        self.events_updated_after_check.setChecked(after is not None)
        if after is not None:
            self.events_updated_after.setDateTime(after)

    def set_extent_limit(self, box: List[float]):
        """
        Sets the extent limits
        """
        self.long_min_spinbox.setMinimum(box[0])
        self.long_max_spinbox.setMinimum(box[0])
        self.lat_min_spinbox.setMinimum(box[1])
        self.lat_max_spinbox.setMinimum(box[1])
        self.long_min_spinbox.setMaximum(box[2])
        self.long_max_spinbox.setMaximum(box[2])
        self.lat_min_spinbox.setMaximum(box[3])
        self.lat_max_spinbox.setMaximum(box[3])

        # reset previously selected predefined area, now that new min/max area has been applied
        self._use_predefined_area()

    def start_date(self) -> Optional[QDateTime]:
        """
        Returns the start date
        """
        if self.service_type not in (
                SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION):
            return None

        return self.fdsn_event_start_date.dateTime() if self.min_time_check.isChecked() else None

    def end_date(self) -> Optional[QDateTime]:
        """
        Returns the start date
        """
        if self.service_type not in (
                SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION):
            return None

        return self.fdsn_event_end_date.dateTime() if self.max_time_check.isChecked() else None

    def min_magnitude(self) -> Optional[float]:
        """
        Returns the maximum magnitude
        """
        if self.service_type not in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT):
            return None

        return self.fdsn_event_min_magnitude.value() if self.min_mag_check.isChecked() else None

    def max_magnitude(self) -> Optional[float]:
        """
        Returns the maximum magnitude
        """
        if self.service_type not in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT):
            return None

        return self.fdsn_event_max_magnitude.value() if self.max_mag_check.isChecked() else None

    def extent_rect(self) -> bool:
        """
        Returns True if extent should be filtered by rectangle
        """
        return self.limit_extent_checkbox.isChecked() and (self.radio_rectangular_area.isChecked() or
                                                           self.radio_predefined_area.isChecked())

    def min_latitude(self) -> Optional[float]:
        """
        Returns the minimum latitude for the extent
        """
        return self.lat_min_spinbox.value() if self.lat_min_checkbox.isChecked() else None

    def max_latitude(self) -> Optional[float]:
        """
        Returns the maximum latitude for the extent
        """
        return self.lat_max_spinbox.value() if self.lat_max_checkbox.isChecked() else None

    def min_longitude(self) -> Optional[float]:
        """
        Returns the minimum longitude for the extent
        """
        return self.long_min_spinbox.value() if self.long_min_checkbox.isChecked() else None

    def max_longitude(self) -> Optional[float]:
        """
        Returns the maximum longitude for the extent
        """
        return self.long_max_spinbox.value() if self.long_max_checkbox.isChecked() else None

    def limit_extent_circle(self) -> bool:
        """
        Returns True if extent should be limited to a circle region
        """
        return self.limit_extent_checkbox.isChecked() and self.radio_circular_area.isChecked()

    def circle_latitude(self) -> float:
        """
        Returns the circle longitude
        """
        return self.circular_lat_spinbox.value()

    def circle_longitude(self) -> float:
        """
        Returns the circle longitude
        """
        return self.circular_long_spinbox.value()

    def circle_min_radius(self) -> Optional[float]:
        """
        Returns the minimum circle radius distance
        """
        return self.radius_min_spinbox.value() if self.radius_min_checkbox.isChecked() else None

    def circle_max_radius(self) -> Optional[float]:
        """
        Returns the maximum circle radius distance
        """
        return self.radius_max_spinbox.value() if self.radius_max_checkbox.isChecked() else None

    def circle_radius_unit(self) -> QgsUnitTypes.DistanceUnit:
        """
        Returns the circle radius unit
        """
        return self.radius_unit_combobox.currentData()

    def earthquake_max_intensity_greater(self) -> Optional[float]:
        """
        Returns the max intensity greater than filter value
        """
        if self.service_type != SERVICE_MANAGER.MACROSEISMIC:
            return None
        return self.earthquake_max_intensity_greater_combo.currentData() if self.earthquake_max_intensity_greater_check.isChecked() else None

    def earthquake_number_mdps_greater(self) -> Optional[float]:
        """
        Returns the MDP greater than filter value
        """
        if self.service_type != SERVICE_MANAGER.MACROSEISMIC:
            return None

        return self.earthquake_number_mdps_greater_spin.value() if self.earthquake_number_mdps_greater_check.isChecked() else None

    def convert_negative_depths(self) -> bool:
        return self.output_options_widget.convert_negative_depths()

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        return self.output_options_widget.depth_unit()

    def event_type(self) -> Optional[str]:
        """
        Returns the selected event type, or None
        """
        return self.event_type_combo.currentData() if self.event_type_check.isChecked() else None

    def updated_after(self) -> Optional[QDateTime]:
        """
        Returns the selected updated after date, or None
        """
        return self.events_updated_after.dateTime() if self.events_updated_after_check.isChecked() else None

    def output_type(self) -> str:
        return self.output_table_options_widget.output_type()

    def output_fields(self) -> Optional[List[str]]:
        return self.output_table_options_widget.output_fields

    def selected_styles(self) -> Dict[str, str]:
        return self.output_table_options_widget.selected_styles()

    def to_service_definition(self) -> dict:
        """
        Converts the widget state to a service definition
        """
        base_config = deepcopy(SERVICE_MANAGER.service_details(self.service_type, self.service_id))

        defaults = base_config.get('default', {})

        for k, v in {'datestart': self.start_date().toString(Qt.ISODate) if self.start_date() else None,
                     'dateend': self.end_date().toString(Qt.ISODate) if self.end_date() else None,
                     'boundingboxpredefined': self.combo_predefined_area.currentData() if self.radio_predefined_area.isChecked() else None,
                     'minimumlatitude': self.min_latitude() if self.radio_rectangular_area.isChecked() else None,
                     'maximumlatitude': self.max_latitude() if self.radio_rectangular_area.isChecked() else None,
                     'minimumlongitude': self.min_longitude() if self.radio_rectangular_area.isChecked() else None,
                     'maximumlongitude': self.max_longitude() if self.radio_rectangular_area.isChecked() else None,
                     'circlelatitude': self.circle_latitude() if self.radio_circular_area.isChecked() else None,
                     'circlelongitude': self.circle_longitude() if self.radio_circular_area.isChecked() else None,
                     'minimumcircleradius': self.circle_min_radius() if self.radio_circular_area.isChecked() else None,
                     'maximumcircleradius': self.circle_max_radius() if self.radio_circular_area.isChecked() else None,
                     'minimummagnitude': self.min_magnitude(),
                     'maximummagnitude': self.max_magnitude(),
                     'macromaxintensitygreater': self.earthquake_max_intensity_greater(),
                     'macromdpsgreaterthan': self.earthquake_number_mdps_greater(),
                     'eventtype': self.event_type(),
                     'updatedafter': self.updated_after().toString(Qt.ISODate) if self.updated_after() else None,
                     }.items():
            if v:
                defaults[k] = v
            elif k in defaults:
                del defaults[k]

        base_config['default'] = defaults
        return base_config

    def _customize_areas(self):
        """
        Shows the customise areas dialog
        """
        if self.customize_areas_dialog:
            self.customize_areas_dialog.show()
            return

        self.customize_areas_dialog = PredefinedAreasDialog(self)
        self.customize_areas_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self.customize_areas_dialog.show()

        def accepted():
            self.customize_areas_dialog = None

        def rejected():
            self.customize_areas_dialog = None

        self.customize_areas_dialog.accepted.connect(accepted)
        self.customize_areas_dialog.rejected.connect(rejected)
