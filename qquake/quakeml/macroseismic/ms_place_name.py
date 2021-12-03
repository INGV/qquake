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


class MsPlaceName(QuakeMlElement):
    """
    MsPlaceName
    """

    def __init__(self,
                 name,
                 ms_type,
                 alternateType,
                 language,
                 epoch):
        self.name = name
        self.type = ms_type
        self.alternateType = alternateType
        self.language = language
        self.epoch = epoch

    @staticmethod
    def from_element(element: QDomElement) -> 'MsPlaceName':
        """
        Constructs a MsPlaceName from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        return MsPlaceName(name=parser.string('ms:name', is_attribute=False, optional=False),
                           ms_type=parser.string('ms:type', is_attribute=False, optional=True),
                           alternateType=parser.string('ms:alternateType', is_attribute=False, optional=True),
                           language=parser.string('ms:language', is_attribute=False, optional=True),
                           epoch=parser.string('ms:epoch', is_attribute=False, optional=True))
