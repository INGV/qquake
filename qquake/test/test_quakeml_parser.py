# coding=utf-8
"""QuakeML parser test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import ast
import os
import pprint
import unittest

from qgis.PyQt.QtCore import (
    QByteArray,
    QDateTime,
    Qt
)
from qgis.core import NULL

from qquake.quakeml import QuakeMlParser, FDSNStationXMLParser


class TestQuakeMlParser(unittest.TestCase):
    """
    Test QuakeML parsing
    """

    maxDiff = None

    UPDATE = True

    def run_check(self, path):
        """
        Checks parsed results against expectations
        """
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        parser = QuakeMlParser()
        parser.parse_initial(byte_array)

        base, expected_name = os.path.split(path)
        name, _ = os.path.splitext(expected_name)

        expected_file = os.path.join(base, name + '.txt')
        res = parser.to_dict()

        if self.UPDATE:
            with open(expected_file, 'wt', encoding='utf8') as o:
                pprint.pprint(res, o)
        else:
            with open(expected_file, 'rt', encoding='utf8') as o:
                expected_res = ast.literal_eval(o.read())

            self.assertEqual(res, expected_res)

    def run_check_stations(self, path):
        """
        Checks parsed stations against expectations
        """
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        fdsn = FDSNStationXMLParser().parse(byte_array)

        base, expected_name = os.path.split(path)
        name, _ = os.path.splitext(expected_name)

        expected_file = os.path.join(base, name + '.txt')

        res = fdsn.to_dict()

        if self.UPDATE:
            with open(expected_file, 'wt', encoding='utf8') as o:
                pprint.pprint(res, o)
        else:
            with open(expected_file, 'rt', encoding='utf8') as o:
                expected_res = ast.literal_eval(o.read())

            self.assertEqual(res, expected_res)

    def test_events(self):
        """
        Test event XML parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'events.xml')
        self.run_check(path)

    def test_macro(self):
        """
        Test macroseismic XML parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'macro.xml')
        self.run_check(path)

    def test_stations(self):
        """
        Test station XML parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'stations.xml')
        self.run_check_stations(path)

    def test_origin_datetime_composite_handling(self):
        """
        Test that datetime values can be split to component fields
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'date_components.xml')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        parser = QuakeMlParser()
        parser.parse_initial(byte_array)
        self.assertTrue(parser.events)

        features = list(parser.create_event_features([], False, False))
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['time'], QDateTime(2020, 1, 19, 2, 52, 9, 500, Qt.UTC))
        self.assertEqual(features[0]['year'], 2020)
        self.assertEqual(features[0]['month'], 1)
        self.assertEqual(features[0]['day'], 19)
        self.assertEqual(features[0]['hour'], 2)
        self.assertEqual(features[0]['min'], 52)
        self.assertEqual(features[0]['sec'], 9)

        # with some unselected fields
        features = list(parser.create_event_features(['eventParameters>event>origin>time>value',
                                                      'eventParameters>event>origin>compositeTime>month>value'],
                                                     False, False))
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['time'], QDateTime(2020, 1, 19, 2, 52, 9, 500, Qt.UTC))
        with self.assertRaises(KeyError):
            _ = features[0]['year']
        self.assertEqual(features[0]['month'], 1)
        with self.assertRaises(KeyError):
            _ = features[0]['day']
        with self.assertRaises(KeyError):
            _ = features[0]['hour']
        with self.assertRaises(KeyError):
            _ = features[0]['min']
        with self.assertRaises(KeyError):
            _ = features[0]['sec']

    def test_origin_datetime_composite_exists(self):
        """
        Test that datetime values when composite time exists
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'composite_time.xml')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        parser = QuakeMlParser()
        parser.parse_initial(byte_array)
        self.assertTrue(parser.events)

        features = list(parser.create_event_features([], False, False))
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['time'], QDateTime(1899, 9, 21, 8, 0, 0, 0))
        self.assertEqual(features[0]['year'], 1899)
        self.assertEqual(features[0]['month'], 9)
        self.assertEqual(features[0]['day'], 21)
        self.assertEqual(features[0]['hour'], 8)
        self.assertEqual(features[0]['min'], 0)
        self.assertEqual(features[0]['sec'], 0)

        # with some unselected fields
        features = list(parser.create_event_features(['eventParameters>event>origin>time>value',
                                                      'eventParameters>event>origin>compositeTime>month>value'],
                                                     False, False))
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['time'], QDateTime(1899, 9, 21, 8, 0, 0, 0))
        with self.assertRaises(KeyError):
            _ = features[0]['year']
        self.assertEqual(features[0]['month'], 9)
        with self.assertRaises(KeyError):
            _ = features[0]['day']
        with self.assertRaises(KeyError):
            _ = features[0]['hour']
        with self.assertRaises(KeyError):
            _ = features[0]['min']
        with self.assertRaises(KeyError):
            _ = features[0]['sec']

    def test_stations_to_features(self):
        """
        Test converting stations to features
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'stations.xml')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        parser = FDSNStationXMLParser()
        fdsn = parser.parse(byte_array)

        features = fdsn.to_station_features([])
        self.assertEqual(len(features), 9)

        self.assertEqual([f.attributes() for f in features], [['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'WIMIS',
                                                               QDateTime(2000, 5, 24, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               46.66488,
                                                               7.62418,
                                                               770.0,
                                                               'Wimmis, BE',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2000, 5, 24, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'SINS',
                                                               QDateTime(2012, 9, 14, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               46.68692,
                                                               7.86414,
                                                               560.0,
                                                               'Interlaken, Schloss, BE',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2012, 9, 14, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'SFRS',
                                                               QDateTime(2018, 10, 11, 22, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               46.58232,
                                                               7.65632,
                                                               772.3,
                                                               'Frutigen, Schulhaus Kanderbrück, BE',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2018, 10, 11, 22, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'STHK',
                                                               QDateTime(2015, 4, 21, 11, 31, 34, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               46.7437,
                                                               7.62953,
                                                               559.0,
                                                               'Thun, Kantonsschule, BE',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2015, 4, 21, 11, 31, 34, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'SOLB',
                                                               QDateTime(2011, 11, 22, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               47.206835,
                                                               7.517052,
                                                               430.0,
                                                               'Solothurn, Schulhaus Bruehl, SO',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2011, 11, 22, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'SOLZ',
                                                               QDateTime(2012, 1, 12, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               47.208825,
                                                               7.538306,
                                                               444.0,
                                                               'Solothurn, Zeughausgasse, SO',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2012, 1, 12, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'CH',
                                                               QDateTime(1980, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               'National Seismic Networks of Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'LAUCH',
                                                               QDateTime(2010, 10, 21, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               '',
                                                               'open',
                                                               NULL,
                                                               NULL,
                                                               46.41554,
                                                               7.77166,
                                                               2160.0,
                                                               'Lauchernalp - Loetschental, VS',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2010, 10, 21, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'Z3',
                                                               QDateTime(2015, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               QDateTime(2022, 12, 31, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               '',
                                                               'closed',
                                                               NULL,
                                                               NULL,
                                                               'AlpArray Seismic Network (AASN) temporary component',
                                                               '10.12686/alparray/z3_2015',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'A060A',
                                                               QDateTime(2015, 8, 14, 14, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               QDateTime(2017, 2, 16, 10, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               '',
                                                               'closed',
                                                               NULL,
                                                               NULL,
                                                               47.0305,
                                                               7.8904,
                                                               1112.1,
                                                               'Wasen, Napf, BE, Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2015, 8, 14, 14, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL],
                                                              ['SeisComP',
                                                               'SED',
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2021, 11, 30, 0, 56, 10, 720,
                                                                         Qt.TimeSpec(1)),
                                                               'Z3',
                                                               QDateTime(2015, 1, 1, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               QDateTime(2022, 12, 31, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               '',
                                                               'closed',
                                                               NULL,
                                                               NULL,
                                                               'AlpArray Seismic Network (AASN) temporary component',
                                                               '10.12686/alparray/z3_2015',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               'A060B',
                                                               QDateTime(2017, 5, 9, 12, 30, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               QDateTime(2022, 12, 31, 0, 0, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               '',
                                                               'closed',
                                                               NULL,
                                                               NULL,
                                                               46.993,
                                                               7.97764,
                                                               1049.1,
                                                               'Romoos, Napf, BE, Switzerland',
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               QDateTime(2017, 5, 9, 12, 30, 0, 0,
                                                                         Qt.TimeSpec(1)),
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL,
                                                               NULL]])


if __name__ == '__main__':
    unittest.main()
