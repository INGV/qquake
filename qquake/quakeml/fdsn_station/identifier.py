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


class Identifier(QuakeMlElement):
    """
    A type to document persistent identifiers. Identifier
    values should be specified without a URI scheme (prefix), instead the
    identifer type is documented as an attribute.
    """

    def __init__(self,
                 value,
                 _type
                 ):
        self.Value = value
        self.Type = _type

    @staticmethod
    def from_element(element: QDomElement) -> 'Identifier':
        """
        Constructs a Identifier from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return Identifier(
            value=parser.text(),
            _type=parser.string('type', is_attribute=True)
        )
