# coding=utf-8
"""QuakeML parser test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import os
import unittest

from qgis.PyQt.QtCore import (
    QByteArray
)

from qquake.services import WadlServiceParser, ServiceManager


class TestWadl(unittest.TestCase):
    """
    Test WADL parsing
    """

    maxDiff = None

    def test_event_wadl(self):
        """
        Test WADL event parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'event.wadl')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        res = WadlServiceParser.parse_wadl(byte_array, ServiceManager.FDSNEVENT)
        self.assertEqual(res, {'boundingbox': [-120.0, -70.0, 60.0, 50.0],
                               'endpointurl': 'http://webservices.rm.ingv.it/fdsnws/event/1/query?',
                               'settings': {'querydepth': True,
                                            'queryeventid': True,
                                            'queryincludeallmagnitudes': True,
                                            'queryincludeallorigins': True}})

    def test_event_wadl2(self):
        """
        Test WADL event parsing 2
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'event2.wadl')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        res = WadlServiceParser.parse_wadl(byte_array, ServiceManager.FDSNEVENT)
        self.assertEqual(res, {'boundingbox': [5.0, 35.0, 21.0, 48.0],
                               'endpointurl': 'https://www.emidius.mi.ingv.it/fdsnws/event/1/query?',
                               'settings': {'querydepth': False,
                                            'queryeventid': False,
                                            'queryincludeallmagnitudes': False,
                                            'queryincludeallorigins': False}})

    def test_macro_1(self):
        """
        Test WADL macro parsing 1
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'macro.wadl')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        res = WadlServiceParser.parse_wadl(byte_array, ServiceManager.MACROSEISMIC)
        self.assertEqual(res, {'boundingbox': [-32.0, 33.0, 45.0, 74.0],
                               'endpointurl': 'https://www.emidius.eu/services/macroseismic/query?',
                               'settings': {'querydepth': False,
                                            'queryeventid': True,
                                            'queryincludeallmagnitudes': True,
                                            'queryincludeallorigins': True}})

    def test_macro_2(self):
        """
        Test WADL macro parsing 2
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'macro2.wadl')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        res = WadlServiceParser.parse_wadl(byte_array, ServiceManager.MACROSEISMIC)
        self.assertEqual(res, {'boundingbox': [5.0, 35.0, 21.0, 48.0],
                               'endpointurl': 'https://www.emidius.mi.ingv.it/services/macroseismic/query?',
                               'settings': {'querydepth': False,
                                            'queryeventid': True,
                                            'queryincludeallmagnitudes': True,
                                            'queryincludeallorigins': True}})

    def test_station(self):
        """
        Test station parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'data', 'station.wadl')
        with open(path, 'rb') as f:
            content = f.read()

        byte_array = QByteArray(content)

        res = WadlServiceParser.parse_wadl(byte_array, ServiceManager.FDSNSTATION)
        self.assertEqual(res, {'boundingbox': [-90.0, -180.0, 90.0, 180.0],
                               'endpointurl': '/fdsnws/station/1/query?',
                               'settings': {}})

    def test_find_url(self):
        """
        Test finding URL
        """
        self.assertEqual(WadlServiceParser.find_url('https://www.emidius.eu/fdsnws/event/1/query?'),
                         'https://www.emidius.eu/fdsnws/event/1/application.wadl')
        self.assertEqual(WadlServiceParser.find_url('https://www.emidius.eu/fdsnws/event/1/query'),
                         'https://www.emidius.eu/fdsnws/event/1/application.wadl')

        self.assertEqual(WadlServiceParser.find_url('https://www.emidius.eu/fdsnws/event/1/'),
                         'https://www.emidius.eu/fdsnws/event/1/application.wadl')

        self.assertEqual(WadlServiceParser.find_url('https://www.emidius.eu/fdsnws/event/1/application.wadl'),
                         'https://www.emidius.eu/fdsnws/event/1/application.wadl')


if __name__ == '__main__':
    unittest.main()
