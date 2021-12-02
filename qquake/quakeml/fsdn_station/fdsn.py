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


class Fdsn(QuakeMlElement):
    """
    Root type for FDSN
    """

    def __init__(self,
                 source,
                 sender,
                 module,
                 module_uri,
                 created,
                 networks,
                 schema_version
                 ):
        self.Source = source
        self.Sender = sender
        self.Module = module
        self.ModuleURI = module_uri
        self.Created = created
        self.networks = networks
        self.schemaVersion = schema_version

    @staticmethod
    def from_element(element: QDomElement) -> 'Fdsn':
        """
        Constructs a DataAvailability from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)

        network_elements = element.elementsByTagName('Network')

        from .network import Network  # pylint: disable=import-outside-toplevel
        networks = []
        for e in range(network_elements.length()):
            network_element = network_elements.at(e).toElement()
            networks.append(Network.from_element(network_element))

        return Fdsn(
            source=parser.string('Source'),
            sender=parser.string('Sender', optional=True),
            module=parser.string('Module', optional=True),
            module_uri=parser.string('ModuleURI', optional=True),
            created=parser.datetime('Created', optional=False),
            networks=networks,
            schema_version=parser.float('schemaVersion', is_attribute=True)
        )
