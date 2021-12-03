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


class ConfidenceEllipsoid(QuakeMlElement):
    """
    ConfidenceEllipsoid
    """

    def __init__(self,
                 semiMajorAxisLength,
                 semiMinorAxisLength,
                 semiIntermediateAxisLength,
                 majorAxisPlunge,
                 majorAxisAzimuth,
                 majorAxisRotation):
        self.semiMajorAxisLength = semiMajorAxisLength
        self.semiMinorAxisLength = semiMinorAxisLength
        self.semiIntermediateAxisLength = semiIntermediateAxisLength
        self.majorAxisPlunge = majorAxisPlunge
        self.majorAxisAzimuth = majorAxisAzimuth
        self.majorAxisRotation = majorAxisRotation

    @staticmethod
    def from_element(element: QDomElement) -> 'ConfidenceEllipsoid':
        """
        Constructs a ConfidenceEllipsoid from a DOM element
        """
        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)
        return ConfidenceEllipsoid(
            semiMajorAxisLength=parser.float('semiMajorAxisLength', optional=False),
            semiMinorAxisLength=parser.float('semiMinorAxisLength', optional=False),
            semiIntermediateAxisLength=parser.float('semiIntermediateAxisLength', optional=False),
            majorAxisPlunge=parser.float('majorAxisPlunge', optional=False),
            majorAxisAzimuth=parser.float('majorAxisAzimuth', optional=False),
            majorAxisRotation=parser.float('majorAxisRotation', optional=False))
