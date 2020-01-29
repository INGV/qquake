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
    QDateTime
)
from qgis.core import QgsRectangle

from qquake.fetcher import Fetcher

from qquake.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class QQuakeFetcherTest(unittest.TestCase):
    """Test fetcher works."""

    def test_url(self):
        """Test Fetcher url generation."""
        fetcher = Fetcher(event_service='AHEAD/SHEEC')
        self.assertEqual(fetcher.generate_url(), 'https://www.emidius.eu/fdsnws/event/1/query?limit=1000&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', event_start_date=QDateTime(QDate(2000, 5, 8), QTime(12, 0, 5)))
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?starttime=2000-05-08T12:00:05&limit=1000&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', event_start_date=QDateTime(QDate(2000, 5, 8), QTime(12, 0, 5)),
                          event_end_date=QDateTime(QDate(2010, 5, 8), QTime(12, 0, 5)))
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?starttime=2000-05-08T12:00:05&endtime=2010-05-08T12:00:05&limit=1000&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', event_min_magnitude=7, event_max_magnitude=9)
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?minmag=7&maxmag=9&limit=1000&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', extent=QgsRectangle(1, 2, 3, 4))
        self.assertEqual(fetcher.generate_url(),
                         'https://www.emidius.eu/fdsnws/event/1/query?minlat=2.0&maxlat=4.0&minlon=1.0&maxlon=3.0&limit=1000&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', limit=1)
        self.assertEqual(fetcher.generate_url(), 'https://www.emidius.eu/fdsnws/event/1/query?limit=1&format=text')

        fetcher = Fetcher(event_service='AHEAD/SHEEC', limit=None)
        self.assertEqual(fetcher.generate_url(), 'https://www.emidius.eu/fdsnws/event/1/query?format=text')


if __name__ == "__main__":
    suite = unittest.makeSuite(QQuakeFetcherTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
