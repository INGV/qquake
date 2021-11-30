# -*- coding: utf-8 -*-
"""QuakeML element

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = 'Original authors: Mario Locati, Roberto Vallone, Matteo Ghetta, Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Istituto Nazionale di Geofisica e Vulcanologia (INGV)'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt.QtXml import QDomElement

from ..element import QuakeMlElement


class Equipment(QuakeMlElement):
    """
    Equipment
    """

    def __init__(self, Type, Description, Manufacturer, Vendor, Model, SerialNumber, InstallationDate, RemovalDate,
                 CalibrationDate, resourceId):
        self.Type = Type
        self.Description = Description
        self.Manufacturer = Manufacturer
        self.Vendor = Vendor
        self.Model = Model
        self.SerialNumber = SerialNumber
        self.InstallationDate = InstallationDate
        self.RemovalDate = RemovalDate
        self.CalibrationDate = CalibrationDate
        self.resourceId = resourceId

    @staticmethod
    def from_element(element: QDomElement) -> 'Equipment':
        """
        Constructs Equipment from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return Equipment(Type=parser.string('Type', optional=True),
                         Description=parser.string('Description', optional=True),
                         Manufacturer=parser.string('Manufacturer', optional=True),
                         Vendor=parser.string('Vendor', optional=True),
                         Model=parser.string('Model', optional=True),
                         SerialNumber=parser.string('SerialNumber', optional=True),
                         InstallationDate=parser.datetime('InstallationDate', optional=True),
                         RemovalDate=parser.datetime('RemovalDate', optional=True),
                         CalibrationDate=parser.datetime('CalibrationDate', optional=True),
                         resourceId=parser.string('resourceId', optional=True, is_attribute=True))
