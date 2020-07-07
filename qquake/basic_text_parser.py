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

MDP_FIELD_TYPE = {
    'EventID': QVariant.String,
    'MDPsetID': QVariant.String,
    'Time': QVariant.DateTime,
    'Region': QVariant.String,
    'MDPcount': QVariant.Int,
    'maximumIntensity': QVariant.String,
    'macroseismicScale': QVariant.String,
    'MDPID': QVariant.String,
    'PlaceID': QVariant.String,
    'PlaceName': QVariant.String,
    'ReferenceLatitude': QVariant.Double,
    'ReferenceLongitude': QVariant.Double,
    'ExpectedIntensity': QVariant.String,
    'Quality': QVariant.String,
    'ReportCount': QVariant.String
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
        self.mdp_headers = []
        self.events = []
        self.mdp = []

    def parser_header_line(self, line):
        assert line[0] == '#'
        line = line[1:]
        self.headers = [h.strip() for h in line.split('|')]

    def parse(self, content):
        if not content:
            return
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

    def add_mdp(self, content):
        if not content:
            return

        lines = content.data().decode().split('\n')
        if not len(lines):
            return

        assert lines[0][0] == '#'
        self.mdp_headers = [h.strip() for h in lines[0][1:].split('|')]
        for e in lines[1:]:
            if not e:
                continue

            self.mdp.append(dict(zip(self.mdp_headers, e.split('|'))))

    @staticmethod
    def get_field_type(name):
        for k, v in EVENT_FIELD_TYPE.items():
            if k.lower() == name.lower():
                return v
        return None

    @staticmethod
    def get_mdp_field_type(name):
        for k, v in MDP_FIELD_TYPE.items():
            if k.lower() == name.lower():
                return v
        return None

    def to_event_fields(self, selected_fields=None):
        fields = QgsFields()
        for f in self.headers:
            fields.append(QgsField(f, self.get_field_type(f)))

        return fields

    def to_event_feature(self, event, fields):
        f = QgsFeature(fields)
        for k, v in event.items():
            try:
                if fields[fields.lookupField(k)].type() == QVariant.DateTime:
                    v = v.replace('--','00')
                    v = QDateTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Date:
                    v = QDate.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Time:
                    v = QTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Double:
                    v = float(v)
                elif fields[fields.lookupField(k)].type() == QVariant.Int:
                    v = int(v)
            except:
                v = NULL

            f[k] = v

        if event.get('Latitude') and event.get('Longitude'):
            geom = QgsPoint(x=float(event['Longitude']), y=float(event['Latitude']))
            f.setGeometry(QgsGeometry(geom))

        return f

    def create_event_features(self, output_fields, preferred_origin_only, preferred_magnitudes_only):
        fields = self.to_event_fields()

        for e in self.events:
            yield self.to_event_feature(e, fields)

    def create_mdp_fields(self, selected_fields):
        fields = QgsFields()
        for f in self.mdp_headers:
            fields.append(QgsField(f, self.get_mdp_field_type(f)))

        return fields

    def create_mdp_features(self, selected_fields):
        fields = self.create_mdp_fields(selected_fields)

        for e in self.mdp:
            yield self.to_mdp_feature(e, fields)

    def to_mdp_feature(self, event, fields):
        f = QgsFeature(fields)
        for k, v in event.items():
            try:
                if fields[fields.lookupField(k)].type() == QVariant.DateTime:
                    v = v.replace('--','00')
                    v = QDateTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Date:
                    v = QDate.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Time:
                    v = QTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Double:
                    v = float(v)
                elif fields[fields.lookupField(k)].type() == QVariant.Int:
                    v = int(v)
            except:
                v = NULL
                
            f[k] = v

        if event.get('ReferenceLatitude') and event.get('ReferenceLongitude'):
            geom = QgsPoint(x=float(event['ReferenceLongitude']), y=float(event['ReferenceLatitude']))
            f.setGeometry(QgsGeometry(geom))

        return f


class BasicStationParser:

    def __init__(self):
        self.headers = []
        self.stations = []

    def parser_header_line(self, line):
        assert line[0] == '#'
        line = line[1:]
        self.headers = [h.strip() for h in line.split('|')]

    def parse(self, content):
        if not content:
            return

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
            try:
                if fields[fields.lookupField(k)].type() == QVariant.DateTime:
                    v = v.replace('--','00')
                    v = QDateTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Date:
                    v = QDate.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Time:
                    v = QTime.fromString(v, Qt.ISODate)
                elif fields[fields.lookupField(k)].type() == QVariant.Double:
                    v = float(v)
                elif fields[fields.lookupField(k)].type() == QVariant.Int:
                    v = int(v)
            except:
                v = NULL

            f[k] = v

        if station.get('Latitude') and station.get('Longitude'):
            geom = QgsPoint(x=float(station['Longitude']), y=float(station['Latitude']))
            f.setGeometry(QgsGeometry(geom))

        return f

    def create_station_features(self):
        fields = self.to_station_fields()

        for e in self.stations:
            yield self.to_station_feature(e, fields)
