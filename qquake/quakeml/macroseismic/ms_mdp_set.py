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


class MsMdpSet(QuakeMlElement):
    """
    MsMdpSet
    """

    def __init__(self,
                 publicID,
                 relatedMDPSet,
                 comment: List,
                 methodID,
                 mdpCount,
                 maximumIntensity,
                 literatureSource,
                 creationInfo,
                 mdpReferences: List):
        self.publicID = publicID
        self.relatedMDPSet = relatedMDPSet
        self.comment = comment  # one to many
        self.mdpCount = mdpCount
        self.maximumIntensity = maximumIntensity
        self.methodID = methodID
        self.literatureSource = literatureSource
        self.creationInfo = creationInfo
        self.mdpReferences = mdpReferences  # one to many

    @staticmethod
    def from_element(element: QDomElement) -> 'MsMdpSet':
        """
        Constructs an MsMdpSet from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        comments = []
        comment_node = element.firstChildElement('ms:comment')
        while not comment_node.isNull():
            comments.append(Comment.from_element(comment_node))
            comment_node = comment_node.nextSiblingElement('ms:comment')

        mdpReferences = []
        reference_node = element.firstChildElement('ms:mdpReference')
        while not reference_node.isNull():
            mdpReferences.append(reference_node.text())
            reference_node = reference_node.nextSiblingElement('ms:mdpReference')

        return MsMdpSet(publicID=parser.string('publicID', is_attribute=True, optional=False),
                        relatedMDPSet=parser.resource_reference('ms:relatedMDPSet'),
                        comment=comments,
                        mdpCount=parser.int('ms:mdpCount', optional=True),
                        maximumIntensity=parser.ms_intensity('ms:maximumIntensity', optional=True),
                        methodID=parser.resource_reference('ms:methodID', optional=True),
                        literatureSource=parser.string('ms:literatureSource', optional=True),
                        creationInfo=parser.creation_info('ms:creationInfo', optional=True),
                        mdpReferences=mdpReferences)
