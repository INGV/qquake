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

from typing import Optional

from ..element_parser import ElementParser


class FDSNEventElementParser(ElementParser):
    """
    FDSN Event element parser
    """

    def confidence_ellipsoid(self, attribute, optional=True) -> Optional['ConfidenceEllipsoid']:
        """
        Returns an attributes as a ConfidenceEllipsoid
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .confidence_ellipsoid import ConfidenceEllipsoid  # pylint: disable=import-outside-toplevel,cyclic-import
        return ConfidenceEllipsoid.from_element(child)

    def origin_uncertainty_description(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attributes as an origin uncertainty string
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def origin_quality(self, attribute, optional=True) -> Optional['OriginQuality']:
        """
        Returns an attribute as a OriginQuality
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .origin_quality import OriginQuality  # pylint: disable=import-outside-toplevel,cyclic-import
        return OriginQuality.from_element(child)

    def origin_type(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attribute as a origin type
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def origin_depth_type(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attribute as an origin depth type
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()
