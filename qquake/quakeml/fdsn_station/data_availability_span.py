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


class DataAvailabilitySpan(QuakeMlElement):
    """
    A type for describing data availability spans, with variable continuity.
    The time range described may be based on the request parameters that
    generated the document and not necessarily relate to continuity outside
    of the range. It may also be a smaller time window than the request
    depending on the data characteristics.
    """

    def __init__(self,
                 start,
                 end,
                 number_segments,
                 maximum_time_tear):
        self.start = start
        self.end = end
        self.numberSegments = number_segments
        self.maximumTimeTear = maximum_time_tear

    @staticmethod
    def from_element(element: QDomElement) -> 'DataAvailabilitySpan':
        """
        Constructs a DataAvailabilityExtent from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return DataAvailabilitySpan(
            start=parser.datetime('start', optional=False, is_attribute=True),
            end=parser.datetime('end', optional=False, is_attribute=True),
            number_segments=parser.int('numberSegments', optional=False, is_attribute=True),
            maximum_time_tear=parser.float('maximumTimeTear', optional=True, is_attribute=True),
        )
