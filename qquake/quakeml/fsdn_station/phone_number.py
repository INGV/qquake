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


class PhoneNumber(QuakeMlElement):
    """
    PhoneNumber
    """

    def __init__(self,
                 country_code,
                 area_code,
                 phone_number,
                 description):
        self.CountryCode = country_code
        self.AreaCode = area_code
        self.PhoneNumber = phone_number
        self.description = description

    @staticmethod
    def from_element(element: QDomElement) -> 'PhoneNumber':
        """
        Constructs a Person from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return PhoneNumber(
            country_code=parser.int('CountryCode', optional=True),
            area_code=parser.int('AreaCode', optional=True),
            phone_number=parser.string('PhoneNumber', optional=False),
            description=parser.string('description', optional=True)
        )
