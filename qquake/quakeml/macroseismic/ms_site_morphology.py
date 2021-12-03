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


class MsSiteMorphology(QuakeMlElement):
    """
    MsSiteMorphology
    """

    def __init__(self,  # pylint: disable=too-many-locals
                 basinFlagLiteratureSource,
                 bedrockDepth,
                 bedrockDepthLiteratureSource,
                 geologicalSurfaceAge,
                 geologicalUnit,
                 groundwaterDepth,
                 creationInfo,
                 groundwaterDepthLiteratureSource,
                 morphology,
                 morphologyLiteratureSource,
                 referenceBorehole,
                 sedimentaryBasinName,
                 siteClassDescription,
                 siteClassEC8,
                 siteClassEC8LiteratureSource,
                 siteClassSIA261,
                 siteClassSIA261Source,
                 SurfaceLayerGranularity):
        self.basinFlagLiteratureSource = basinFlagLiteratureSource
        self.bedrockDepth = bedrockDepth
        self.bedrockDepthLiteratureSource = bedrockDepthLiteratureSource
        self.geologicalSurfaceAge = geologicalSurfaceAge
        self.geologicalUnit = geologicalUnit
        self.groundwaterDepth = groundwaterDepth
        self.groundwaterDepthLiteratureSource = groundwaterDepthLiteratureSource
        self.morphology = morphology
        self.creationInfo = creationInfo
        self.morphologyLiteratureSource = morphologyLiteratureSource
        self.referenceBorehole = referenceBorehole
        self.sedimentaryBasinName = sedimentaryBasinName
        self.siteClassDescription = siteClassDescription
        self.siteClassEC8 = siteClassEC8
        self.siteClassEC8LiteratureSource = siteClassEC8LiteratureSource
        self.siteClassSIA261 = siteClassSIA261
        self.siteClassSIA261Source = siteClassSIA261Source
        self.SurfaceLayerGranularity = SurfaceLayerGranularity

    @staticmethod
    def from_element(element: QDomElement) -> 'MsSiteMorphology':
        """
        Constructs a MsSiteMorphology from a DOM element
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

        assert False, 'Not implemented'
        return MsSiteMorphology(basinFlagLiteratureSource=parser.string('ms:basinFlagLiteratureSource', optional=True),
                                bedrockDepth=parser.int('ms:bedrockDepth', optional=True),
                                bedrockDepthLiteratureSource=parser.string('ms:bedrockDepthLiteratureSource',
                                                                           optional=True),
                                geologicalSurfaceAge=parser.int_quantity('ms:geologicalSurfaceAge', optional=True),
                                geologicalUnit=parser.string('ms:geologicalUnit', optional=True),
                                groundwaterDepth=parser.int('ms:groundwaterDepth', optional=True),
                                groundwaterDepthLiteratureSource=parser.string('ms:groundwaterDepthLiteratureSource',
                                                                               optional=True),
                                morphology=parser.string('ms:morphology', optional=True),
                                morphologyLiteratureSource=parser.string('ms:morphologyLiteratureSource',
                                                                         optional=True),
                                referenceBorehole=parser.string('ms:referenceBorehole', optional=True),
                                sedimentaryBasinName=parser.string('ms:sedimentaryBasinName', optional=True),
                                siteClassDescription=parser.string('ms:siteClassDescription', optional=True),
                                siteClassEC8=parser.string('ms:siteClassEC8', optional=True),
                                siteClassEC8LiteratureSource=parser.string('ms:siteClassEC8LiteratureSource',
                                                                           optional=True),
                                siteClassSIA261=parser.string('ms:siteClassSIA261', optional=True),
                                siteClassSIA261Source=parser.string('ms:siteClassSIA261Source', optional=True),
                                SurfaceLayerGranularity=parser.string('ms:SurfaceLayerGranularity', optional=True),
                                creationInfo=None)
