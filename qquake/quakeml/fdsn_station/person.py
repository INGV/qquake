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
    Representation of a person's contact information. A person can belong
    to multiple agencies and have multiple email addresses and phone numbers.
    """

    def __init__(self,
                 name,
                 agency,
                 email,
                 phone):
        self.Name = name
        self.Agency = agency
        self.Email = email
        self.Phone = phone

    @staticmethod
    def from_element(element: QDomElement) -> 'Person':
        """
        Constructs a Person from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return Person(
            name=parser.string('Name', optional=True),
            agency=parser.string('Agency', optional=True),
            email=parser.string('Email', optional=True),
            phone=parser.phone_number('Phone', optional=True)
        )
