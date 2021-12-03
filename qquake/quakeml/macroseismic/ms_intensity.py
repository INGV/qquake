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


class MsIntensity(QuakeMlElement):
    """
    MsIntensity
    """

    def __init__(self,
                 macroseismicScale,
                 expectedIntensity,
                 maximalCredibleIntensity,
                 minimalCredibleIntensity):
        self.macroseismicScale = macroseismicScale
        self.expectedIntensity = expectedIntensity
        self.maximalCredibleIntensity = maximalCredibleIntensity
        self.minimalCredibleIntensity = minimalCredibleIntensity

    @staticmethod
    def from_element(element: QDomElement) -> 'MsIntensity':
        """
        Constructs an MsIntensity from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        return MsIntensity(macroseismicScale=parser.string('ms:macroseismicScale', is_attribute=False, optional=False),
                           expectedIntensity=parser.ms_intensity_value_type('ms:expectedIntensity'),
                           maximalCredibleIntensity=parser.ms_intensity_value_type('ms:maximalCredibleIntensity',
                                                                                   optional=True),
                           minimalCredibleIntensity=parser.ms_intensity_value_type('ms:minimalCredibleIntensity',
                                                                                   optional=True))
