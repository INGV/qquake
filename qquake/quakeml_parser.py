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
    QgsPointXY,
    NULL
)

from qquake.qquake_defs import (
    fdsn_event_fields
)


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
        agency_id = element.elementsByTagName('agencyID').at(0).toElement().text()
        author = element.elementsByTagName('author').at(0).toElement().text()
        version = element.elementsByTagName('version').at(0).toElement().text()
        author_uri = element.elementsByTagName('authorURI').at(0).toElement().text()
        agency_uri = element.elementsByTagName('agencyURI').at(0).toElement().text()
        creation_time = element.elementsByTagName('creationTime').at(0).toElement().text()

        return CreationInfo(agencyID=agency_id,
                            agencyURI=agency_uri,
                            author=author,
                            authorURI=author_uri,
                            creationTime=creation_time,
                            version=version)


class EventDescription:

    def __init__(self, text, type):
        self.text = text
        self.type = type

    @staticmethod
    def from_element(element):
        type = element.elementsByTagName('type').at(0).toElement().text()
        text = element.elementsByTagName('text').at(0).toElement().text()
        return EventDescription(text=text, type=type)


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
        publicId = element.attribute('publicID')
        time = element.elementsByTagName('time').at(0).toElement().elementsByTagName('value').at(0).toElement().text()
        region = element.elementsByTagName('region').at(0).toElement().text()
        latitude = element.elementsByTagName('latitude').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        longitude = element.elementsByTagName('longitude').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        depth = element.elementsByTagName('depth').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        evaluationMode = element.elementsByTagName('evaluationMode').at(0).toElement().text()
        evaluationStatus = element.elementsByTagName('evaluationStatus').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

        return Origin(publicID=publicId,
                      time=time,
                      longitude=longitude,
                      latitude=latitude,
                      depth=depth,
                      depthType=None,
                      timeFixed=None,
                      epicenterFixed=None,
                      referenceSystemID=None,
                      methodID=None,
                      earthModeID=None,
                      compositeTime=None,
                      quality=None,
                      type=None,
                      region=region,
                      evaluationMode=evaluationMode,
                      evaluationStatus=evaluationStatus,
                      comment=None,
                      creationInfo=creation_info)


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
        value = element.elementsByTagName('value').at(0).toElement().text()
        uncertainty = element.elementsByTagName('uncertainty').at(
            0).toElement().text() if not element.elementsByTagName('uncertainty').at(0).toElement().isNull() else None
        lowerUncertainty = element.elementsByTagName('lowerUncertainty').at(
            0).toElement().text() if not element.elementsByTagName('lowerUncertainty').at(
            0).toElement().isNull() else None
        upperUncertainty = element.elementsByTagName('upperUncertainty').at(
            0).toElement().text() if not element.elementsByTagName('upperUncertainty').at(
            0).toElement().isNull() else None
        confidenceLevel = element.elementsByTagName('confidenceLevel').at(
            0).toElement().text() if not element.elementsByTagName('confidenceLevel').at(
            0).toElement().isNull() else None

        return RealQuantity(value=value,
                            uncertainty=uncertainty,
                            lowerUncertainty=lowerUncertainty,
                            upperUncertainty=upperUncertainty,
                            confidenceLevel=confidenceLevel)


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
        publicId = element.attribute('publicID')
        type = element.elementsByTagName('type').at(0).toElement().text()
        originID = element.elementsByTagName('originID').at(0).toElement().text()
        mag = Magnitude.from_element(
            element.elementsByTagName('mag').at(0).toElement()) if not element.elementsByTagName('mag').at(
            0).toElement().isNull() else None
        evaluationMode = element.elementsByTagName('evaluationMode').at(0).toElement().text()
        evaluationStatus = element.elementsByTagName('evaluationStatus').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

        return Magnitude(publicID=publicId,
                         mag=mag,
                         type=type,
                         originID=originID,
                         methodID=None,
                         stationCount=None,
                         azimuthalGap=None,
                         evalutionMode=evaluationMode,
                         evaluationStatus=evaluationStatus,
                         comment=None,
                         creationInfo=creation_info)


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
            f['Latitude'] = o.latitude
            f['Longitude'] = o.longitude
            f['DepthKm'] = o.depth
            f['Author'] = o.creationInfo.author if o.creationInfo else NULL
            f['Catalog'] = NULL  # ?
            f['Contributor'] = NULL  # ?
            f['ContributorID'] = NULL  # ?
            f['MagType'] = NULL  # ?
            f['Magnitude'] = NULL  # ?
            f['MagAuthor'] = NULL  # ?
            f['EventLocationName'] = o.region  # ?

            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(o.longitude), float(o.latitude))))
            features.append(f)

        return features

    @staticmethod
    def from_element(element):
        publicId = element.attribute('publicID')
        type = element.elementsByTagName('type').at(0).toElement().text()
        typeCertainty = element.elementsByTagName('typeCertainty').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

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

        return Event(publicID=publicId,
                     type=type,
                     typeCertainty=typeCertainty,
                     description=descriptions,
                     preferredOriginID=None,
                     preferredMagnitudeID=None,
                     preferredFocalMechanismID=None,
                     comment=None,
                     creationInfo=creation_info,
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
