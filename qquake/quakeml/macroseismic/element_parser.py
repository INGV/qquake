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


class MacroseismicElementParser(ElementParser):
    """
    Macroseismic element parser
    """

    def ms_intensity_value_type(self, attribute, optional=True) -> Optional['MsItensityValueType']:
        """
        Returns an attribute as a MsItensityValueType
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .ms_intensity_value_type import MsItensityValueType  # pylint: disable=import-outside-toplevel,cyclic-import
        return MsItensityValueType.from_element(child)

    def ms_intensity(self, attribute, optional=True) -> Optional['MsIntensity']:
        """
        Returns an attribute as a MsIntensity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .ms_intensity import MsIntensity  # pylint: disable=import-outside-toplevel,cyclic-import
        return MsIntensity.from_element(child)

    def ms_placename(self, attribute, optional=True) -> Optional['MsPlaceName']:
        """
        Returns an attribute as a MsPlaceName
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .ms_place_name import MsPlaceName  # pylint: disable=import-outside-toplevel,cyclic-import
        return MsPlaceName.from_element(child)

    def ms_sitemorphology(self, attribute, optional=True) -> Optional['MsSiteMorphology']:
        """
        Returns an attribute as a MsSiteMorphology
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .ms_site_morphology import MsSiteMorphology  # pylint: disable=import-outside-toplevel,cyclic-import
        return MsSiteMorphology.from_element(child)
