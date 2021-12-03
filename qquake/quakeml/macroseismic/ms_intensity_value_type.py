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


class MsItensityValueType(QuakeMlElement):
    """
    MsItensityValueType
    """

    def __init__(self,
                 _class,
                 numeric,
                 text):
        self._class = _class
        self.numeric = numeric
        self.text = text

    @staticmethod
    def from_element(element: QDomElement) -> 'MsItensityValueType':
        """
        Constructs a MsItensityValueType from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        return MsItensityValueType(_class=parser.string('ms:class', is_attribute=False, optional=True),
                                   numeric=parser.float('ms:numeric', optional=True),
                                   text=parser.string('ms:text', is_attribute=False, optional=True),
                                   )
