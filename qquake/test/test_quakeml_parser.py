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

from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtGui import QGuiApplication

from qquake.quakeml_parser import QuakeMlParser, FDSNStationXMLParser


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


app = QGuiApplication([])

if __name__ == '__main__':
    unittest.main()
