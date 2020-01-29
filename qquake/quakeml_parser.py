# -*- coding: utf-8 -*-
"""QQuake- QuakeML Parser

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2020 by Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Copyright 2020, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    NULL
)

from qquake.qquake_defs import (
    fdsn_event_fields
)


class ElementParser:

    def __init__(self, element):
        self.element = element

    def string(self, attribute, optional=True, is_attribute=False):
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                return None
            else:
                return self.element.attribute(attribute)
        else:
            child = self.element.elementsByTagName(attribute).at(0).toElement()
            if optional and child.isNull():
                return None

            return child.text()

    def resource_reference(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return child.text()

    def datetime(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        # TODO - return as QDateTime
        return child.text()

    def time_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        # TODO - return as QDateTime
        return child.elementsByTagName('value').at(0).toElement().text()

    def real_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional:
            return RealQuantity.from_element(child) if not child.isNull() else None
        else:
            return RealQuantity.from_element(child)

    def float(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional:
            return float(child.text()) if not child.isNull() else None
        else:
            return float(child.text())

    def int(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional:
            return int(child.text()) if not child.isNull() else None
        else:
            return int(child.text())

    def boolean(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional:
            return bool(child.text()) if not child.isNull() else None
        else:
            return bool(child.text())

    def creation_info(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return CreationInfo.from_element(child)


class CreationInfo:

    def __init__(self,
                 agencyID,
                 agencyURI,
                 author,
                 authorURI,
                 creationTime,
                 version):
        self.agencyID = agencyID
        self.agencyURI = agencyURI
        self.author = author
        self.authorURI = authorURI
        self.creationTime = creationTime
        self.version = version

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return CreationInfo(agencyID=parser.string('agencyID'),
                            agencyURI=parser.string('agencyURI'),
                            author=parser.string('author'),
                            authorURI=parser.string('authorURI'),
                            creationTime=parser.datetime('creationTime'),
                            version=parser.string('version'))


class EventDescription:

    def __init__(self, text, type):
        self.text = text
        self.type = type

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return EventDescription(text=parser.string('text'), type=parser.string('type'))


class Origin:

    def __init__(self,
                 publicID,
                 time,
                 longitude,
                 latitude,
                 depth,
                 depthType,
                 timeFixed,
                 epicenterFixed,
                 referenceSystemID,
                 methodID,
                 earthModeID,
                 compositeTime,
                 quality,
                 type,
                 region,
                 evaluationMode,
                 evaluationStatus,
                 comment,
                 creationInfo):
        self.publicID = publicID
        self.time = time
        self.longitude = longitude
        self.latitude = latitude
        self.depth = depth
        self.depthType = depthType
        self.timeFixed = timeFixed
        self.epicenterFixed = epicenterFixed
        self.referenceSystemID = referenceSystemID
        self.methodID = methodID
        self.earthModeID = earthModeID
        self.compositeTime = compositeTime
        self.quality = quality
        self.type = type
        self.region = region
        self.evaluationMode = evaluationMode
        self.evaluationStatus = evaluationStatus
        self.comment = comment
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return Origin(publicID=parser.string('publicID', optional=False, is_attribute=False),
                      time=parser.time_quantity('time'),
                      longitude=parser.real_quantity('longitude'),
                      latitude=parser.real_quantity('latitude'),
                      depth=parser.real_quantity('depth', optional=True),
                      depthType=None,
                      timeFixed=parser.boolean('timeFixed'),
                      epicenterFixed=parser.boolean('epicenterFixed'),
                      referenceSystemID=parser.resource_reference('referenceSystemID'),
                      methodID=parser.resource_reference('methodID'),
                      earthModeID=parser.resource_reference('earthModeID'),
                      compositeTime=None,
                      quality=None,
                      type=None,
                      region=parser.string('region'),
                      evaluationMode=parser.string('evaluationMode'),
                      evaluationStatus=parser.string('evaluationStatus'),
                      comment=None,
                      creationInfo=parser.creation_info('creationInfo'))


class RealQuantity:

    def __init__(self,
                 value,
                 uncertainty,
                 lowerUncertainty,
                 upperUncertainty,
                 confidenceLevel):
        self.value = value
        self.uncertainty = uncertainty
        self.lowerUncertainty = lowerUncertainty
        self.upperUncertainty = upperUncertainty
        self.confidenceLevel = confidenceLevel

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return RealQuantity(value=parser.float('value', optional=False),
                            uncertainty=parser.float('uncertainty'),
                            lowerUncertainty=parser.float('lowerUncertainty'),
                            upperUncertainty=parser.float('upperUncertainty'),
                            confidenceLevel=parser.float('confidenceLevel'))


class Magnitude:

    def __init__(self,
                 publicID,
                 mag,
                 type,
                 originID,
                 methodID,
                 stationCount,
                 azimuthalGap,
                 evalutionMode,
                 evaluationStatus,
                 comment,
                 creationInfo):
        self.publicID = publicID
        self.mag = mag
        self.originID = originID
        self.methodID = methodID
        self.azimuthalGap = azimuthalGap
        self.stationCount = stationCount
        self.stationCount = stationCount
        self.evalutionMode = evalutionMode
        self.type = type
        self.evaluationStatus = evaluationStatus
        self.comment = comment
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return Magnitude(publicID=parser.string('publicID', is_attribute=True),
                         mag=parser.real_quantity('mag', optional=False),
                         type=parser.string('type'),
                         originID=parser.resource_reference('originID'),
                         methodID=parser.resource_reference('methodID'),
                         stationCount=parser.int('stationCount'),
                         azimuthalGap=parser.float('azimuthalGap'),
                         evalutionMode=parser.string('evaluationMode'),
                         evaluationStatus=parser.string('evaluationStatus'),
                         comment=None,
                         creationInfo=parser.creation_info('creationInfo'))


class Event:

    def __init__(self, publicID,
                 type,
                 typeCertainty,
                 description,
                 preferredOriginID,
                 preferredMagnitudeID,
                 preferredFocalMechanismID,
                 comment,
                 creationInfo,
                 origins,
                 magnitudes):
        self.publicID = publicID
        self.type = type
        self.typeCertainty = typeCertainty
        self.description = description
        self.preferredOriginID = preferredOriginID
        self.preferredMagnitudeID = preferredMagnitudeID
        self.preferredFocalMechanismID = preferredFocalMechanismID
        self.comment = comment
        self.creationInfo = creationInfo
        self.origins = origins
        self.magnitudes = magnitudes

    def to_features(self):
        fields = QgsFields()
        for k, v in fdsn_event_fields.items():
            fields.append(QgsField(k, v))

        features = []
        for o in self.origins:
            f = QgsFeature(fields)
            f['EventID'] = self.publicID
            f['Time'] = o.time
            f['Latitude'] = o.latitude.value
            f['Longitude'] = o.longitude.value
            f['DepthKm'] = o.depth.value if o.depth else NULL
            f['Author'] = o.creationInfo.author if o.creationInfo else NULL
            f['Catalog'] = NULL  # ?
            f['Contributor'] = NULL  # ?
            f['ContributorID'] = NULL  # ?
            f['MagType'] = NULL  # ?
            f['Magnitude'] = NULL  # ?
            f['MagAuthor'] = NULL  # ?
            f['EventLocationName'] = o.region  # ?

            if o.depth is not None:
                geom = QgsPoint(x=o.longitude.value, y=o.latitude.value, z=-o.depth.value*1000)
            else:
                geom = QgsPoint(x=o.longitude.value, y=o.latitude.value)
            f.setGeometry(QgsGeometry(geom))
            features.append(f)

        return features

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)

        description_nodes = element.elementsByTagName('description')
        descriptions = []
        for e in range(description_nodes.length()):
            descriptions.append(EventDescription.from_element(description_nodes.at(e).toElement()))

        origin_nodes = element.elementsByTagName('origin')
        origins = []
        for e in range(origin_nodes.length()):
            origins.append(Origin.from_element(origin_nodes.at(e).toElement()))

        magnitude_nodes = element.elementsByTagName('magnitude')
        magnitudes = []
        for e in range(magnitude_nodes.length()):
            magnitudes.append(Magnitude.from_element(magnitude_nodes.at(e).toElement()))

        return Event(publicID=parser.string('publicID', is_attribute=True, optional=False),
                     type=parser.string('type'),
                     typeCertainty=parser.string('typeCertainty'),
                     description=descriptions,
                     preferredOriginID=None,
                     preferredMagnitudeID=None,
                     preferredFocalMechanismID=None,
                     comment=None,
                     creationInfo=parser.creation_info('creationInfo'),
                     origins=origins,
                     magnitudes=magnitudes)


class QuakeMlParser:
    """
    QuakeML parser
    """

    @staticmethod
    def parse(content):
        doc = QDomDocument()
        doc.setContent(content)
        event_elements = doc.elementsByTagName('event')

        events = []
        for e in range(event_elements.length()):
            event_element = event_elements.at(e).toElement()
            events.append(Event.from_element(event_element))

        return events
