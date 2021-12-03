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


class EventDescription(QuakeMlElement):
    """
    EventDescription
    """

    def __init__(self, text, event_description_type):
        self.text = text
        self.type = event_description_type

    @staticmethod
    def from_element(element: QDomElement) -> 'EventDescription':
        """
        Constructs a EventDescription from a DOM element
        """
        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)
        return EventDescription(text=parser.string('text'), event_description_type=parser.string('type'))
