# coding=utf-8
"""Fetcher test.

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

import unittest

from qgis.PyQt.QtCore import (
    QDate,
    QTime,
    QDateTime,
    QCoreApplication
)
from qgis.core import QgsRectangle

from qquake.fetcher import Fetcher

from qquake.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class QQuakeFetcherTest(unittest.TestCase):
    """Test fetcher works."""

    def test_url(self):
        """Test Fetcher url generation."""
        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT)
        self.assertEqual(fetcher.generate_url(), 'https://www.emidius.eu/fdsnws/event/1/query?limit=5000&format=text')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_start_date=QDateTime(QDate(2000, 5, 8), QTime(12, 0, 5)))
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?starttime=2000-05-08T12:00:05&limit=5000&format=text')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_start_date=QDateTime(QDate(2000, 5, 8), QTime(12, 0, 5)),
                          event_end_date=QDateTime(QDate(2010, 5, 8), QTime(12, 0, 5)))
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?starttime=2000-05-08T12:00:05&endtime=2010-05-08T12:00:05&limit=5000&format=text')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_min_magnitude=7, event_max_magnitude=9)
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?minmag=7&maxmag=9&limit=5000&format=text')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, limit_extent_rect=True, max_latitude=4, min_latitude=2, min_longitude=1, max_longitude=3)
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?minlatitude=2&maxlatitude=4&minlongitude=1&maxlongitude=3&limit=5000&format=text')

    def test_name(self):
        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT)
        self.assertEqual(fetcher._generate_layer_name('Events'), 'AHEAD-SHEEC - Events')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_min_magnitude=7, event_max_magnitude=9)
        self.assertEqual(fetcher._generate_layer_name('Events'),
                         'AHEAD-SHEEC (7.0 ≤ Magnitude ≤ 9.0) - Events')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_min_magnitude=7)
        self.assertEqual(fetcher._generate_layer_name('Events'),
                         'AHEAD-SHEEC (7.0 ≤ Magnitude) - Events')

        fetcher = Fetcher(event_service='AHEAD-SHEEC', service_type=SERVICE_MANAGER.FDSNEVENT, event_max_magnitude=9)
        self.assertEqual(fetcher._generate_layer_name('Events'),
                         'AHEAD-SHEEC (Magnitude ≤ 9.0) - Events')

    def test_fetch_and_parse(self):
        fetcher = Fetcher(event_service='INGV ASMI-CPTI', service_type=SERVICE_MANAGER.FDSNEVENT, event_start_date=QDateTime(QDate(2013, 1, 1)),
                          event_end_date=QDateTime(QDate(2014, 1, 1)))

        self.done = False

        self.result = None

        def parse_reply():
            self.done = True
            self.result = fetcher.result

        fetcher.finished.connect(parse_reply)
        fetcher.fetch_data()

        while not self.done:
            QCoreApplication.processEvents()

        self.assertTrue(self.result)


if __name__ == "__main__":
    suite = unittest.makeSuite(QQuakeFetcherTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
