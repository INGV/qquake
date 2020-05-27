# -*- coding: utf-8 -*-
"""QQuake- Basic text parser

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

import json
import os

from qgis.PyQt.QtCore import QVariant, QDate, QDateTime, QTime, Qt
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsSettings,
    NULL
)

EVENT_FIELD_TYPE = {
    'EventID': QVariant.String,
    'Time': QVariant.DateTime,
    'Latitude': QVariant.Double,
    'Longitude': QVariant.Double,
    'Depth/km': QVariant.Double,
    'Author': QVariant.String,
    'Catalog': QVariant.String,
    'Contributor': QVariant.String,
    'ContributorID': QVariant.String,
    'MagType': QVariant.String,
    'Magnitude': QVariant.Double,
    'MagAuthor': QVariant.String,
    'EventLocationName': QVariant.String
}

STATION_FIELD_TYPE = {
    'Network': QVariant.String,
    'Station': QVariant.String,
    'Latitude': QVariant.Double,
    'Longitude': QVariant.Double,
    'Elevation': QVariant.Double,
    'SiteName': QVariant.String,
    'StartTime': QVariant.DateTime,
    'EndTime': QVariant.DateTime
}


class BasicTextParser:
    """
    Basic plain text parser
    """

    def __init__(self):
        self.headers = []
        self.events = []

    def parser_header_line(self, line):
        assert line[0] == '#'
        line = line[1:]
        self.headers = line.split('|')

    def parse(self, content):
        lines = content.data().decode().split('\n')
        self.parser_header_line(lines[0])
        self._add_events(lines[1:])

    def add_events(self, content):
        lines = content.data().decode().split('\n')
        self._add_events(lines[1:])

    def _add_events(self, lines):
        for e in lines:
            if not e:
                continue

            self.events.append(dict(zip(self.headers, e.split('|'))))

    def to_event_fields(self, selected_fields=None):
        fields = QgsFields()
        for f in self.headers:
            fields.append(QgsField(f, EVENT_FIELD_TYPE[f]))

        return fields

    def to_event_feature(self, event, fields):
        f = QgsFeature(fields)
        for k, v in event.items():
            f[k] = v

        if event.get('Latitude') and event.get('Longitude'):
            geom = QgsPoint(x=float(event['Longitude']), y=float(event['Latitude']))
            f.setGeometry(QgsGeometry(geom))

        return f

    def create_event_features(self, output_fields, preferred_origin_only, preferred_magnitudes_only):
        fields = self.to_event_fields()

        for e in self.events:
            yield self.to_event_feature(e, fields)


class BasicStationParser:

    def __init__(self):
        self.headers = []
        self.stations = []

    def parser_header_line(self, line):
        assert line[0] == '#'
        line = line[1:]
        self.headers = line.split('|')

    def parse(self, content):
        lines = content.data().decode().split('\n')
        self.parser_header_line(lines[0])
        self._add_stations(lines[1:])

    def add_stations(self, content):
        lines = content.data().decode().split('\n')
        self._add_stations(lines[1:])

    def _add_stations(self, lines):
        for e in lines:
            if not e:
                continue

            self.stations.append(dict(zip(self.headers, e.split('|'))))

    def to_station_fields(self, selected_fields=None):
        fields = QgsFields()
        for f in self.headers:
            fields.append(QgsField(f, STATION_FIELD_TYPE[f]))

        return fields

    def to_station_feature(self, station, fields):
        f = QgsFeature(fields)
        for k, v in station.items():
            f[k] = v

        if station.get('Latitude') and station.get('Longitude'):
            geom = QgsPoint(x=float(station['Longitude']), y=float(station['Latitude']))
            f.setGeometry(QgsGeometry(geom))

        return f

    def create_station_features(self):
        fields = self.to_station_fields()

        for e in self.stations:
            yield self.to_station_feature(e, fields)
