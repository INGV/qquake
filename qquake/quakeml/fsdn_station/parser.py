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

from qgis.PyQt.QtCore import (
    QByteArray
)
from qgis.PyQt.QtXml import QDomDocument

from qquake.services import SERVICE_MANAGER
from .fdsn import Fdsn
from ..fields import get_service_fields


class FDSNStationXMLParser:
    """
    FDSNStationXML parser
    """

    @staticmethod
    def parse(content: QByteArray) -> Fdsn:
        """
        Parses content
        """
        doc = QDomDocument()
        doc.setContent(content)

        return Fdsn.from_element(doc.documentElement())

    @staticmethod
    def remap_attribute_name(attribute: str) -> str:
        """
        Returns a remapped attribute name (i.e. accounting for user-defined output attribute names)
        """
        if not attribute:
            return attribute
        return get_service_fields(SERVICE_MANAGER.FDSNSTATION, [attribute]).at(0).name()
