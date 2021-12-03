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


class DataAvailabilityExtent(QuakeMlElement):
    """
    A type for describing data availability extents, the earliest and latest data available. No information is included about the continuity of the data is included or implied.
    """

    def __init__(self,
                 start,
                 end):
        self.start = start
        self.end = end

    @staticmethod
    def from_element(element: QDomElement) -> 'DataAvailabilityExtent':
        """
        Constructs a DataAvailabilityExtent from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return DataAvailabilityExtent(
            start=parser.datetime('start', optional=False, is_attribute=True),
            end=parser.datetime('end', optional=False, is_attribute=True)
        )
