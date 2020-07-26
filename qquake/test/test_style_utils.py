# coding=utf-8
"""StyleUtils test.

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

from qgis.core import (
    QgsVectorLayer,
    QgsGraduatedSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsSingleSymbolRenderer
)

from qquake.style_utils import StyleUtils

from qquake.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class QQuakeStyleUtilsTest(unittest.TestCase):
    """Test StyleUtils works."""

    def testApply(self):
        layer = QgsVectorLayer("Point?crs=EPSG:27700&field=field1:string&field=field2:string", "points", "memory")
        self.assertTrue(layer.isValid())

        self.assertIsInstance(layer.renderer(), QgsSingleSymbolRenderer)
        res = StyleUtils.fetch_and_apply_style(layer, 'hasdasdasdasd')
        self.assertIsInstance(layer.renderer(), QgsSingleSymbolRenderer)
        self.assertEqual(res, 'Error while fetching QML style: Protocol "" is unknown')

        self.assertIsNone(
            StyleUtils.fetch_and_apply_style(layer, 'https://www.emidius.eu/AHEAD/symbols/SHEEC_symbols_wfs.qml'))
        self.assertIsInstance(layer.renderer(), QgsGraduatedSymbolRenderer)
        self.assertEqual(layer.renderer().classAttribute(), 'Mw')

        # with style attribute override
        self.assertIsNone(
            StyleUtils.fetch_and_apply_style(layer, 'https://www.emidius.eu/AHEAD/symbols/SHEEC_symbols_wfs.qml',
                                             'field2'))
        self.assertIsInstance(layer.renderer(), QgsGraduatedSymbolRenderer)
        self.assertEqual(layer.renderer().classAttribute(), 'field2')

    def testUpdateClassAttribute(self):
        layer = QgsVectorLayer("Point?crs=EPSG:27700&field=field1:string&field=field2:string", "points", "memory")
        self.assertTrue(layer.isValid())

        # should do nothing, but no exception at least..
        StyleUtils.update_class_attribute(layer, 'field2')

        # graduated renderer
        layer.setRenderer(QgsGraduatedSymbolRenderer('field1'))
        self.assertEqual(layer.renderer().classAttribute(), 'field1')
        StyleUtils.update_class_attribute(layer, 'field2')
        self.assertEqual(layer.renderer().classAttribute(), 'field2')

        # categorized renderer
        layer.setRenderer(QgsCategorizedSymbolRenderer('field2'))
        self.assertEqual(layer.renderer().classAttribute(), 'field2')
        StyleUtils.update_class_attribute(layer, 'field1')
        self.assertEqual(layer.renderer().classAttribute(), 'field1')


if __name__ == "__main__":
    suite = unittest.makeSuite(QQuakeStyleUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
