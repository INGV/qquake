# coding=utf-8
"""Service manager test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import unittest

from qgis.PyQt.QtTest import QSignalSpy

from qquake.services import ServiceManager


class TestServiceManager(unittest.TestCase):
    """
    Test service manager
    """

    def test_styles(self):
        """
        Test retrieving styles from service manager
        """
        manager = ServiceManager()
        self.assertIn('square_colors', manager.PRESET_STYLES)
        self.assertIn('circles_red', manager.PRESET_STYLES)

    def test_styles_for_service_type(self):
        """
        Test retrieving styles for a specific service type
        """
        manager = ServiceManager()
        self.assertIn('square_colors', manager.styles_for_service_type(ServiceManager.FDSNEVENT))
        self.assertNotIn('AHEAD_intensities', manager.styles_for_service_type(ServiceManager.FDSNEVENT))

        self.assertIn('AHEAD_intensities', manager.styles_for_service_type(ServiceManager.MACROSEISMIC))
        self.assertNotIn('square_colors', manager.styles_for_service_type(ServiceManager.MACROSEISMIC))

        self.assertIn('stations', manager.styles_for_service_type(ServiceManager.FDSNSTATION))
        self.assertNotIn('square_colors', manager.styles_for_service_type(ServiceManager.FDSNSTATION))

    def test_user_styles(self):
        """
        Test user styles
        """
        manager = ServiceManager()

        manager.remove_user_style('test')
        self.assertNotIn('test', manager.user_styles())

        spy = QSignalSpy(manager.user_styles_changed)
        manager.add_user_style('test', ServiceManager.MACROSEISMIC, 'http://me')
        self.assertEqual(len(spy), 1)

        # create a second manager to test that the style is persisted
        manager2 = ServiceManager()
        self.assertIn('test', manager2.user_styles())

        self.assertIn('test', manager.styles_for_service_type(ServiceManager.MACROSEISMIC))
        self.assertNotIn('test', manager.styles_for_service_type(ServiceManager.FDSNEVENT))
        self.assertNotIn('test', manager.styles_for_service_type(ServiceManager.FDSNSTATION))

        self.assertIn('test', manager2.styles_for_service_type(ServiceManager.MACROSEISMIC))
        self.assertNotIn('test', manager2.styles_for_service_type(ServiceManager.FDSNEVENT))
        self.assertNotIn('test', manager2.styles_for_service_type(ServiceManager.FDSNSTATION))

        manager.remove_user_style('test')
        self.assertEqual(len(spy), 2)
        manager.remove_user_style('test')
        self.assertEqual(len(spy), 2)

        manager2 = ServiceManager()
        self.assertNotIn('test', manager2.user_styles())


if __name__ == '__main__':
    unittest.main()
