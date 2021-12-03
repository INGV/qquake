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
from qquake.services import ServiceManager, SERVICE_MANAGER


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

    def test_url_no_fetch_multiple(self):
        """
        Test generation of urls when include all * multiple is false
        """
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe')
        self.assertTrue(fetcher.preferred_magnitudes_only)
        self.assertTrue(fetcher.preferred_origins_only)
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?limit=15000&format=xml')

        # if event ids are specified then we can safely get all origins/magnitudes
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe', event_ids=[1, 2])
        fetcher.preferred_origins_only = False
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?eventid=1&includeallorigins=true&format=xml')

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe', event_ids=[1, 2])
        fetcher.preferred_magnitudes_only = False
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?eventid=1&includeallmagnitudes=true&format=xml')

        # without event ids we can't get all origins/magnitudes
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe')
        fetcher.preferred_origins_only = False
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?limit=15000&format=xml')

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe')
        fetcher.preferred_magnitudes_only = False
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?limit=15000&format=xml')

        # a service which doesn't support all magnitudes/origins should never include the parameter
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['INGV ISIDe']['settings']['queryincludeallorigins'] = False
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe', event_ids=[1, 2])
        self.assertTrue(fetcher.preferred_origins_only)
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?eventid=1&format=xml')

        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['INGV ISIDe']['settings']['queryincludeallorigins'] = True
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['INGV ISIDe']['settings'][
            'queryincludeallmagnitudes'] = False

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          'INGV ISIDe', event_ids=[1, 2])
        self.assertTrue(fetcher.preferred_magnitudes_only)
        self.assertEqual(fetcher.generate_url(),
                         'http://webservices.ingv.it/fdsnws/event/1/query?eventid=1&format=xml')


if __name__ == '__main__':
    unittest.main()
