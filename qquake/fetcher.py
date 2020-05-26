# -*- coding: utf-8 -*-
"""QQuake- Data Fetcher

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2020 by Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Copyright 2020, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
import json

from qgis.PyQt.QtCore import (
    Qt,
    QUrl,
    QObject,
    pyqtSignal
)
from qgis.PyQt.QtNetwork import QNetworkRequest

from qgis.core import (
    QgsNetworkAccessManager,
    QgsVectorLayer,
    QgsSettings
)

from qquake.quakeml_parser import (
    QuakeMlParser,
    FDSNStationXMLParser,
    Event,
    Origin,
    Magnitude,
    Station
)
from qquake.basic_text_parser import BasicTextParser

from qquake.services import SERVICES


class Fetcher(QObject):
    """
    Fetcher for feeds
    """

    BASIC = 'BASIC'
    EXTENDED = 'EXTENDED'

    progress = pyqtSignal(float)
    finished = pyqtSignal()
    message = pyqtSignal(str)

    def __init__(self, service_type,
                 event_service,
                 event_start_date=None,
                 event_end_date=None,
                 event_min_magnitude=None,
                 event_max_magnitude=None,
                 limit_extent_rect=False,
                 min_latitude=None,
                 max_latitude=None,
                 min_longitude=None,
                 max_longitude=None,
                 limit_extent_circle=False,
                 circle_latitude=None,
                 circle_longitude=None,
                 circle_min_radius=None,
                 circle_max_radius=None,
                 earthquake_number_mdps_greater=None,
                 earthquake_max_intensity_greater=None,
                 event_ids=None,
                 parent=None,
                 output_fields=None,
                 output_type=EXTENDED
                 ):
        super().__init__(parent=parent)

        self.service_type = service_type
        self.event_service = event_service
        self.event_start_date = event_start_date
        self.event_end_date = event_end_date
        self.event_min_magnitude = event_min_magnitude
        self.event_max_magnitude = event_max_magnitude
        self.limit_extent_rect = limit_extent_rect
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude
        self.limit_extent_circle = limit_extent_circle
        self.circle_latitude = circle_latitude
        self.circle_longitude = circle_longitude
        self.circle_min_radius = circle_min_radius
        self.circle_max_radius = circle_max_radius
        self.earthquake_number_mdps_greater = earthquake_number_mdps_greater
        self.earthquake_max_intensity_greater = earthquake_max_intensity_greater
        self.event_ids = event_ids
        self.pending_event_ids = event_ids
        self.output_type = output_type

        s = QgsSettings()
        self.preferred_origins_only = s.value('/plugins/qquake/output_preferred_origins', True, bool)
        self.preferred_magnitudes_only = s.value('/plugins/qquake/output_preferred_magnitude', True, bool)
        self.preferred_mdp_only = s.value('/plugins/qquake/output_preferred_mdp', True, bool)

        self.output_fields = output_fields

        if self.output_type == self.EXTENDED:
            self.result = QuakeMlParser()
        else:
            self.result = BasicTextParser()

        self.service_config = SERVICES[self.service_type][self.event_service]

        self.missing_origins = set()
        self.is_missing_origin_request = False

    def generate_url(self):
        """
        Returns the URL request for the query
        """
        format = 'text' if self.output_type == Fetcher.BASIC else 'xml'

        query = []
        # append to the string the parameter of the UI (starttime, endtime, etc)
        if self.event_start_date is not None and self.event_start_date.isValid():
            query.append('starttime={}'.format(self.event_start_date.toString(Qt.ISODate)))

        if self.event_end_date is not None and self.event_end_date.isValid():
            query.append('endtime={}'.format(self.event_end_date.toString(Qt.ISODate)))

        if self.event_min_magnitude is not None:
            query.append('minmag={}'.format(self.event_min_magnitude))

        if self.event_max_magnitude is not None:
            query.append('maxmag={}'.format(self.event_max_magnitude))

        if self.limit_extent_rect:
            if self.min_latitude is not None:
                query.append('minlatitude={}'.format(self.min_latitude))
            if self.max_latitude is not None:
                query.append('maxlatitude={}'.format(self.max_latitude))
            if self.min_longitude is not None:
                query.append('minlongitude={}'.format(self.min_longitude))
            if self.max_longitude is not None:
                query.append('maxlongitude={}'.format(self.max_longitude))
        elif self.limit_extent_circle and self.circle_latitude is not None and self.circle_longitude is not None and \
                (self.circle_min_radius is not None or self.circle_max_radius is not None):
            query.append('latitude={}'.format(self.circle_latitude))
            query.append('longitude={}'.format(self.circle_longitude))
            if self.circle_min_radius is not None:
                query.append('minradius={}'.format(self.circle_min_radius))
            if self.circle_max_radius is not None:
                query.append('maxradius={}'.format(self.circle_max_radius))

        if self.earthquake_number_mdps_greater is not None:
            query.append('minmdps={}'.format(
                self.earthquake_number_mdps_greater))

        if self.earthquake_max_intensity_greater is not None:
            query.append('minintensity={}'.format(
                self.earthquake_max_intensity_greater))

        if not self.event_ids and 'querylimitmaxentries' in self.service_config['settings']:
            query.append('limit={}'.format(self.service_config['settings']['querylimitmaxentries']))

        if self.pending_event_ids:
            query.append('eventid={}'.format(self.pending_event_ids[0]))

        if not self.preferred_origins_only:
            query.append('includeallorigins=true')
        if not self.preferred_magnitudes_only:
            query.append('includeallmagnitudes=true')

        if self.service_type == 'macroseismic':
            query.append('includemdps=true')

        query.append('format={}'.format(format))

        return self.service_config['endpointurl'] + '&'.join(query)

    def fetch_data(self):
        """
        Starts the fetch request
        """
        request = QNetworkRequest(QUrl(self.generate_url()))

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def fetch_missing(self):
        # pop first missing origin from front of queue and fetch it
        self.message.emit(self.tr('Returned XML was incomplete. {} missing origins left to fetch').format(len(self.missing_origins)))

        remaining = list(self.missing_origins)
        next_origin = remaining[0]
        self.missing_origins = set(remaining[1:])

        # change smi: prefix to http://
        next_origin = 'http://' + next_origin[4:]

        self.is_missing_origin_request = True

        request = QNetworkRequest(QUrl(next_origin))

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def fetch_next_event_by_id(self):
        # pop first id from front of queue and fetch it
        self.message.emit(self.tr('{} events left to fetch').format(len(self.pending_event_ids)))
        self.fetch_data()

    def _reply_progress(self, received, total):
        if total > 0:
            self.progress.emit(float(received) / total * 100)

    def _reply_finished(self, reply):
        if self.output_type == self.EXTENDED:
            if self.service_type in ('fdsnevent', 'macroseismic'):
                if self.is_missing_origin_request:
                    self.result.parse_missing_origin(reply.readAll())
                else:
                    if self.pending_event_ids:
                        self.pending_event_ids = self.pending_event_ids[1:]

                    if self.result.events:
                        self.result.add_events(reply.readAll())
                    else:
                        self.result.parse_initial(reply.readAll())
                        if self.service_type == 'macroseismic' and not self.event_ids:
                            # for a macroseismic parameter based search, we have to then go and fetch events
                            # one by one in order to get all the mdp location information required
                            self.pending_event_ids = [e.publicID for e in self.result.events]

                    self.missing_origins = self.missing_origins.union(self.result.scan_for_missing_origins())
            elif self.service_type == 'fdsnstation':
                self.result = FDSNStationXMLParser.parse(reply.readAll())
            else:
                assert False

            if self.missing_origins:
                self.fetch_missing()
            elif self.pending_event_ids:
                self.fetch_next_event_by_id()
            else:
                self.finished.emit()

        else:
            # basic output types
            if self.pending_event_ids:
                self.pending_event_ids = self.pending_event_ids[1:]

            if self.result.events:
                self.result.add_events(reply.readAll())
            else:
                self.result.parse(reply.readAll())

            if self.pending_event_ids:
                self.fetch_next_event_by_id()
            else:
                self.finished.emit()

    def _generate_layer_name(self, layer_type=None):
        name = self.event_service

        if self.event_min_magnitude is not None and self.event_max_magnitude is not None:
            name += ' ({:.1f} ≤ Magnitude ≤ {:.1f})'.format(self.event_min_magnitude, self.event_max_magnitude)
        elif self.event_min_magnitude is not None:
            name += ' ({:.1f} ≤ Magnitude)'.format(self.event_min_magnitude)
        elif self.event_max_magnitude is not None:
            name += ' (Magnitude ≤ {:.1f})'.format(self.event_max_magnitude)

        if layer_type:
            name += ' - {}'.format(layer_type)

        return name

    def _create_empty_event_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name(), 'memory')

        vl.dataProvider().addAttributes(self.result.to_event_fields(self.output_fields))
        vl.updateFields()

        try:
            # QGIS 3.14 - setup temporal handling automatically if time field was selected
            if vl.fields().lookupField('time') >= 0:
                temporal_props = vl.temporalProperties()
                temporal_props.setIsActive(True)
                temporal_props.setStartField('time')
                from qgis.core import QgsVectorLayerTemporalProperties
                temporal_props.setMode(QgsVectorLayerTemporalProperties.ModeFeatureDateTimeInstantFromField)

        except AttributeError:
            pass

        return vl

    def _create_empty_mdp_layer(self):
        """
        Creates an empty layer for mdp
        """
        vl = QgsVectorLayer('Point?crs=EPSG:4326', self._generate_layer_name(layer_type='mdp'), 'memory')

        vl.dataProvider().addAttributes(QuakeMlParser.create_mdp_fields())
        vl.updateFields()

        return vl

    def _create_empty_magnitudes_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Magnitudes'), 'memory')

        vl.dataProvider().addAttributes(Magnitude.to_fields(self.output_fields))
        vl.updateFields()

        return vl

    def _create_empty_stations_layer(self):
        """
        Creates an empty layer for stations
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Stations'), 'memory')

        vl.dataProvider().addAttributes(Station.to_fields(self.output_fields))
        vl.updateFields()

        return vl

    def events_to_layer(self, parser, preferred_origin_only, preferred_magnitudes_only):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_event_layer()

        features = []
        for f in parser.create_event_features(self.output_fields, preferred_origin_only, preferred_magnitudes_only):
            features.append(f)

        vl.dataProvider().addFeatures(features)

        return vl

    def mdpset_to_layer(self, parser):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_mdp_layer()

        features = []
        for f in parser.create_mdp_features():
            features.append(f)

        vl.dataProvider().addFeatures(features)

        return vl

    def stations_to_layer(self, networks):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_stations_layer()

        features = []
        for n in networks:
            features.extend(n.to_station_features(self.output_fields))

        vl.dataProvider().addFeatures(features)

        return vl

    def create_event_layer(self):
        return self.events_to_layer(self.result, self.preferred_origins_only, self.preferred_magnitudes_only)

    def create_mdp_layer(self):
        if not hasattr(self.result, 'create_mdp_features'):
            return None

        return self.mdpset_to_layer(self.result)

    def create_stations_layer(self):
        return self.stations_to_layer(self.result)
