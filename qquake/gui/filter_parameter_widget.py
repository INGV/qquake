# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuakeDialog
                                 A QGIS plugin
 QQuake plugin to download seismologic data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Faunalia
        email                : matteo.ghetta@faunalia.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from copy import deepcopy
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import pyqtSignal, Qt

from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsSettings
)
from qgis.gui import (
    QgsMapToolExtent,
    QgsMapToolEmitPoint,
)

from qquake.gui.gui_utils import GuiUtils
from qquake.gui.output_table_options_dialog import OutputTableOptionsDialog
from qquake.services import SERVICE_MANAGER
from qquake.fetcher import Fetcher

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('filter_parameter_widget_base.ui'))


class FilterParameterWidget(QWidget, FORM_CLASS):
    changed = pyqtSignal()

    def __init__(self, iface, service_type, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        for m in range(1, 13):
            self.earthquake_max_intensity_greater_combo.addItem(str(m), m)

        self.iface = iface
        self.previous_map_tool = None
        self.extent_tool = None

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
        self.earthquake_max_intensity_greater_check.toggled.connect(self.changed)
        self.earthquake_max_intensity_greater_combo.currentIndexChanged.connect(self.changed)
        self.earthquake_number_mdps_greater_check.toggled.connect(self.changed)
        self.earthquake_number_mdps_greater_spin.valueChanged.connect(self.changed)
        self.radio_basic_output.toggled.connect(self.changed)
        self.radio_extended_output.toggled.connect(self.changed)

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
        self.radio_basic_output.toggled.connect(self._enable_widgets)
        self.radio_extended_output.toggled.connect(self._enable_widgets)
        self.earthquake_max_intensity_greater_check.toggled.connect(self._enable_widgets)
        self.earthquake_number_mdps_greater_check.toggled.connect(self._enable_widgets)
        self._enable_widgets()

        self.output_table_options_button.clicked.connect(self._output_table_options)
        self._populated_predined_areas()
        self.combo_predefined_area.currentIndexChanged.connect(self._use_predefined_area)
        self.radio_predefined_area.toggled.connect(self._use_predefined_area)

        self.service_type = None
        self.service_id = None
        self.set_service_type(service_type)
        self.output_fields = None

    def is_valid(self):
        return True

    def set_service_type(self, service_type):
        self.service_type = service_type

        self.time_coverage_group.setVisible(
            self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION))
        self.magnitude_group.setVisible(self.service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT))
        self.macroseismic_data_group.setVisible(self.service_type == SERVICE_MANAGER.MACROSEISMIC)

    def set_service_id(self, service_id):
        self.service_id = service_id

        service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

        if 'fields' in service_config['default']:
            self.output_fields = service_config['default']['fields']

        if not service_config['settings'].get('querycircular', False):
            if self.radio_circular_area.isChecked():
                self.radio_rectangular_area.setChecked(True)
            self.radio_circular_area.setEnabled(False)
        else:
            self.radio_circular_area.setEnabled(True)

        if not service_config['settings'].get('outputtext', False):
            if self.radio_basic_output.isChecked():
                self.radio_extended_output.setChecked(True)
            self.radio_basic_output.setEnabled(False)
        else:
            self.radio_basic_output.setEnabled(True)

        if not service_config['settings'].get('outputxml', False):
            if self.radio_extended_output.isChecked():
                self.radio_basic_output.setChecked(True)
            self.radio_extended_output.setEnabled(False)
        else:
            self.radio_extended_output.setEnabled(True)

    def restore_settings(self, prefix):
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
            self.earthquake_number_mdps_greater_spin.setValue(float(v))

        if not service_config or service_config['settings'].get('outputtext', False):
            self.radio_basic_output.setChecked(
                s.value('/plugins/qquake/{}_last_event_basic_checked'.format(prefix), True, bool))

        if not service_config or service_config['settings'].get('outputxml', False):
            self.radio_extended_output.setChecked(
                s.value('/plugins/qquake/{}_last_event_extended_checked'.format(prefix), False, bool))

    def save_settings(self, prefix):
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

        s.setValue('/plugins/qquake/{}_last_event_basic_checked'.format(prefix), self.radio_basic_output.isChecked())
        s.setValue('/plugins/qquake/{}_last_event_extended_checked'.format(prefix),
                   self.radio_extended_output.isChecked())

    def _populated_predined_areas(self):
        for name in SERVICE_MANAGER.available_predefined_bounding_boxes():
            extent = SERVICE_MANAGER.predefined_bounding_box(name)
            self.combo_predefined_area.addItem(extent['title'], name)

    def _use_predefined_area(self):
        if not self.radio_predefined_area.isChecked():
            return

        selected_extent_id = self.combo_predefined_area.currentData()
        extent = SERVICE_MANAGER.predefined_bounding_box(selected_extent_id)['boundingbox']
        self.lat_min_spinbox.setValue(extent[1])
        self.lat_max_spinbox.setValue(extent[3])
        self.long_min_spinbox.setValue(extent[0])
        self.long_max_spinbox.setValue(extent[2])
        self.lat_max_checkbox.setChecked(True)
        self.long_max_checkbox.setChecked(True)
        self.lat_min_checkbox.setChecked(True)
        self.long_min_checkbox.setChecked(True)

    def set_extent_from_canvas_extent(self, rect):
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

    def set_center_from_canvas_point(self, point):
        ct = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),
                                    QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        try:
            point = ct.transform(point)
            self.circular_lat_spinbox.setValue(point.y())
            self.circular_long_spinbox.setValue(point.x())
        except QgsCsException:
            pass

    def _enable_widgets(self):
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
                  self.circle_center_draw_on_map]:
            w.setEnabled(self.radio_circular_area.isChecked() and self.limit_extent_checkbox.isChecked())
        self.radius_min_spinbox.setEnabled(self.radius_min_spinbox.isEnabled() and self.radius_min_checkbox.isChecked())
        self.radius_max_spinbox.setEnabled(self.radius_max_spinbox.isEnabled() and self.radius_max_checkbox.isChecked())

        self.fdsn_event_start_date.setEnabled(self.min_time_check.isChecked())
        self.fdsn_event_end_date.setEnabled(self.max_time_check.isChecked())
        self.fdsn_event_min_magnitude.setEnabled(self.min_mag_check.isChecked())
        self.fdsn_event_max_magnitude.setEnabled(self.max_mag_check.isChecked())

        self.earthquake_max_intensity_greater_combo.setEnabled(self.earthquake_max_intensity_greater_check.isChecked())
        self.earthquake_number_mdps_greater_spin.setEnabled(self.earthquake_number_mdps_greater_check.isChecked())

        self.output_table_options_button.setEnabled(self.radio_extended_output.isChecked())

    def draw_rect_on_map(self):
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        if not self.extent_tool:
            self.extent_tool = QgsMapToolExtent(self.iface.mapCanvas())
            self.extent_tool.extentChanged.connect(self.extent_drawn)
            self.extent_tool.deactivated.connect(self.deactivate_tool)
        self.iface.mapCanvas().setMapTool(self.extent_tool)
        self.window().setVisible(False)

    def draw_center_on_map(self):
        self.previous_map_tool = self.iface.mapCanvas().mapTool()
        if not self.extent_tool:
            self.extent_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
            self.extent_tool.canvasClicked.connect(self.center_picked)
            self.extent_tool.deactivated.connect(self.deactivate_tool)
        self.iface.mapCanvas().setMapTool(self.extent_tool)
        self.window().setVisible(False)

    def extent_drawn(self, extent):
        self.set_extent_from_canvas_extent(extent)
        self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def center_picked(self, point, button):
        self.set_center_from_canvas_point(point)
        self.iface.mapCanvas().setMapTool(self.previous_map_tool)
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def deactivate_tool(self):
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def _refresh_date(self):
        """
        Avoids negative date intervals by checking start_date > end_date
        """

        if self.fdsn_event_start_date.dateTime() > self.fdsn_event_end_date.dateTime():
            self.fdsn_event_end_date.setDate(self.fdsn_event_start_date.date())

    def set_date_range_limits(self, date_start=None, date_end=None):
        if date_start:
            self.fdsn_event_start_date.setMinimumDateTime(date_start)
        else:
            self.fdsn_event_start_date.clearMinimumDate()

        if date_end:
            self.fdsn_event_start_date.setMaximumDateTime(date_end)
        else:
            self.fdsn_event_start_date.clearMaximumDate()

        if date_start:
            self.fdsn_event_start_date.setDateTime(date_start)

        if date_start:
            self.min_time_check.setText(
                self.tr("Start (from {})").format(date_start.toString('yyyy-MM-dd')))
        else:
            self.min_time_check.setText(self.tr("Start"))

        if date_end:
            self.max_time_check.setText(
                self.tr("End (until {})").format(date_end.toString('yyyy-MM-dd')))
        else:
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

    def set_current_date_range(self, date_start=None, date_end=None):
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
        self.radio_predefined_area.setChecked(True)
        self.combo_predefined_area.setCurrentIndex(self.combo_predefined_area.findData(box))

    def set_min_latitude(self, lat):
        self.radio_rectangular_area.setChecked(True)
        self.lat_min_spinbox.setValue(float(lat))

    def set_max_latitude(self, lat):
        self.radio_rectangular_area.setChecked(True)
        self.lat_max_spinbox.setValue(float(lat))

    def set_min_longitude(self, lat):
        self.radio_rectangular_area.setChecked(True)
        self.long_min_spinbox.setValue(float(lat))

    def set_max_longitude(self, lat):
        self.radio_rectangular_area.setChecked(True)
        self.long_max_spinbox.setValue(float(lat))

    def set_circle_longitude(self, lat):
        self.radio_circular_area.setChecked(True)
        self.circular_long_spinbox.setValue(float(lat))

    def set_circle_latitude(self, lat):
        self.radio_circular_area.setChecked(True)
        self.circular_lat_spinbox.setValue(float(lat))

    def set_min_circle_radius(self, radius):
        self.radius_min_checkbox.setChecked(True)
        self.radius_min_spinbox.setValue(float(radius))

    def set_max_circle_radius(self, radius):
        self.radius_max_checkbox.setChecked(True)
        self.radius_max_spinbox.setValue(float(radius))

    def set_min_magnitude(self, mag):
        self.min_mag_check.setChecked(mag is not None)
        if mag is not None:
            self.fdsn_event_min_magnitude.setValue(float(mag))

    def set_max_magnitude(self, mag):
        self.max_mag_check.setChecked(mag is not None)
        if mag is not None:
            self.fdsn_event_max_magnitude.setValue(float(mag))

    def set_max_intensity_greater(self, intensity):
        self.earthquake_max_intensity_greater_check.setChecked(intensity is not None)
        if intensity is not None:
            self.earthquake_max_intensity_greater_combo.setCurrentIndex(self.earthquake_max_intensity_greater_combo.findData(float(intensity)))

    def set_mdps_greater_than(self, mdps):
        self.earthquake_number_mdps_greater_check.setChecked(mdps is not None)
        if mdps is not None:
            self.earthquake_number_mdps_greater_spin.setValue(float(mdps))

    def set_extent_limit(self, box):
        self.long_min_spinbox.setMinimum(box[0])
        self.long_max_spinbox.setMinimum(box[0])
        self.lat_min_spinbox.setMinimum(box[1])
        self.lat_max_spinbox.setMinimum(box[1])
        self.long_min_spinbox.setMaximum(box[2])
        self.long_max_spinbox.setMaximum(box[2])
        self.lat_min_spinbox.setMaximum(box[3])
        self.lat_max_spinbox.setMaximum(box[3])

    def _output_table_options(self):
        dlg = OutputTableOptionsDialog(self.service_type, self.service_id, self.output_fields, self)
        if dlg.exec_():
            self.output_fields = dlg.selected_fields()
            self.changed.emit()

    def start_date(self):
        if self.service_type not in (
        SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION):
            return None

        return self.fdsn_event_start_date.dateTime() if self.min_time_check.isChecked() else None

    def end_date(self):
        if self.service_type not in (
        SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.FDSNSTATION):
            return None

        return self.fdsn_event_end_date.dateTime() if self.max_time_check.isChecked() else None

    def min_magnitude(self):
        if self.service_type not in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT):
            return None

        return self.fdsn_event_min_magnitude.value() if self.min_mag_check.isChecked() else None

    def max_magnitude(self):
        if self.service_type not in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNEVENT):
            return None

        return self.fdsn_event_max_magnitude.value() if self.max_mag_check.isChecked() else None

    def extent_rect(self):
        return self.limit_extent_checkbox.isChecked() and (self.radio_rectangular_area.isChecked() or
                                                           self.radio_predefined_area.isChecked())

    def min_latitude(self):
        return self.lat_min_spinbox.value() if self.lat_min_checkbox.isChecked() else None

    def max_latitude(self):
        return self.lat_max_spinbox.value() if self.lat_max_checkbox.isChecked() else None

    def min_longitude(self):
        return self.long_min_spinbox.value() if self.long_min_checkbox.isChecked() else None

    def max_longitude(self):
        return self.long_max_spinbox.value() if self.long_max_checkbox.isChecked() else None

    def limit_extent_circle(self):
        return self.limit_extent_checkbox.isChecked() and self.radio_circular_area.isChecked()

    def circle_latitude(self):
        return self.circular_lat_spinbox.value()

    def circle_longitude(self):
        return self.circular_long_spinbox.value()

    def circle_min_radius(self):
        return self.radius_min_spinbox.value() if self.radius_min_checkbox.isChecked() else None

    def circle_max_radius(self):
        return self.radius_max_spinbox.value() if self.radius_max_checkbox.isChecked() else None

    def earthquake_max_intensity_greater(self):
        if self.service_type != SERVICE_MANAGER.MACROSEISMIC:
            return None
        return self.earthquake_max_intensity_greater_combo.currentData() if self.earthquake_max_intensity_greater_check.isChecked() else None

    def earthquake_number_mdps_greater(self):
        if self.service_type != SERVICE_MANAGER.MACROSEISMIC:
            return None

        return self.earthquake_number_mdps_greater_spin.value() if self.earthquake_number_mdps_greater_check.isChecked() else None

    def output_type(self):
        return Fetcher.BASIC if self.radio_basic_output.isChecked() else Fetcher.EXTENDED

    def to_service_definition(self):
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
                     'macromdpsgreaterthan': self.earthquake_number_mdps_greater()
                     }.items():
            if v:
                defaults[k] = v
            elif k in defaults:
                del defaults[k]

        base_config['default'] = defaults
        return base_config
