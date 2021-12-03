# coding=utf-8
"""Fetcher test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import unittest

from qgis.PyQt.QtCore import QDateTime, Qt

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

    def test_url_with_limit(self):
        """
        Test URL with limit
        """
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM")
        self.assertEqual(fetcher.generate_url(),
                         'https://www.seismicportal.eu/fdsnws/event/1/query?limit=1000&format=xml')
        self.assertEqual(fetcher.query_limit, 1000)

    def test_suggest_strategy(self):
        """
        Test suggesting a split strategy
        """

        # with both start and end date specified
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM", event_start_date=QDateTime(1980, 1, 1, 0, 0, 0),
                          event_end_date=QDateTime(2000, 1, 1, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_YEAR)

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM", event_start_date=QDateTime(1980, 1, 1, 0, 0, 0),
                          event_end_date=QDateTime(1981, 1, 1, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_MONTH)

        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM", event_start_date=QDateTime(1980, 1, 1, 0, 0, 0),
                          event_end_date=QDateTime(1980, 1, 30, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_DAY)

        # with only end date specified
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["datestart"] = "1998-01-01T00:00:00+00:00"
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_end_date=QDateTime(2003, 1, 30, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_YEAR)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_end_date=QDateTime(1998, 5, 30, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_MONTH)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_end_date=QDateTime(1998, 1, 30, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_DAY)

        # with only start date specified
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["dateend"] = "1998-05-01T00:00:00+00:00"
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(1991, 1, 30, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_YEAR)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(1998, 1, 1, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_MONTH)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(1998, 4, 20, 0, 0, 0))
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_DAY)

        # service doesn't have a fixed end date
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["dateend"] = None
        start_date = QDateTime.currentDateTime().addYears(-10)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=start_date)
        start_date = QDateTime.currentDateTime().addMonths(-10)
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_YEAR)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=start_date)
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_MONTH)
        start_date = QDateTime.currentDateTime().addDays(-10)
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=start_date)
        self.assertEqual(fetcher.suggest_split_strategy(), Fetcher.SPLIT_STRATEGY_DAY)

    def test_split_strategy(self):
        """
        Test split strategy logic
        """
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM", event_start_date=QDateTime(1980, 1, 1, 0, 0, 0),
                          event_end_date=QDateTime(2000, 1, 1, 0, 0, 0),
                          split_strategy=Fetcher.SPLIT_STRATEGY_DAY)
        self.assertEqual(fetcher.event_start_date_limit, QDateTime(1980, 1, 1, 0, 0, 0))
        self.assertEqual(fetcher.event_end_date_limit, QDateTime(2000, 1, 1, 0, 0, 0))

        # no explicit start date
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["datestart"] = "1998-01-01T00:00:00+00:00"
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_end_date=QDateTime(2000, 1, 1, 0, 0, 0),
                          split_strategy=Fetcher.SPLIT_STRATEGY_DAY)
        self.assertEqual(fetcher.event_start_date_limit, QDateTime(1998, 1, 1, 0, 0, 0, 0, Qt.UTC))
        self.assertEqual(fetcher.event_end_date_limit, QDateTime(2000, 1, 1, 0, 0, 0))

        # no explicit end date
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["dateend"] = "1998-01-01T00:00:00+00:00"
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(1997, 1, 1, 0, 0, 0),
                          split_strategy=Fetcher.SPLIT_STRATEGY_DAY)
        self.assertEqual(fetcher.event_start_date_limit, QDateTime(1997, 1, 1, 0, 0, 0, 0))
        self.assertEqual(fetcher.event_end_date_limit, QDateTime(1998, 1, 1, 0, 0, 0, 0, Qt.UTC))
        SERVICE_MANAGER.services[ServiceManager.FDSNEVENT]['EMSC-CSEM']["dateend"] = ''
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(1997, 1, 1, 0, 0, 0),
                          split_strategy=Fetcher.SPLIT_STRATEGY_DAY)
        self.assertEqual(fetcher.event_start_date_limit, QDateTime(1997, 1, 1, 0, 0, 0, 0))
        self.assertEqual(fetcher.event_end_date_limit.date(), QDateTime.currentDateTime().date())

    def test_split_range(self):
        """
        Test splitting a date range by strategy
        """
        self.assertEqual(Fetcher.split_range_by_strategy(Fetcher.SPLIT_STRATEGY_YEAR, QDateTime(2020, 1, 1, 1, 1, 1),
                                                         QDateTime(2022, 1, 1, 1, 1, 1)),
                         [(QDateTime(2020, 1, 1, 1, 1, 1),
                           QDateTime(2021, 1, 1, 1, 1, 1)),
                          (QDateTime(2021, 1, 1, 1, 1, 2),
                           QDateTime(2022, 1, 1, 1, 1, 2))])

        self.assertEqual(Fetcher.split_range_by_strategy(Fetcher.SPLIT_STRATEGY_MONTH, QDateTime(2020, 1, 1, 1, 1, 1),
                                                         QDateTime(2020, 4, 1, 1, 1, 1)),
                         [(QDateTime(2020, 1, 1, 1, 1, 1),
                           QDateTime(2020, 2, 1, 1, 1, 1)),
                          (QDateTime(2020, 2, 1, 1, 1, 2),
                           QDateTime(2020, 3, 1, 1, 1, 2)),
                          (QDateTime(2020, 3, 1, 1, 1, 3),
                           QDateTime(2020, 4, 1, 1, 1, 3))])

    def test_fetch_with_split(self):
        """
        Test fetcher with split strategy
        """
        fetcher = Fetcher(ServiceManager.FDSNEVENT,
                          "EMSC-CSEM",
                          event_start_date=QDateTime(2020, 1, 1, 1, 1, 1),
                          event_end_date=QDateTime(2020, 1, 4, 1, 1, 1),
                          split_strategy=Fetcher.SPLIT_STRATEGY_DAY)
        self.assertEqual(fetcher.event_start_date, QDateTime(2020, 1, 1, 1, 1, 1))
        self.assertEqual(fetcher.event_end_date, QDateTime(2020, 1, 2, 1, 1, 1))
        self.assertEqual(fetcher.ranges, [
            (QDateTime(2020, 1, 2, 1, 1, 2),
             QDateTime(2020, 1, 3, 1, 1, 2)),
            (QDateTime(2020, 1, 3, 1, 1, 3),
             QDateTime(2020, 1, 4, 1, 1, 3))])


if __name__ == '__main__':
    unittest.main()
