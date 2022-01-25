# -*- coding: utf-8 -*-
# pylint:disable=too-many-lines
"""
The main plugin dialog
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

from typing import Optional, Union

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QDateTime,
    QDir,
    QItemSelectionModel
)
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel
)
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QSizePolicy,
    QVBoxLayout,
    QMenu,
    QAction,
    QMessageBox,
    QInputDialog,
    QFileDialog
)
from qgis.core import (
    Qgis,
    QgsProject,
    QgsSettings,
    QgsFileUtils
)
from qgis.gui import (
    QgsGui,
    QgsMessageBar,
    QgsNewNameDialog
)

from qquake.fetcher import Fetcher
from qquake.gui.base_filter_widget import BaseFilterWidget
from qquake.gui.fetch_by_url_widget import FetchByUrlWidget
from qquake.gui.filter_by_id_widget import FilterByIdWidget
from qquake.gui.filter_parameter_widget import FilterParameterWidget
from qquake.gui.filter_station_by_id_widget import FilterStationByIdWidget
from qquake.gui.gui_utils import GuiUtils
from qquake.gui.ogc_service_options_widget import OgcServiceWidget
from qquake.gui.service_configuration_widget import ServiceConfigurationDialog
from qquake.gui.service_information_widget import ServiceInformationWidget
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('qquake_dialog_base.ui'))


class QQuakeDialog(QDialog, FORM_CLASS):
    """
    The main plugin dialog
    """

    def __init__(self, iface, parent=None):  # pylint:disable=too-many-statements
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.setObjectName('QQuakeDialog')
        QgsGui.enableAutoGeometryRestore(self)

        self.splitter.setStretchFactor(0, 0)
        self.splitter_2.setStretchFactor(0, 0)
        self.splitter_3.setStretchFactor(0, 0)
        self.splitter_4.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter_2.setStretchFactor(1, 1)
        self.splitter_3.setStretchFactor(1, 1)
        self.splitter_4.setStretchFactor(1, 1)

        self.fdsn_event_filter = FilterParameterWidget(iface, SERVICE_MANAGER.FDSNEVENT)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.fdsn_event_filter)
        self.fdsn_event_filter_container.setLayout(vl)
        self.earthquake_service_info_widget = ServiceInformationWidget(iface)
        self.fdsn_by_id_filter = FilterByIdWidget(iface, SERVICE_MANAGER.FDSNEVENT)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.fdsn_by_id_filter)
        self.fdsn_by_id_container.setLayout(vl)
        self.fdsn_by_url_widget = FetchByUrlWidget(iface, SERVICE_MANAGER.FDSNEVENT)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.fdsn_by_url_widget)
        self.fdsn_by_url_container.setLayout(vl)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.earthquake_service_info_widget)
        self.earthquake_service_info_container.setLayout(vl)

        self.macro_filter = FilterParameterWidget(iface, SERVICE_MANAGER.MACROSEISMIC)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_filter)
        self.macro_filter_container.setLayout(vl)
        self.macro_by_id_filter = FilterByIdWidget(iface, SERVICE_MANAGER.MACROSEISMIC)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_by_id_filter)
        self.macro_by_id_container.setLayout(vl)
        self.macro_by_url_widget = FetchByUrlWidget(iface, SERVICE_MANAGER.MACROSEISMIC)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_by_url_widget)
        self.macro_by_url_container.setLayout(vl)
        self.macro_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_service_info_widget)
        self.macro_service_info_container.setLayout(vl)

        self.station_filter = FilterParameterWidget(iface, SERVICE_MANAGER.FDSNSTATION)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_filter)
        self.station_filter_container.setLayout(vl)
        self.station_by_id_filter = FilterStationByIdWidget(iface, SERVICE_MANAGER.FDSNSTATION)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_by_id_filter)
        self.station_by_id_container.setLayout(vl)
        self.station_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_service_info_widget)
        self.station_service_info_container.setLayout(vl)

        self.station_by_url_widget = FetchByUrlWidget(iface, SERVICE_MANAGER.FDSNSTATION)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_by_url_widget)
        self.station_by_url_container.setLayout(vl)

        self.ogc_service_widget = OgcServiceWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.ogc_service_widget)
        self.ogc_widget_container.setLayout(vl)
        self.ogc_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.ogc_service_info_widget)
        self.ogc_service_info_container.setLayout(vl)

        self.message_bar = QgsMessageBar()
        self.message_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.verticalLayout.insertWidget(0, self.message_bar)

        self.fdsn_event_url_text_browser.viewport().setAutoFillBackground(False)
        self.fdsn_macro_url_text_browser.viewport().setAutoFillBackground(False)
        self.fdsn_station_url_text_browser.viewport().setAutoFillBackground(False)

        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetch Data'))
        self.button_box.rejected.connect(self._save_settings)

        self.iface = iface

        # OGC
        self.ogc_combo.addItem(self.tr('Web Map Services (WMS)'), SERVICE_MANAGER.WMS)
        self.ogc_combo.addItem(self.tr('Web Feature Services (WFS)'), SERVICE_MANAGER.WFS)
        self.ogc_combo.addItem(self.tr('Web Coverage Services (WCS)'), SERVICE_MANAGER.WCS)
        self.ogc_combo.currentIndexChanged.connect(self.refreshOgcWidgets)

        self.ogc_list_model = QStandardItemModel(self.ogc_list)
        self.ogc_list.setModel(self.ogc_list_model)
        self.ogc_list.selectionModel().selectionChanged.connect(
            self._ogc_service_changed)

        self._refresh_services()
        SERVICE_MANAGER.refreshed.connect(self._refresh_services)

        # connect to refreshing function to refresh the UI depending on the WS
        self._refresh_fdsnevent_widgets()
        self.refreshFdsnMacroseismicWidgets()
        self.refreshFdsnStationWidgets()

        # change the UI parameter according to the web service chosen
        self.fdsn_event_list.currentRowChanged.connect(
            self._refresh_fdsnevent_widgets)
        self.fdsn_macro_list.currentRowChanged.connect(
            self.refreshFdsnMacroseismicWidgets)
        self.fdsn_station_list.currentRowChanged.connect(
            self.refreshFdsnStationWidgets)

        self.fdsn_event_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNEVENT))
        self.fdsn_by_id_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNEVENT))
        self.fdsn_by_url_widget.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNEVENT))
        self.fdsn_event_list.currentRowChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNEVENT))
        self.macro_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.MACROSEISMIC))
        self.macro_by_id_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.MACROSEISMIC))
        self.macro_by_url_widget.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.MACROSEISMIC))
        self.fdsn_macro_list.currentRowChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.MACROSEISMIC))
        self.station_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNSTATION))
        self.station_by_id_filter.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNSTATION))
        self.fdsn_station_list.currentRowChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNSTATION))
        self.station_by_url_widget.changed.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNSTATION))

        self.button_box.accepted.connect(self._getEventList)

        self.service_tab_widget.currentChanged.connect(lambda: self._refresh_url(None))

        self.fetcher = None

        QgsGui.enableAutoGeometryRestore(self)

        self.fdsn_tab_widget.currentChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNEVENT))
        self.macro_tab_widget.currentChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.MACROSEISMIC))
        self.fdsnstation_tab_widget.currentChanged.connect(lambda: self._refresh_url(SERVICE_MANAGER.FDSNSTATION))

        for b in [self.button_fdsn_new_service, self.button_macro_new_service,
                  self.button_station_new_service, self.button_ogc_new_service]:
            self._build_add_service_menu(b)

        for b in [self.button_fdsn_edit_service, self.button_macro_edit_service,
                  self.button_station_edit_service, self.button_ogc_edit_service]:
            b.clicked.connect(self._edit_service)

        for b in [self.button_fdsn_rename_service, self.button_macro_rename_service,
                  self.button_station_rename_service, self.button_ogc_rename_service]:
            b.clicked.connect(self._rename_service)

        for b in [self.button_fdsn_remove_service, self.button_macro_remove_service,
                  self.button_station_remove_service, self.button_ogc_remove_service]:
            b.clicked.connect(self._remove_service)

        for b in [self.button_fdsn_export_service, self.button_macro_export_service,
                  self.button_station_export_service, self.button_ogc_export_service]:
            b.clicked.connect(self._export_service)

        self._restore_settings()
        self._refresh_url(SERVICE_MANAGER.FDSNEVENT)
        self._refresh_url(SERVICE_MANAGER.MACROSEISMIC)
        self._refresh_url(SERVICE_MANAGER.FDSNSTATION)

    def closeEvent(self, e):  # pylint: disable=missing-function-docstring
        self._save_settings()
        super().closeEvent(e)

    def _build_add_service_menu(self, widget):
        """
        Builds the add service menu for a specific widget
        """
        menu = QMenu()
        save_action = QAction(self.tr('Save Current Configuration As…'), parent=menu)
        save_action.setObjectName('save_action')
        menu.addAction(save_action)
        save_action.triggered.connect(self._save_configuration)

        import_action = QAction(self.tr('Import from File…'), parent=menu)
        menu.addAction(import_action)
        import_action.triggered.connect(self._import_configuration)

        create_new_action = QAction(self.tr('Create New Service…'), parent=menu)
        menu.addAction(create_new_action)
        create_new_action.triggered.connect(self._create_configuration)

        menu.aboutToShow.connect(lambda: self._menu_about_to_show(menu))
        widget.setMenu(menu)

    def _menu_about_to_show(self, menu):
        """
        Triggered when the Add Service menu is about to show
        """
        save_current_action = menu.findChild(QAction, 'save_action')

        service_type = self.get_current_service_type()
        filter_widget = self.get_service_filter_widget(service_type)

        save_current_action.setEnabled(hasattr(filter_widget, 'to_service_definition'))

    def _refresh_services(self):
        """
        Refreshes the list of available services
        """

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_event_list.clear()
        self.fdsn_event_list.addItems(SERVICE_MANAGER.available_services(SERVICE_MANAGER.FDSNEVENT))
        self.fdsn_event_list.setCurrentRow(0)

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_macro_list.clear()
        self.fdsn_macro_list.addItems(SERVICE_MANAGER.available_services(SERVICE_MANAGER.MACROSEISMIC))
        self.fdsn_macro_list.setCurrentRow(0)

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_station_list.clear()
        self.fdsn_station_list.addItems(SERVICE_MANAGER.available_services(SERVICE_MANAGER.FDSNSTATION))
        self.fdsn_station_list.setCurrentRow(0)

        self.refreshOgcWidgets()

    def _save_configuration(self):
        """
        Triggers saving the current service configuration
        """
        service_type = self.get_current_service_type()
        name, ok = QInputDialog.getText(self, self.tr('Save Service Configuration'),
                                        self.tr('Save the current service configuration as'))
        if not name or not ok:
            return

        filter_widget = self.get_service_filter_widget(service_type)
        SERVICE_MANAGER.save_service(service_type, name, filter_widget.to_service_definition())
        self.set_current_service(service_type, name)

    def _save_settings(self):
        """
        Saves all settings currently defined in the dialog
        """
        s = QgsSettings()
        s.setValue('/plugins/qquake/last_tab', self.service_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/fdsn_event_last_event_service', self.fdsn_event_list.currentItem().text())
        s.setValue('/plugins/qquake/macro_last_event_service', self.fdsn_macro_list.currentItem().text())

        s.setValue('/plugins/qquake/fdsnevent_last_tab', self.fdsn_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/macro_last_tab', self.macro_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/station_last_tab', self.fdsnstation_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/ogc_last_tab', self.ogc_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/ogc_last_service_type', self.ogc_combo.currentIndex())

        self.fdsn_event_filter.save_settings('fdsn_event')
        self.fdsn_by_id_filter.save_settings('fdsn_event')
        self.fdsn_by_url_widget.save_settings('fdsn_event')
        self.macro_filter.save_settings('macro')
        self.macro_by_id_filter.save_settings('macro')
        self.macro_by_url_widget.save_settings('macro')
        self.station_filter.save_settings('stations')
        self.station_by_id_filter.save_settings('stations')
        self.station_by_url_widget.save_settings('stations')
        self.ogc_service_widget.save_settings()

    def _restore_settings(self):
        """
        Restores dialog settings
        """
        s = QgsSettings()

        last_tab = s.value('/plugins/qquake/last_tab')
        if last_tab is not None:
            self.service_tab_widget.setCurrentIndex(int(last_tab))

        last_service = s.value('/plugins/qquake/fdsn_event_last_event_service')
        if last_service is not None:
            try:
                self.fdsn_event_list.setCurrentItem(
                    self.fdsn_event_list.findItems(last_service, Qt.MatchContains)[0])
            except IndexError:
                pass

        last_service = s.value('/plugins/qquake/macro_last_event_service')
        if last_service is not None:
            self.fdsn_macro_list.setCurrentItem(
                self.fdsn_macro_list.findItems(last_service, Qt.MatchContains)[0])

        self.fdsn_event_filter.restore_settings('fdsn_event')
        self.fdsn_by_id_filter.restore_settings('fdsn_event')
        self.fdsn_by_url_widget.restore_settings('fdsn_event')
        self.macro_filter.restore_settings('macro')
        self.macro_by_id_filter.restore_settings('macro')
        self.macro_by_url_widget.restore_settings('fdsn_event')
        self.station_filter.restore_settings('stations')
        self.station_by_id_filter.restore_settings('stations')
        self.station_by_url_widget.restore_settings('stations')
        self.ogc_service_widget.restore_settings()

        self.fdsn_tab_widget.setCurrentIndex(s.value('/plugins/qquake/fdsnevent_last_tab', 0, int))
        self.macro_tab_widget.setCurrentIndex(s.value('/plugins/qquake/macro_last_tab', 0, int))
        self.fdsnstation_tab_widget.setCurrentIndex(s.value('/plugins/qquake/station_last_tab', 0, int))
        self.ogc_tab_widget.setCurrentIndex(s.value('/plugins/qquake/ogc_last_tab', 0, int))
        self.ogc_combo.setCurrentIndex(s.value('/plugins/qquake/ogc_last_service_type', 0, int))

    def get_current_service_id(self, service_type: str) -> Optional[str]:
        """
        Returns the current selected service id
        """
        if service_type == SERVICE_MANAGER.FDSNEVENT:
            service_id = self.fdsn_event_list.currentItem().text() if self.fdsn_event_list.currentItem() else None
        elif service_type == SERVICE_MANAGER.MACROSEISMIC:
            service_id = self.fdsn_macro_list.currentItem().text() if self.fdsn_macro_list.currentItem() else None
        elif service_type == SERVICE_MANAGER.FDSNSTATION:
            service_id = self.fdsn_station_list.currentItem().text() if self.fdsn_station_list.currentItem() else None
        elif service_type in (SERVICE_MANAGER.WMS, SERVICE_MANAGER.WFS, SERVICE_MANAGER.WCS):
            service_id = self.ogc_list.selectionModel().selectedIndexes()[
                0].data() if self.ogc_list.selectionModel().selectedIndexes() else None
        else:
            service_id = None

        return service_id

    def get_current_service_type(self) -> Optional[str]:
        """
        Returns the current service type
        """
        if self.service_tab_widget.currentIndex() == 0:
            service_type = SERVICE_MANAGER.FDSNEVENT
        elif self.service_tab_widget.currentIndex() == 1:
            service_type = SERVICE_MANAGER.MACROSEISMIC
        elif self.service_tab_widget.currentIndex() == 2:
            service_type = SERVICE_MANAGER.FDSNSTATION
        elif self.service_tab_widget.currentIndex() == 3:
            return self.ogc_combo.currentData()
        else:
            service_type = None
        return service_type

    def get_service_filter_widget(self,  # pylint:disable=too-many-branches
                                  service_type: str) -> Optional[
        Union[BaseFilterWidget, OgcServiceWidget]]:
        """
        Returns the service filter widget for a specific service type
        """
        widget = None
        if service_type == SERVICE_MANAGER.FDSNEVENT:
            if self.fdsn_tab_widget.currentIndex() in (0, 3):
                widget = self.fdsn_event_filter
            elif self.fdsn_tab_widget.currentIndex() == 1:
                widget = self.fdsn_by_id_filter
            elif self.fdsn_tab_widget.currentIndex() == 2:
                widget = self.fdsn_by_url_widget
        elif service_type == SERVICE_MANAGER.MACROSEISMIC:
            if self.macro_tab_widget.currentIndex() in (0, 3):
                widget = self.macro_filter
            elif self.macro_tab_widget.currentIndex() == 1:
                widget = self.macro_by_id_filter
            elif self.macro_tab_widget.currentIndex() == 2:
                widget = self.macro_by_url_widget
        elif service_type == SERVICE_MANAGER.FDSNSTATION:
            if self.fdsnstation_tab_widget.currentIndex() in (0, 3):
                widget = self.station_filter
            elif self.fdsnstation_tab_widget.currentIndex() == 1:
                widget = self.station_by_id_filter
            elif self.fdsnstation_tab_widget.currentIndex() == 2:
                widget = self.station_by_url_widget
        elif service_type in (SERVICE_MANAGER.WMS, SERVICE_MANAGER.WFS, SERVICE_MANAGER.WCS):
            widget = self.ogc_service_widget
        return widget

    def get_fetcher(self,
                    service_type: Optional[str] = None,
                    split_strategy: Optional[str] = None):
        """
        Returns a quake fetcher corresponding to the current dialog settings
        """

        if service_type is None:
            service_type = self.get_current_service_type()

        service = self.get_current_service_id(service_type)
        if not service:
            return None

        filter_widget = self.get_service_filter_widget(service_type)

        service_config = SERVICE_MANAGER.service_details(service_type, service)

        if isinstance(filter_widget, FilterParameterWidget):
            fetcher = Fetcher(service_type=service_type,
                              event_service=service,
                              event_start_date=filter_widget.start_date(),
                              event_end_date=filter_widget.end_date(),
                              event_min_magnitude=filter_widget.min_magnitude(),
                              event_max_magnitude=filter_widget.max_magnitude(),
                              limit_extent_rect=filter_widget.extent_rect(),
                              min_latitude=filter_widget.min_latitude(),
                              max_latitude=filter_widget.max_latitude(),
                              min_longitude=filter_widget.min_longitude(),
                              max_longitude=filter_widget.max_longitude(),
                              limit_extent_circle=filter_widget.limit_extent_circle(),
                              circle_latitude=filter_widget.circle_latitude(),
                              circle_longitude=filter_widget.circle_longitude(),
                              circle_min_radius=filter_widget.circle_min_radius(),
                              circle_max_radius=filter_widget.circle_max_radius(),
                              circle_radius_unit=filter_widget.circle_radius_unit(),
                              earthquake_number_mdps_greater=filter_widget.earthquake_number_mdps_greater(),
                              earthquake_max_intensity_greater=filter_widget.earthquake_max_intensity_greater(),
                              output_fields=filter_widget.output_fields(),
                              output_type=filter_widget.output_type(),
                              convert_negative_depths=filter_widget.convert_negative_depths(),
                              depth_unit=filter_widget.depth_unit(),
                              event_type=filter_widget.event_type(),
                              updated_after=filter_widget.updated_after(),
                              split_strategy=split_strategy,
                              styles=filter_widget.selected_styles()
                              )
        elif isinstance(filter_widget, FilterByIdWidget):
            if not service_config['settings'].get('queryeventid'):
                fetcher = None
            else:
                fetcher = Fetcher(service_type=service_type,
                                  event_service=service,
                                  event_ids=filter_widget.ids(),
                                  contributor_id=filter_widget.contributor_id(),
                                  output_fields=filter_widget.output_fields(),
                                  output_type=filter_widget.output_type(),
                                  convert_negative_depths=filter_widget.convert_negative_depths(),
                                  depth_unit=filter_widget.depth_unit(),
                                  styles=filter_widget.selected_styles()
                                  )
        elif isinstance(filter_widget, FetchByUrlWidget):
            fetcher = Fetcher(service_type=service_type,
                              event_service=service,
                              url=filter_widget.url(),
                              output_fields=filter_widget.output_fields(),
                              output_type=filter_widget.output_type(),
                              convert_negative_depths=filter_widget.convert_negative_depths(),
                              depth_unit=filter_widget.depth_unit(),
                              styles=filter_widget.selected_styles()
                              )
        elif isinstance(filter_widget, FilterStationByIdWidget):
            fetcher = Fetcher(service_type=service_type,
                              event_service=service,
                              network_codes=filter_widget.network_codes(),
                              station_codes=filter_widget.station_codes(),
                              locations=filter_widget.locations(),
                              output_fields=filter_widget.output_fields(),
                              output_type=filter_widget.output_type(),
                              convert_negative_depths=filter_widget.convert_negative_depths(),
                              depth_unit=filter_widget.depth_unit(),
                              styles=filter_widget.selected_styles()
                              )
        return fetcher

    def _refresh_url(self, service_type: Optional[str] = None):
        """
        Updates the service URL
        """
        if not service_type:
            service_type = self.get_current_service_type()
            if service_type is None:
                self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
                return

            if service_type not in (
                    SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNSTATION):
                self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
                return

        fetcher = self.get_fetcher(service_type)
        if not fetcher:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
            return

        self._valid_changed()

        if service_type == SERVICE_MANAGER.FDSNEVENT:
            self.fdsn_event_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))
        elif service_type == SERVICE_MANAGER.MACROSEISMIC:
            self.fdsn_macro_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))
        elif service_type == SERVICE_MANAGER.FDSNSTATION:
            self.fdsn_station_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))

    def _valid_changed(self):
        """
        Called when dialog entry validation should occur
        """
        service_type = self.get_current_service_type()
        if service_type not in (
                SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNSTATION):
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            return

        filter_widget = self.get_service_filter_widget(service_type)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(filter_widget.is_valid())

    def _update_service_widgets(self,  # pylint: disable=too-many-locals,too-many-branches
                                service_type, service_id, filter_widget, filter_by_id_widget, fetch_by_url_widget,
                                info_widget,
                                remove_service_button, edit_service_button, rename_service_button, tab_widget):
        """
        Updates all widgets to reflect the current service details
        """
        service_config = SERVICE_MANAGER.service_details(service_type, service_id)

        date_start = QDateTime.fromString(
            service_config['datestart'],
            Qt.ISODate
        )
        default_date_start = QDateTime.fromString(
            service_config['default']['datestart'],
            Qt.ISODate
        ) if service_config['default'].get('datestart') else None

        # if the dateend is not set in the config.json set the date to NOW
        date_end = QDateTime.fromString(
            service_config['dateend'],
            Qt.ISODate
        ) if 'dateend' in service_config and service_config['dateend'] else None

        default_date_end = QDateTime.fromString(
            service_config['default']['dateend'],
            Qt.ISODate
        ) if service_config['default'].get('dateend') else None

        filter_widget.set_date_range_limits(date_start, date_end)
        filter_widget.set_current_date_range(default_date_start, default_date_end)

        if service_config['default'].get('boundingboxpredefined'):
            filter_widget.set_predefined_bounding_box(service_config['default'].get('boundingboxpredefined'))
        if service_config['default'].get('minimumlatitude'):
            filter_widget.set_min_latitude(service_config['default'].get('minimumlatitude'))
        if service_config['default'].get('maximumlatitude'):
            filter_widget.set_max_latitude(service_config['default'].get('maximumlatitude'))
        if service_config['default'].get('minimumlongitude'):
            filter_widget.set_min_longitude(service_config['default'].get('minimumlongitude'))
        if service_config['default'].get('maximumlongitude'):
            filter_widget.set_max_longitude(service_config['default'].get('maximumlongitude'))
        if service_config['default'].get('circlelatitude'):
            filter_widget.set_circle_latitude(service_config['default'].get('circlelatitude'))
        if service_config['default'].get('circlelongitude'):
            filter_widget.set_circle_longitude(service_config['default'].get('circlelongitude'))
        if service_config['default'].get('minimumcircleradius'):
            filter_widget.set_min_circle_radius(service_config['default'].get('minimumcircleradius'))
        if service_config['default'].get('maximumcircleradius'):
            filter_widget.set_max_circle_radius(service_config['default'].get('maximumcircleradius'))
        if service_config['default'].get('minimummagnitude'):
            filter_widget.set_min_magnitude(service_config['default'].get('minimummagnitude'))
        if service_config['default'].get('maximummagnitude'):
            filter_widget.set_max_magnitude(service_config['default'].get('maximummagnitude'))
        if service_config['default'].get('macromaxintensitygreater'):
            filter_widget.set_max_intensity_greater(service_config['default'].get('macromaxintensitygreater'))
        if service_config['default'].get('macromdpsgreaterthan'):
            filter_widget.set_mdps_greater_than(service_config['default'].get('macromdpsgreaterthan'))
        if service_config['default'].get('eventtype'):
            filter_widget.set_event_type(service_config['default'].get('eventtype'))
        updated_after = QDateTime.fromString(
            service_config['default']['updatedafter'],
            Qt.ISODate
        ) if service_config['default'].get('updatedafter') else None
        if updated_after:
            filter_widget.set_updated_after(updated_after)

        filter_widget.set_extent_limit(service_config.get('boundingbox', [-180, -90, 180, 90]))

        if service_type in [SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC]:
            tab_widget.widget(1).setEnabled(service_config['settings'].get('queryeventid', False))

        info_widget.set_service(service_type=service_type, service_id=service_id)

        filter_widget.set_service_id(service_id)
        filter_by_id_widget.set_service_id(service_id)
        if fetch_by_url_widget is not None:
            fetch_by_url_widget.set_service_id(service_id)

        remove_service_button.setEnabled(not service_config['read_only'])
        edit_service_button.setEnabled(not service_config['read_only'])
        rename_service_button.setEnabled(not service_config['read_only'])

    def _refresh_fdsnevent_widgets(self):
        """
        Refreshing the FDSN-Event UI depending on the WS chosen
        """
        if not self.fdsn_event_list.currentItem():
            return

        service_id = self.fdsn_event_list.currentItem().text()
        self._update_service_widgets(service_type=SERVICE_MANAGER.FDSNEVENT, service_id=service_id,
                                     filter_widget=self.fdsn_event_filter,
                                     filter_by_id_widget=self.fdsn_by_id_filter,
                                     fetch_by_url_widget=self.fdsn_by_url_widget,
                                     info_widget=self.earthquake_service_info_widget,
                                     remove_service_button=self.button_fdsn_remove_service,
                                     edit_service_button=self.button_fdsn_edit_service,
                                     rename_service_button=self.button_fdsn_rename_service,
                                     tab_widget=self.fdsn_tab_widget)

    def refreshFdsnMacroseismicWidgets(self):
        """
        Refreshing the FDSN-Macroseismic UI depending on the WS chosen
        """
        if not self.fdsn_macro_list.currentItem():
            return

        service_id = self.fdsn_macro_list.currentItem().text()
        self._update_service_widgets(service_type=SERVICE_MANAGER.MACROSEISMIC, service_id=service_id,
                                     filter_widget=self.macro_filter,
                                     filter_by_id_widget=self.macro_by_id_filter,
                                     fetch_by_url_widget=self.macro_by_url_widget,
                                     info_widget=self.macro_service_info_widget,
                                     remove_service_button=self.button_macro_remove_service,
                                     edit_service_button=self.button_macro_edit_service,
                                     rename_service_button=self.button_macro_rename_service,
                                     tab_widget=self.macro_tab_widget)

    def refreshFdsnStationWidgets(self):
        """
        Refreshing the FDSN-Macroseismic UI depending on the WS chosen
        """
        if not self.fdsn_station_list.currentItem():
            return

        service_id = self.fdsn_station_list.currentItem().text()
        self._update_service_widgets(service_type=SERVICE_MANAGER.FDSNSTATION, service_id=service_id,
                                     filter_by_id_widget=self.station_by_id_filter,
                                     fetch_by_url_widget=self.station_by_url_widget,
                                     filter_widget=self.station_filter, info_widget=self.station_service_info_widget,
                                     remove_service_button=self.button_station_remove_service,
                                     edit_service_button=self.button_station_edit_service,
                                     rename_service_button=self.button_station_rename_service,
                                     tab_widget=self.fdsnstation_tab_widget)

    def refreshOgcWidgets(self):
        """
        read the ogc_combo and fill it with the services
        """
        self.ogc_list_model.clear()
        ogc_selection = self.ogc_combo.currentData()

        services = SERVICE_MANAGER.available_services(ogc_selection)

        group_items = {}

        for service in services:
            service_config = SERVICE_MANAGER.service_details(ogc_selection, service)
            group = service_config.get('group')
            if not group or group in group_items:
                continue

            group_item = QStandardItem(group)
            group_item.setFlags(Qt.ItemIsEnabled)
            self.ogc_list_model.appendRow([group_item])
            group_items[group] = group_item

        first_item = None
        for service in services:
            item = QStandardItem(service)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setData(service, role=Qt.UserRole)
            if not first_item:
                first_item = item

            service_config = SERVICE_MANAGER.service_details(ogc_selection, service)
            group = service_config.get('group')
            if group:
                parent = group_items[group]
                parent.appendRow([item])
            else:
                self.ogc_list_model.appendRow([item])

        self.ogc_list.expandAll()
        first_item_index = self.ogc_list_model.indexFromItem(first_item)
        self.ogc_list.selectionModel().select(first_item_index, QItemSelectionModel.ClearAndSelect)

        service_config = SERVICE_MANAGER.service_details(ogc_selection, self.get_current_service_id(ogc_selection))
        self.button_ogc_edit_service.setEnabled(not service_config['read_only'])
        self.button_ogc_rename_service.setEnabled(not service_config['read_only'])
        self.button_ogc_remove_service.setEnabled(not service_config['read_only'])

    def _ogc_service_changed(self, _, __):
        """
        Triggered when the current OGC service changes
        """
        if not self.ogc_list.selectionModel().selectedIndexes():
            return

        current_service = self.ogc_list.selectionModel().selectedIndexes()[0].data(Qt.UserRole)
        if not current_service:
            return

        self.ogc_service_widget.set_service(service_type=self.ogc_combo.currentData(),
                                            service_id=current_service)

        self.ogc_service_info_widget.set_service(service_type=self.ogc_combo.currentData(),
                                                 service_id=current_service)

        service_config = SERVICE_MANAGER.service_details(self.ogc_combo.currentData(),
                                                         current_service)
        self.button_ogc_edit_service.setEnabled(not service_config['read_only'])
        self.button_ogc_rename_service.setEnabled(not service_config['read_only'])
        self.button_ogc_remove_service.setEnabled(not service_config['read_only'])

    def _remove_service(self):
        """
        Removes the current service
        """
        service_type = self.get_current_service_type()
        service_id = self.get_current_service_id(service_type)
        if QMessageBox.question(self, self.tr('Remove Service'),
                                self.tr('Are you sure you want to remove "{}"?'.format(service_id))) != QMessageBox.Yes:
            return

        SERVICE_MANAGER.remove_service(service_type, service_id)

    def _edit_service(self):
        """
        Edits the current service
        """
        service_type = self.get_current_service_type()
        service_id = self.get_current_service_id(service_type)

        config_dialog = ServiceConfigurationDialog(self.iface, service_type, service_id, self)
        if config_dialog.exec_():
            self.set_current_service(service_type, service_id)

    def _rename_service(self):
        """
        Renames the current service
        """
        service_type = self.get_current_service_type()
        service_id = self.get_current_service_id(service_type)

        dlg = QgsNewNameDialog(service_id, service_id, [], existing=SERVICE_MANAGER.available_services(service_type))
        dlg.setHintString(self.tr('Rename service configuration to'))
        dlg.setWindowTitle(self.tr('Rename Service Configuration'))
        dlg.setOverwriteEnabled(False)
        dlg.setConflictingNameWarning(self.tr('A configuration with this name already exists'))
        if not dlg.exec_():
            return

        new_name = dlg.name()
        SERVICE_MANAGER.rename_service(service_type, service_id, new_name)
        self.set_current_service(service_type, new_name)

    def set_current_service(self, service_type: str, service_id: str):
        """
        Sets the current service
        """
        if service_type == SERVICE_MANAGER.FDSNEVENT:
            self.fdsn_event_list.setCurrentItem(self.fdsn_event_list.findItems(service_id, Qt.MatchContains)[0])
        elif service_type == SERVICE_MANAGER.MACROSEISMIC:
            self.fdsn_macro_list.setCurrentItem(self.fdsn_macro_list.findItems(service_id, Qt.MatchContains)[0])
        elif service_type == SERVICE_MANAGER.FDSNSTATION:
            self.fdsn_station_list.setCurrentItem(self.fdsn_station_list.findItems(service_id, Qt.MatchContains)[0])
        elif service_type in (SERVICE_MANAGER.WMS, SERVICE_MANAGER.WFS, SERVICE_MANAGER.WCS):
            self.ogc_combo.setCurrentIndex(self.ogc_combo.findData(service_type))

            indexes = self.ogc_list_model.match(self.ogc_list_model.index(0, 0), Qt.UserRole, service_id,
                                                flags=Qt.MatchExactly | Qt.MatchRecursive)
            if len(indexes) > 0:
                self.ogc_list.selectionModel().select(indexes[0], QItemSelectionModel.ClearAndSelect)

    def _create_configuration(self):
        """
        Creates a new service configuration
        """
        service_type = self.get_current_service_type()
        dlg = QgsNewNameDialog('', '', [], existing=SERVICE_MANAGER.available_services(service_type))
        dlg.setHintString(self.tr('Create a new service configuration named'))
        dlg.setWindowTitle(self.tr('New Service Configuration'))
        dlg.setOverwriteEnabled(False)
        dlg.setConflictingNameWarning(self.tr('A configuration with this name already exists'))
        if not dlg.exec_():
            return

        name = dlg.name()
        config_dialog = ServiceConfigurationDialog(self.iface, service_type, name, self)
        if config_dialog.exec_():
            self.set_current_service(service_type, name)

    def _export_service(self):
        """
        Triggers exporting a service configuration
        """
        service_type = self.get_current_service_type()
        service_id = self.get_current_service_id(service_type)
        file, _ = QFileDialog.getSaveFileName(self, self.tr('Export Service'),
                                              QDir.homePath() + '/{}.json'.format(service_id), 'JSON Files (*.json)')
        if not file:
            return

        file = QgsFileUtils.ensureFileNameHasExtension(file, ['json'])

        if SERVICE_MANAGER.export_service(service_type, service_id, file):
            self.message_bar.pushMessage(
                self.tr("Service exported"), Qgis.Success, 5)
        else:
            self.message_bar.pushMessage(
                self.tr("An error occurred while exporting service"), Qgis.Critical, 5)

    def _import_configuration(self):
        """
        Triggers importing a configuration
        """
        file, _ = QFileDialog.getOpenFileName(self, self.tr('Import Service'), QDir.homePath(), 'JSON Files (*.json)')
        if not file:
            return

        res, err = SERVICE_MANAGER.import_service(file)
        if res:
            self.message_bar.pushMessage(
                self.tr("Service imported"), Qgis.Success, 5)
        else:
            self.message_bar.pushMessage(
                err, Qgis.Critical, 5)

    def _getEventList(self, split_strategy: Optional[str] = None):
        """
        read the event URL and convert the response in a list
        """
        if self.get_current_service_type() in (SERVICE_MANAGER.WMS, SERVICE_MANAGER.WFS, SERVICE_MANAGER.WCS):
            self.ogc_service_widget.add_selected_layers()
            return

        if self.fetcher:
            # TODO - cancel current request
            return

        self.fetcher = self.get_fetcher(split_strategy=split_strategy)

        def on_started():
            self.progressBar.setValue(0)
            self.progressBar.setRange(0, 0)

        def on_progress(progress: float):
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(progress)

        self.fetcher.started.connect(on_started)
        self.fetcher.progress.connect(on_progress)
        self.fetcher.finished.connect(self._fetcher_finished)
        self.fetcher.message.connect(self._fetcher_message)
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetching'))
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.fetcher.fetch_data()

    def _fetcher_message(self, message, level):
        """
        Handles message feedback from a fetcher
        """
        self.message_bar.clearWidgets()
        self.message_bar.pushMessage(
            message, level, 0)

    def _fetcher_finished(self, res):  # pylint: disable=too-many-branches,too-many-statements
        """
        Triggered when a fetcher is finished
        """
        self.progressBar.setRange(0, 100)
        self.progressBar.reset()
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetch Data'))
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

        if not res:
            self.fetcher.deleteLater()
            self.fetcher = None
            return

        found_results = False

        layers = []
        if self.fetcher.service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC):
            layer = self.fetcher.create_event_layer()
            if layer:
                layers.append(layer)
            if self.fetcher.service_type == SERVICE_MANAGER.MACROSEISMIC:
                layer = self.fetcher.create_mdp_layer()
                if layer:
                    layers.append(layer)

            if layers:
                events_count = layers[0].featureCount()
                found_results = bool(events_count)

                service_limit = self.fetcher.service_config['settings'].get('querylimitmaxentries', None)
                self.message_bar.clearWidgets()
                if service_limit is not None and events_count >= service_limit:
                    if self.fetcher.split_strategy is None:
                        choices = list(Fetcher.STRATEGIES)
                        default_choice = \
                            [k for k, v in Fetcher.STRATEGIES.items() if v == self.fetcher.suggest_split_strategy()][0]

                        selection, ok = QInputDialog.getItem(self, self.tr('Query Exceeded Service Limit'),
                                                             self.tr(
                                                                 'Query exceeded the service\'s result limit.') + '\n\n' + self.tr(
                                                                 'Select a strategy to split the query:'),
                                                             choices,
                                                             choices.index(default_choice), False)
                        if ok:
                            split_strategy = Fetcher.STRATEGIES[selection]
                            self.fetcher.deleteLater()
                            self.fetcher = None
                            self._getEventList(split_strategy=split_strategy)
                            return

                        self.message_bar.pushMessage(self.tr("Query exceeded the service's result limit"),
                                                     Qgis.Critical, 0)

                    elif self.fetcher.exceeded_limit:
                        self.message_bar.pushMessage(self.tr(
                            "One or more queries exceeded the service's result limit. Please retry using an alternative strategy."),
                            Qgis.Critical, 0)
                elif events_count > 500:
                    self.message_bar.pushMessage(
                        self.tr("Query returned a large number of results ({})".format(events_count)), Qgis.Warning, 0)
                elif events_count == 0:
                    self.message_bar.pushMessage(
                        self.tr("Query returned no results - possibly parameters are invalid for this service"),
                        Qgis.Critical,
                        0)
                else:
                    self.message_bar.pushMessage(
                        self.tr("Query returned {} records").format(events_count), Qgis.Success, 0)
        elif self.fetcher.service_type == SERVICE_MANAGER.FDSNSTATION:
            layers.append(self.fetcher.create_stations_layer())
            stations_count = layers[0].featureCount()
            found_results = bool(stations_count)

            if stations_count == 0:
                self.message_bar.pushMessage(
                    self.tr("Query returned no results - possibly parameters are invalid for this service"),
                    Qgis.Critical,
                    0)
            else:
                self.message_bar.pushMessage(
                    self.tr("Query returned {} stations").format(stations_count), Qgis.Info, 0)
        else:
            assert False

        self.fetcher.deleteLater()
        self.fetcher = None

        if found_results:
            QgsProject.instance().addMapLayers(layers)
