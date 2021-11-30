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

from typing import List

from qgis.PyQt.QtCore import (
    QByteArray
)
from qgis.PyQt.QtXml import QDomDocument

from qquake.services import SERVICE_MANAGER

from .network import Network
from ..fields import get_service_fields


class FDSNStationXMLParser:
    """
    FDSNStationXML parser
    """

    @staticmethod
    def parse(content: QByteArray) -> List[Network]:
        """
        Parses content
        """
        doc = QDomDocument()
        doc.setContent(content)
        network_elements = doc.elementsByTagName('Network')

        networks = []
        for e in range(network_elements.length()):
            network_element = network_elements.at(e).toElement()
            networks.append(Network.from_element(network_element))

        return networks

    @staticmethod
    def remap_attribute_name(attribute: str) -> str:
        """
        Returns a remapped attribute name (i.e. accounting for user-defined output attribute names)
        """
        if not attribute:
            return attribute
        return get_service_fields(SERVICE_MANAGER.FDSNSTATION, [attribute]).at(0).name()
