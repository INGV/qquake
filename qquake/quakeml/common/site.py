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


class Site(QuakeMlElement):
    """
    Site
    """

    def __init__(self, Name, Description, Town, County, Region, Country):
        self.Name = Name
        self.Description = Description
        self.Town = Town
        self.County = County
        self.Region = Region
        self.Country = Country

    @staticmethod
    def from_element(element: QDomElement) -> 'Site':
        """
        Constructs a Site from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return Site(Name=parser.string('Name'),
                    Description=parser.string('Description', optional=True),
                    Town=parser.string('Town', optional=True),
                    County=parser.string('County', optional=True),
                    Region=parser.string('Region', optional=True),
                    Country=parser.string('Country', optional=True))
