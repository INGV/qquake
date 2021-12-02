# coding=utf-8
"""Fetcher test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import unittest

from qgis.PyQt.QtCore import QDateTime

from qquake.fetcher import Fetcher
from qquake.services import ServiceManager


class TestFetcher(unittest.TestCase):
    """
    Test fetcher
    """

    def test_url(self):
        """
        Test generation of urls
        """

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'EMSC-CSEM')
        self.assertEqual(fetcher.generate_url(),
                         'https://www.seismicportal.eu/fdsnws/event/1/query?limit=1000&format=xml')
        fetcher.event_type = 'cavity collapse'
        self.assertEqual(fetcher.generate_url(),
                         'https://www.seismicportal.eu/fdsnws/event/1/query?eventtype=cavity collapse&limit=1000&format=xml')
        fetcher.event_type = None

        fetcher.updated_after = QDateTime(2021, 5, 6, 13, 14, 15)
        self.assertEqual(fetcher.generate_url(),
                         'https://www.seismicportal.eu/fdsnws/event/1/query?updatedafter=2021-05-06T13:14:15&limit=1000&format=xml')


if __name__ == '__main__':
    unittest.main()
