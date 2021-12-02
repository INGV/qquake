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

from qquake.quakeml import QuakeMlParser, FDSNStationXMLParser


class TestQuakeMlParser(unittest.TestCase):
    """
    Test QuakeML parsing
    """

    maxDiff = None

    UPDATE = False

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

        stations = FDSNStationXMLParser().parse(byte_array)

        base, expected_name = os.path.split(path)
        name, _ = os.path.splitext(expected_name)

        expected_file = os.path.join(base, name + '.txt')
        res = [station.to_dict() for station in stations]

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


if __name__ == '__main__':
    unittest.main()
