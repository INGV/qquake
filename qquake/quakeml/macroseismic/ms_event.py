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


class MsEvent(QuakeMlElement):
    """
    MacroseismicEvent
    """

    def __init__(self,
                 publicID,
                 mdpSetReference,
                 eventReference,
                 preferredMDPSetID,
                 preferredMacroseismicOriginID,
                 creationInfo):
        self.publicID = publicID
        self.mdpSetReference = mdpSetReference
        self.eventReference = eventReference
        self.preferredMDPSetID = preferredMDPSetID
        self.preferredMacroseismicOriginID = preferredMacroseismicOriginID
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element: QDomElement) -> 'MsEvent':
        """
        Constructs a MsEvent from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        return MsEvent(publicID=parser.string('publicID', is_attribute=True, optional=False),
                       mdpSetReference=parser.string('ms:mdpSetReference', optional=True),
                       eventReference=parser.string('ms:eventReference', optional=True),
                       preferredMDPSetID=parser.string('ms:preferredMDPSetID', optional=True),
                       preferredMacroseismicOriginID=parser.string('ms:preferredMacroseismicOriginID', optional=True),
                       creationInfo=parser.creation_info('ms:creationInfo', optional=True))
