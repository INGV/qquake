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


class DataAvailability(QuakeMlElement):
    """
    An type for describing data availability.
    """

    def __init__(self,
                 extent,
                 span
                 ):
        self.Extent = extent
        self.Span = span

    @staticmethod
    def from_element(element: QDomElement) -> 'DataAvailability':
        """
        Constructs a DataAvailability from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        return DataAvailability(
            extent=parser.data_availability_extent('Extent', optional=True),
            span=parser.data_availability_span('Span', optional=True),
        )
