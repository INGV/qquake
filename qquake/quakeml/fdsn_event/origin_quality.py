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


class OriginQuality(QuakeMlElement):
    """
    OriginQuality
    """

    def __init__(self,
                 associatedPhaseCount,
                 usedPhaseCount,
                 associatedStationCount,
                 usedStationCount,
                 depthPhaseCount,
                 standardError,
                 azimuthalGap,
                 secondaryAzimuthalGap,
                 groundTruthLevel,
                 maximumDistance,
                 minimumDistance,
                 medianDistance):
        self.associatedPhaseCount = associatedPhaseCount
        self.usedPhaseCount = usedPhaseCount
        self.associatedStationCount = associatedStationCount
        self.usedStationCount = usedStationCount
        self.depthPhaseCount = depthPhaseCount
        self.standardError = standardError
        self.azimuthalGap = azimuthalGap
        self.secondaryAzimuthalGap = secondaryAzimuthalGap
        self.groundTruthLevel = groundTruthLevel
        self.maximumDistance = maximumDistance
        self.minimumDistance = minimumDistance
        self.medianDistance = medianDistance

    @staticmethod
    def from_element(element: QDomElement) -> 'OriginQuality':
        """
        Constructs a OriginQuality from a DOM element
        """
        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)
        return OriginQuality(
            associatedPhaseCount=parser.int('associatedPhaseCount'),
            usedPhaseCount=parser.int('usedPhaseCount'),
            associatedStationCount=parser.int('associatedStationCount'),
            usedStationCount=parser.int('usedStationCount'),
            depthPhaseCount=parser.int('depthPhaseCount'),
            standardError=parser.float('standardError'),
            azimuthalGap=parser.float('azimuthalGap'),
            secondaryAzimuthalGap=parser.float('secondaryAzimuthalGap'),
            groundTruthLevel=parser.string('groundTruthLevel'),
            maximumDistance=parser.float('maximumDistance'),
            minimumDistance=parser.float('minimumDistance'),
            medianDistance=parser.float('medianDistance'),
        )
