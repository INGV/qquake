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
from .ms_place_name import MsPlaceName


class MsPlace(QuakeMlElement):
    """
    MsPlace
    """

    def __init__(self,  # pylint: disable=too-many-locals
                 publicID,
                 name: List,
                 preferredName,
                 referenceLatitude,
                 referenceLongitude,
                 horizontalUncertainty,
                 geometry,
                 externalGazetteer,
                 ms_type,
                 zipCode,
                 altitude,
                 isoCountryCode,
                 literatureSource,
                 siteMorphology,
                 creationInfo,
                 epoch):
        self.publicID = publicID
        self.name = name  # one to many
        self.preferredName = preferredName
        self.referenceLatitude = referenceLatitude
        self.referenceLongitude = referenceLongitude
        self.horizontalUncertainty = horizontalUncertainty
        self.geometry = geometry
        self.externalGazetteer = externalGazetteer
        self.type = ms_type
        self.zipCode = zipCode
        self.altitude = altitude
        self.isoCountryCode = isoCountryCode
        self.literatureSource = literatureSource
        self.siteMorphology = siteMorphology
        self.creationInfo = creationInfo
        self.epoch = epoch

    @staticmethod
    def from_element(element: QDomElement) -> 'MsPlace':
        """
        Constructs a MsPlace from a DOM element
        """
        from .element_parser import MacroseismicElementParser  # pylint: disable=import-outside-toplevel
        parser = MacroseismicElementParser(element)

        names = []
        place_name_node = element.firstChildElement('ms:name')
        while not place_name_node.isNull():
            names.append(MsPlaceName.from_element(place_name_node))
            place_name_node = place_name_node.nextSiblingElement('ms:name')

        return MsPlace(publicID=parser.string('publicID', is_attribute=True, optional=False),
                       preferredName=parser.ms_placename('ms:preferredName', optional=True),
                       name=names,
                       referenceLatitude=parser.real_quantity('ms:referenceLatitude'),
                       referenceLongitude=parser.real_quantity('ms:referenceLongitude'),
                       horizontalUncertainty=parser.float('ms:horizontalUncertainty', optional=True),
                       geometry=parser.string('ms:geometry', optional=True),
                       externalGazetteer=parser.string('ms:externalGazetteer', optional=True),
                       ms_type=parser.string('ms:type', optional=True),
                       zipCode=parser.string('ms:zipCode', optional=True),
                       altitude=parser.float('ms:altitude', optional=True),
                       isoCountryCode=parser.string('ms:isoCountryCode', optional=True),
                       literatureSource=parser.string('ms:literatureSource', optional=True),
                       siteMorphology=parser.ms_sitemorphology('ms:siteMorphology', optional=True),
                       creationInfo=parser.creation_info('ms:creationInfo', optional=True),
                       epoch=parser.epoch('ms:epoch', optional=True))
