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


class OriginUncertainty(QuakeMlElement):
    """
    OriginUncertainty
    """

    def __init__(self,
                 horizontalUncertainty,
                 minHorizontalUncertainty,
                 maxHorizontalUncertainty,
                 azimuthMaxHorizontalUncertainty,
                 confidenceEllipsoid,
                 preferredDescription,
                 confidenceLevel):
        self.horizontalUncertainty = horizontalUncertainty
        self.minHorizontalUncertainty = minHorizontalUncertainty
        self.maxHorizontalUncertainty = maxHorizontalUncertainty
        self.azimuthMaxHorizontalUncertainty = azimuthMaxHorizontalUncertainty
        self.confidenceEllipsoid = confidenceEllipsoid
        self.preferredDescription = preferredDescription
        self.confidenceLevel = confidenceLevel

    @staticmethod
    def from_element(element: QDomElement) -> 'OriginUncertainty':
        """
        Constructs a OriginUncertainty from a DOM element
        """
        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)
        return OriginUncertainty(
            horizontalUncertainty=parser.float('horizontalUncertainty'),
            minHorizontalUncertainty=parser.float('minHorizontalUncertainty'),
            maxHorizontalUncertainty=parser.float('maxHorizontalUncertainty'),
            azimuthMaxHorizontalUncertainty=parser.float('azimuthMaxHorizontalUncertainty'),
            confidenceEllipsoid=parser.confidence_ellipsoid('confidenceEllipsoid'),
            preferredDescription=parser.origin_uncertainty_description('preferredDescription'),
            confidenceLevel=parser.float('confidenceLevel')
        )
