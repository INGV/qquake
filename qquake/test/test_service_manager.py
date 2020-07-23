# coding=utf-8
"""Service manager test.

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
from qgis.PyQt.QtTest import QSignalSpy
from qgis.core import QgsRectangle

from qquake.fetcher import Fetcher
from qquake.services import SERVICE_MANAGER, ServiceManager

from qquake.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class QQuakeServiceManagerTest(unittest.TestCase):
    """Test service manager works."""

    def testPredefinedAreas(self):
        areas = SERVICE_MANAGER.available_predefined_bounding_boxes()
        self.assertIn('world', areas)

        extent = SERVICE_MANAGER.predefined_bounding_box('world')
        self.assertEqual(extent['title'], 'World')
        self.assertTrue(extent['read_only'])

        spy = QSignalSpy(SERVICE_MANAGER.areasChanged)
        SERVICE_MANAGER.add_predefined_bounding_box('mine', {'title': 'Mine', 'boundingbox': [1, 2, 3, 4]})
        self.assertEqual(len(spy), 1)

        self.assertIn('mine', SERVICE_MANAGER.available_predefined_bounding_boxes())
        self.assertEqual(SERVICE_MANAGER.predefined_bounding_box('mine')['title'], 'Mine')

        SERVICE_MANAGER.add_predefined_bounding_box('mine', {'title': 'Mine2', 'boundingbox': [1, 2, 3, 4]})
        self.assertEqual(len(spy), 2)
        self.assertIn('mine', SERVICE_MANAGER.available_predefined_bounding_boxes())
        self.assertEqual(SERVICE_MANAGER.predefined_bounding_box('mine')['title'], 'Mine2')

        sm = ServiceManager()
        self.assertIn('mine', sm.available_predefined_bounding_boxes())
        self.assertEqual(sm.predefined_bounding_box('mine')['title'], 'Mine2')

        self.assertFalse(SERVICE_MANAGER.remove_predefined_bounding_box('x'))
        self.assertEqual(len(spy), 2)
        self.assertFalse(SERVICE_MANAGER.remove_predefined_bounding_box('World'))
        self.assertEqual(len(spy), 2)
        self.assertTrue(SERVICE_MANAGER.remove_predefined_bounding_box('mine'))
        self.assertEqual(len(spy), 3)
        self.assertNotIn('mine', SERVICE_MANAGER.available_predefined_bounding_boxes())

    def testGetContributorEndpoint(self):
        self.assertEqual(SERVICE_MANAGER.get_contributor_endpoint(SERVICE_MANAGER.FDSNEVENT, 'AHEAD-SHEEC'),
                         'https://www.emidius.eu/fdsnws/event/1/contributors')
        self.assertEqual(SERVICE_MANAGER.get_contributor_endpoint(SERVICE_MANAGER.MACROSEISMIC, 'INGV ASMI-DBMI'),
                         'https://emidius.mi.ingv.it/services/macroseismic/contributors')
        self.assertIsNone(SERVICE_MANAGER.get_contributor_endpoint(SERVICE_MANAGER.FDSNSTATION, 'EIDA node ODC'))

    def testContributors(self):
        self.assertFalse(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test'))
        self.assertFalse(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test'))
        self.assertFalse(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.MACROSEISMIC, 'test'))
        SERVICE_MANAGER.set_contributors(SERVICE_MANAGER.FDSNSTATION, 'test', ['a', 'b'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test'), ['a', 'b'])
        self.assertFalse(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test2'))
        SERVICE_MANAGER.set_contributors(SERVICE_MANAGER.FDSNSTATION, 'test2', ['c', 'd'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test'), ['a', 'b'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test2'), ['c', 'd'])
        SERVICE_MANAGER.set_contributors(SERVICE_MANAGER.MACROSEISMIC, 'test', ['e', 'f'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test'), ['a', 'b'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.FDSNSTATION, 'test2'), ['c', 'd'])
        self.assertEqual(SERVICE_MANAGER.get_contributors(SERVICE_MANAGER.MACROSEISMIC, 'test'), ['e', 'f'])


if __name__ == "__main__":
    suite = unittest.makeSuite(QQuakeServiceManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
