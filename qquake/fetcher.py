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
    QgsVectorLayer
)

from qquake.quakeml_parser import (
    QuakeMlParser,
    Event,
    Origin,
    Magnitude
)

from qquake.services import SERVICES


class Fetcher(QObject):
    """
    Fetcher for feeds
    """

    progress = pyqtSignal(float)
    finished = pyqtSignal()

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
                 parent=None,
                 output_origins=True,
                 output_magnitudes=True,
                 output_mdps=True
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

        self.output_origins = output_origins
        self.output_magnitudes = output_magnitudes
        self.output_mdps = output_mdps and self.service_type == 'macroseismic'

        self.result = None

        self.service_config = SERVICES[self.service_type][self.event_service]

    def generate_url(self, format='text'):
        """
        Returns the URL request for the query
        """
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

        if 'querylimitmaxentries' in self.service_config['settings']:
            query.append('limit={}'.format(self.service_config['settings']['querylimitmaxentries']))

        query.append('format={}'.format(format))

        return self.service_config['endpointurl'] + '&'.join(query)

    def fetch_data(self):
        """
        Starts the fetch request
        """
        request = QNetworkRequest(QUrl(self.generate_url(format='xml')))
        self.result = None

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def _reply_progress(self, received, total):
        if total > 0:
            self.progress.emit(float(received) / total * 100)

    def _reply_finished(self, reply):
        self.result = QuakeMlParser.parse(reply.readAll())
        self.finished.emit()

    def _generate_layer_name(self, layer_type):
        name = self.event_service

        if self.event_min_magnitude is not None and self.event_max_magnitude is not None:
            name += ' ({} ≤ Magnitude ≤ {})'.format(self.event_min_magnitude, self.event_max_magnitude)
        elif self.event_min_magnitude is not None:
            name += ' ({} ≤ Magnitude)'.format(self.event_min_magnitude)
        elif self.event_max_magnitude is not None:
            name += ' (Magnitude ≤ {})'.format(self.event_max_magnitude)

        return name + ' - {}'.format(layer_type)

    def _create_empty_event_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Events'), 'memory')

        vl.dataProvider().addAttributes(Event.to_fields())
        vl.updateFields()

        return vl

    def _create_empty_origin_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Origins'), 'memory')

        vl.dataProvider().addAttributes(Origin.to_fields())
        vl.updateFields()

        return vl

    def _create_empty_magnitudes_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Magnitudes'), 'memory')

        vl.dataProvider().addAttributes(Magnitude.to_fields())
        vl.updateFields()

        return vl

    def events_to_layer(self, events):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_event_layer()

        features = []
        for e in events:
            features.append(e.to_feature())

        vl.dataProvider().addFeatures(features)

        return vl

    def origins_to_layer(self, events):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_origin_layer()

        features = []
        for e in events:
            features.extend(e.to_origin_features())

        vl.dataProvider().addFeatures(features)

        return vl

    def magnitudes_to_layer(self, events):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_magnitudes_layer()

        features = []
        for e in events:
            features.extend(e.to_magnitude_features())

        vl.dataProvider().addFeatures(features)

        return vl

    def create_event_layer(self):
        return self.events_to_layer(self.result)

    def create_origin_layer(self):
        return self.origins_to_layer(self.result)

    def create_magnitude_layer(self):
        return self.magnitudes_to_layer(self.result)
