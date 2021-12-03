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

from qgis.PyQt.QtXml import QDomElement

from ..element import QuakeMlElement
from ..common import Comment


class MsMdp(QuakeMlElement):
    """
    MsMdp
    """

    def __init__(self,  # pylint: disable=too-many-locals
                 publicID,
                 reportReference,
                 eventReference,
                 placeReference,
                 comment: List,
                 reportCount,
                 reportedTime,
                 methodID,
                 quality,
                 intensity,
                 evaluationMode,
                 evaluationStatus,
                 literatureSource,
                 creationInfo,
                 relatedMDP: List):
        self.publicID = publicID
        self.reportReference = reportReference
        self.eventReference = eventReference
        self.placeReference = placeReference
        self.intensity = intensity
        self.comment = comment  # one to many
        self.reportCount = reportCount
        self.reportedTime = reportedTime
        self.methodID = methodID
        self.quality = quality
        self.evaluationMode = evaluationMode
        self.evaluationStatus = evaluationStatus
        self.literatureSource = literatureSource
        self.creationInfo = creationInfo
        self.relatedMDP = relatedMDP

    @staticmethod
    def from_element(element: QDomElement) -> 'MsMdp':
        """
        Constructs an MsMdp from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        comments = []
        comment_node = element.firstChildElement('ms:comment')
        while not comment_node.isNull():
            comments.append(Comment.from_element(comment_node))
            comment_node = comment_node.nextSiblingElement('ms:comment')

        related = []
        related_node = element.firstChildElement('ms:relatedMDP')
        while not related_node.isNull():
            related.append(related_node.text())
            related_node = related_node.nextSiblingElement('ms:relatedMDP')

        return MsMdp(publicID=parser.string('publicID', is_attribute=True, optional=False),
                     reportReference=parser.resource_reference('ms:reportReference'),
                     eventReference=parser.resource_reference('ms:eventReference'),
                     placeReference=parser.resource_reference('ms:placeReference'),
                     comment=comments,
                     reportCount=parser.int('ms:reportCount', optional=True),
                     reportedTime=parser.time_quantity('ms:reportedTime', optional=True),
                     methodID=parser.resource_reference('ms:methodID', optional=True),
                     quality=parser.string('ms:quality', optional=True),
                     evaluationMode=parser.string('ms:evaluationMode', optional=True),
                     evaluationStatus=parser.string('ms:evaluationStatus', optional=True),
                     literatureSource=parser.string('ms:literatureSource', optional=True),
                     creationInfo=parser.creation_info('ms:creationInfo', optional=True),
                     intensity=parser.ms_intensity('ms:intensity'),
                     relatedMDP=related)
