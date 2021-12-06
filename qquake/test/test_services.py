# coding=utf-8
"""Service manager test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import unittest

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


if __name__ == '__main__':
    unittest.main()
