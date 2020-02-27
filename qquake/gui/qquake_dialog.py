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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QSizePolicy,
    QVBoxLayout
)
from qgis.PyQt.QtCore import (
    Qt,
    QDate,
    QDateTime
)

from qgis.core import (
    Qgis,
    QgsProject,
    QgsSettings
)
from qgis.gui import (
    QgsGui,
    QgsMessageBar
)

from qquake.fetcher import Fetcher
from qquake.gui.filter_parameter_widget import FilterParameterWidget
from qquake.gui.ogc_service_options_widget import OgcServiceWidget
from qquake.gui.service_information_widget import ServiceInformationWidget
from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICES

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('qquake_dialog_base.ui'))


class QQuakeDialog(QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.fsdn_event_filter = FilterParameterWidget(iface)
        self.fsdn_event_filter.set_show_macroseismic_data_options(False)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.fsdn_event_filter)
        self.fsdn_event_filter_container.setLayout(vl)
        self.earthquake_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.earthquake_service_info_widget)
        self.earthquake_service_info_container.setLayout(vl)

        self.macro_filter = FilterParameterWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_filter)
        self.macro_filter_container.setLayout(vl)
        self.macro_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.macro_service_info_widget)
        self.macro_service_info_container.setLayout(vl)

        self.station_filter = FilterParameterWidget(iface)
        self.station_filter.set_show_macroseismic_data_options(False)
        self.station_filter.set_show_magnitude_options(False)
        self.station_filter.set_show_time_coverage_options(False)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_filter)
        self.station_filter_container.setLayout(vl)
        self.station_service_info_widget = ServiceInformationWidget(iface)
        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.station_service_info_widget)
        self.station_service_info_container.setLayout(vl)

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

        self.fsdn_event_url_text_browser.viewport().setAutoFillBackground(False)
        self.fdsn_macro_url_text_browser.viewport().setAutoFillBackground(False)
        self.fdsn_station_url_text_browser.viewport().setAutoFillBackground(False)

        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetch Data'))
        self.button_box.rejected.connect(self._save_settings)

        self.iface = iface

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_event_list.addItems(SERVICES['fdsnevent'].keys())
        self.fdsn_event_list.setCurrentRow(0)

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_macro_list.addItems(SERVICES['macroseismic'].keys())
        self.fdsn_macro_list.setCurrentRow(0)

        # fill the FDSN listWidget with the dictionary keys
        self.fdsn_station_list.addItems(SERVICES['fdsnstation'].keys())
        self.fdsn_station_list.setCurrentRow(0)

        # OGC
        self.ogc_combo.addItem(self.tr('Web Map Services (WMS)'), 'wms')
        self.ogc_combo.addItem(self.tr('Web Feature Services (WFS)'), 'wfs')
        self.ogc_combo.currentIndexChanged.connect(self.refreshOgcWidgets)
        self.ogc_list.currentRowChanged.connect(
            self._ogc_service_changed)
        self.refreshOgcWidgets()

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

        self.fsdn_event_filter.changed.connect(lambda: self._refresh_url('fdsnevent'))
        self.fdsn_event_list.currentRowChanged.connect(lambda: self._refresh_url('fdsnevent'))
        self.macro_filter.changed.connect(lambda: self._refresh_url('macroseismic'))
        self.fdsn_macro_list.currentRowChanged.connect(lambda: self._refresh_url('macroseismic'))
        self.station_filter.changed.connect(lambda: self._refresh_url('fdsnstation'))
        self.fdsn_station_list.currentRowChanged.connect(lambda: self._refresh_url('fdsnstation'))

        self.button_box.accepted.connect(self._getEventList)

        self.fetcher = None

        QgsGui.enableAutoGeometryRestore(self)

        self._restore_settings()
        self._refresh_url('fdsnevent')
        self._refresh_url('macroseismic')
        self._refresh_url('fdsnstation')

    def closeEvent(self, e):
        self._save_settings()
        super().closeEvent(e)

    def _save_settings(self):
        s = QgsSettings()
        s.setValue('/plugins/qquake/last_tab', self.service_tab_widget.currentIndex())
        s.setValue('/plugins/qquake/fdsn_event_last_event_service', self.fdsn_event_list.currentItem().text())
        s.setValue('/plugins/qquake/macro_last_event_service', self.fdsn_macro_list.currentItem().text())

        self.fsdn_event_filter.save_settings('fsdn_event')
        self.macro_filter.save_settings('macro')
        self.station_filter.save_settings('stations')

    def _restore_settings(self):
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

        self.fsdn_event_filter.restore_settings('fsdn_event')
        self.macro_filter.restore_settings('macro')
        self.station_filter.restore_settings('stations')

    def get_fetcher(self, service_type=None):
        """
        Returns a quake fetcher corresponding to the current dialog settings
        """

        if service_type is None:
            if self.service_tab_widget.currentIndex() == 0:
                service_type = 'fdsnevent'
            elif self.service_tab_widget.currentIndex() == 1:
                service_type = 'macroseismic'
            elif self.service_tab_widget.currentIndex() == 2:
                service_type = 'fdsnstation'

        if service_type == 'fdsnevent':
            service = self.fdsn_event_list.currentItem().text()
            filter_widget = self.fsdn_event_filter
        elif service_type == 'macroseismic':
            service = self.fdsn_macro_list.currentItem().text()
            filter_widget = self.macro_filter
        elif service_type == 'fdsnstation':
            service = self.fdsn_station_list.currentItem().text()
            filter_widget = self.station_filter

        return Fetcher(service_type=service_type,
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
                       earthquake_number_mdps_greater=filter_widget.earthquake_number_mdps_greater(),
                       earthquake_max_intensity_greater=filter_widget.earthquake_max_intensity_greater(),
                       output_magnitudes=not filter_widget.output_preferred_magnitudes_only(),
                       output_origins=not filter_widget.output_preferred_origins_only(),
                       output_mdps=not filter_widget.output_preferred_mdp_only(),
                       )

    def _refresh_url(self, service_type):
        fetcher = self.get_fetcher(service_type)

        if service_type == 'fdsnevent':
            self.fsdn_event_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))
        elif service_type == 'macroseismic':
            self.fdsn_macro_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))
        elif service_type == 'fdsnstation':
            self.fdsn_station_url_text_browser.setText('<a href="{0}">{0}</a>'.format(fetcher.generate_url()))

    def _update_service_widgets(self, service_type, service_id, filter_widget, info_widget):
        service_config = SERVICES[service_type][service_id]

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

        box = SERVICES['boundingboxpredefined'][
            service_config['default']['boundingboxpredefined']]['boundingbox']
        filter_widget.set_extent_limit(box)
        info_widget.set_service(service_type=service_type, service_name=service_id)

    def _refresh_fdsnevent_widgets(self):
        """
        Refreshing the FDSN-Event UI depending on the WS chosen
        """
        service_id = self.fdsn_event_list.currentItem().text()
        self._update_service_widgets(service_type='fdsnevent', service_id=service_id,
                                     filter_widget=self.fsdn_event_filter,
                                     info_widget=self.earthquake_service_info_widget)

    def refreshFdsnMacroseismicWidgets(self):
        """
        Refreshing the FDSN-Macroseismic UI depending on the WS chosen
        """
        service_id = self.fdsn_macro_list.currentItem().text()
        self._update_service_widgets(service_type='macroseismic', service_id=service_id,
                                     filter_widget=self.macro_filter, info_widget=self.macro_service_info_widget)

    def refreshFdsnStationWidgets(self):
        """
        Refreshing the FDSN-Macroseismic UI depending on the WS chosen
        """
        service_id = self.fdsn_station_list.currentItem().text()
        self._update_service_widgets(service_type='fdsnstation', service_id=service_id,
                                     filter_widget=self.station_filter, info_widget=self.station_service_info_widget)

    def refreshOgcWidgets(self):
        """
        read the ogc_combo and fill it with the services
        """
        self.ogc_list.clear()
        ogc_selection = self.ogc_combo.currentData()
        self.ogc_list.addItems(SERVICES[ogc_selection].keys())
        self.ogc_list.setCurrentRow(0)

    def _ogc_service_changed(self):
        if not self.ogc_list.currentItem():
            return

        self.ogc_service_widget.set_service(service_type=self.ogc_combo.currentData(),
                                            service_name=self.ogc_list.currentItem().text())

        self.ogc_service_info_widget.set_service(service_type=self.ogc_combo.currentData(),
                                                 service_name=self.ogc_list.currentItem().text())

    def _getEventList(self):
        """
        read the event URL and convert the response in a list
        """
        if self.fetcher:
            # TODO - cancel current request
            return

        self.fetcher = self.get_fetcher()
        self.fetcher.progress.connect(self.progressBar.setValue)
        self.fetcher.finished.connect(self._fetcher_finished)
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetching'))
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.fetcher.fetch_data()

    def _fetcher_finished(self):
        self.progressBar.reset()
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr('Fetch Data'))
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

        layers = []
        if self.fetcher.service_type in ('fdsnevent', 'macroseismic'):
            layers.append(self.fetcher.create_event_layer())
            events_count = layers[0].featureCount()
            if self.fetcher.output_origins:
                layers.append(self.fetcher.create_origin_layer())
            if self.fetcher.output_magnitudes:
                layers.append(self.fetcher.create_magnitude_layer())
    
            max_feature_count = 0
            for l in layers:
                max_feature_count = max(max_feature_count, l.featureCount())
    
            service_limit = self.fetcher.service_config['settings'].get('querylimitmaxentries', None)
            self.message_bar.clearWidgets()
            if service_limit is not None and max_feature_count >= service_limit:
                self.message_bar.pushMessage(self.tr("Query exceeded the service's result limit"), Qgis.Critical, 0)
            elif max_feature_count > 500:
                self.message_bar.pushMessage(
                    self.tr("Query returned a large number of results ({})".format(max_feature_count)), Qgis.Warning, 0)
            elif max_feature_count == 0:
                self.message_bar.pushMessage(
                    self.tr("Query returned no results - possibly parameters are invalid for this service"), Qgis.Critical,
                    0)
            else:
                self.message_bar.pushMessage(
                    self.tr("Query returned {} events").format(events_count), Qgis.Info, 0)
        elif self.fetcher.service_type =='fdsnstation':
            layers.append(self.fetcher.create_stations_layer())
            stations_count = layers[0].featureCount()
            max_feature_count = 0
            for l in layers:
                max_feature_count = max(max_feature_count, l.featureCount())

            if max_feature_count == 0:
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

        if max_feature_count > 0:
            QgsProject.instance().addMapLayers(layers)
