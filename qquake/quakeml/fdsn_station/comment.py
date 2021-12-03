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


class Comment(QuakeMlElement):
    """
    Container for a comment or log entry. Corresponds to SEED blockettes 31, 51 and 59.
    """

    def __init__(self,
                 value,
                 begin_effective_time,
                 end_effective_time,
                 author,
                 _id,
                 subject
                 ):
        self.Value = value
        self.BeginEffectiveTime = begin_effective_time
        self.EndEffectiveTime = end_effective_time
        self.Author = author
        self.Id = _id
        self.subject = subject

    @staticmethod
    def from_element(element: QDomElement) -> 'Comment':
        """
        Constructs a DataAvailability from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return Comment(
            value=parser.string('Value', optional=False),
            begin_effective_time=parser.datetime('BeginEffectiveTime', optional=True),
            end_effective_time=parser.datetime('EndEffectiveTime', optional=True),
            author=parser.person('Author', optional=True),
            _id=parser.int('id', is_attribute=True, optional=True),
            subject=parser.string('subject', is_attribute=True, optional=True)
        )
