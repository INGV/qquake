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


class Person(QuakeMlElement):
    """
    Person
    """

    def __init__(self, Name, Agency, Email, Phone):
        self.Name = Name
        self.Agency = Agency
        self.Email = Email
        self.Phone = Phone

    @staticmethod
    def from_element(element: QDomElement) -> 'Person':
        """
        Constructs a Person from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return Person(Name=parser.string('Name', optional=True),
                      Agency=parser.string('Agency', optional=True),
                      Email=parser.string('Email', optional=True),
                      Phone=parser.phone_number('Phone', optional=True))
