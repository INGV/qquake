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
from ..common import Comment


class Magnitude(QuakeMlElement):
    """
    Magnitude
    """

    def __init__(self,
                 publicID,
                 mag,
                 magnitude_type,
                 originID,
                 methodID,
                 stationCount,
                 azimuthalGap,
                 evaluationMode,
                 evaluationStatus,
                 comments,
                 creationInfo):
        self.publicID = publicID
        self.mag = mag
        self.originID = originID
        self.methodID = methodID
        self.azimuthalGap = azimuthalGap
        self.stationCount = stationCount
        self.stationCount = stationCount
        self.evaluationMode = evaluationMode
        self.type = magnitude_type
        self.evaluationStatus = evaluationStatus
        self.comments = comments
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element: QDomElement) -> 'Magnitude':
        """
        Constructs a Magnitude from a DOM element
        """
        comment_nodes = element.elementsByTagName('comment')
        comments = []
        for e in range(comment_nodes.length()):
            comments.append(Comment.from_element(comment_nodes.at(e).toElement()))

        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)
        return Magnitude(publicID=parser.string('publicID', is_attribute=True),
                         mag=parser.real_quantity('mag', optional=False),
                         magnitude_type=parser.string('type'),
                         originID=parser.resource_reference('originID'),
                         methodID=parser.resource_reference('methodID'),
                         stationCount=parser.int('stationCount'),
                         azimuthalGap=parser.float('azimuthalGap'),
                         evaluationMode=parser.string('evaluationMode'),
                         evaluationStatus=parser.string('evaluationStatus'),
                         comments=comments,
                         creationInfo=parser.creation_info('creationInfo'))
