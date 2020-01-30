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

ORIGIN_DEPTH_TYPES = {
    'FROM_LOCATION': "from location",
    'FROM_MOMENT_TENSOR_INVERSION': "from moment tensor inversion",
    'BROAD_BAND_P_WAVEFORMS': "from modeling of broad-band P waveforms",
    'CONSTRAINED_BY_DEPTH_PHASES': "constrained by depth phases",
    'CONSTRAINED_BY_DIRECT_PHASES': "constrained by direct phases",
    'OPERATOR_ASSIGNED': "operator assigned",
    'OTHER_ORIGIN_DEPT': "other"
}

ORIGIN_TYPES = {
    'HYPOCENTER': 'hypocenter',
    'CENTROID': 'centroid',
    'AMPLITUDE': 'amplitude',
    'MACROSEISMIC': 'macroseismic',
    'RUPTURE_START': 'rupture start',
    'RUPTURE_EN': 'rupture end'
}

ORIGIN_UNCERTAINTY_DESCRIPTIONS = {
    'HORIZONTAL': 'horizontal uncertainty',
    'ELLIPSE': 'uncertainty ellipse',
    'ELLIPSOID': 'confidence ellipsoid',
    'PDF': 'probability density function'
}


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

    def int_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional:
            return IntegerQuantity.from_element(child) if not child.isNull() else None
        else:
            return IntegerQuantity.from_element(child)

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

    def composite_time(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return CompositeTime.from_element(child)

    def origin_depth_type(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return child.text()

    def origin_type(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return child.text()

    def origin_quality(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return OriginQuality.from_element(child)

    def origin_uncertainty_description(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return child.text()

    def confidence_ellipsoid(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return ConfidenceEllipsoid.from_element(child)


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


class ConfidenceEllipsoid:

    def __init__(self,
                 semiMajorAxisLength,
                 semiMinorAxisLength,
                 semiIntermediateAxisLength,
                 majorAxisPlunge,
                 majorAxisAzimuth,
                 majorAxisRotation):
        self.semiMajorAxisLength = semiMajorAxisLength
        self.semiMinorAxisLength = semiMinorAxisLength
        self.semiIntermediateAxisLength = semiIntermediateAxisLength
        self.majorAxisPlunge = majorAxisPlunge
        self.majorAxisAzimuth = majorAxisAzimuth
        self.majorAxisRotation = majorAxisRotation

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return ConfidenceEllipsoid(
            semiMajorAxisLength=parser.float('semiMajorAxisLength', optional=False),
            semiMinorAxisLength=parser.float('semiMinorAxisLength', optional=False),
            semiIntermediateAxisLength=parser.float('semiIntermediateAxisLength', optional=False),
            majorAxisPlunge=parser.float('majorAxisPlunge', optional=False),
            majorAxisAzimuth=parser.float('majorAxisAzimuth', optional=False),
            majorAxisRotation=parser.float('majorAxisRotation', optional=False))


class OriginQuality:

    def __init__(self,
                 associatedPhaseCount,
                 usedPhaseCount,
                 associatedStationCount,
                 usedStationCount,
                 depthPhaseCount,
                 standardError,
                 azimuthalGap,
                 secondaryAzimuthalGap,
                 groundTruthLevel,
                 maximumDistance,
                 minimumDistance,
                 medianDistance):
        self.associatedPhaseCount = associatedPhaseCount
        self.usedPhaseCount = usedPhaseCount
        self.associatedStationCount = associatedStationCount
        self.usedStationCount = usedStationCount
        self.depthPhaseCount = depthPhaseCount
        self.standardError = standardError
        self.azimuthalGap = azimuthalGap
        self.secondaryAzimuthalGap = secondaryAzimuthalGap
        self.groundTruthLevel = groundTruthLevel
        self.maximumDistance = maximumDistance
        self.minimumDistance = minimumDistance
        self.medianDistance = medianDistance

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return OriginQuality(
            associatedPhaseCount=parser.int('associatedPhaseCount'),
            usedPhaseCount=parser.int('usedPhaseCount'),
            associatedStationCount=parser.int('associatedStationCount'),
            usedStationCount=parser.int('usedStationCount'),
            depthPhaseCount=parser.int('depthPhaseCount'),
            standardError=parser.float('standardError'),
            azimuthalGap=parser.float('azimuthalGap'),
            secondaryAzimuthalGap=parser.float('secondaryAzimuthalGap'),
            groundTruthLevel=parser.string('groundTruthLevel'),
            maximumDistance=parser.float('maximumDistance'),
            minimumDistance=parser.float('minimumDistance'),
            medianDistance=parser.float('medianDistance'),
        )


class OriginUncertainty:

    def __init__(self,
                 horizontalUncertainty,
                 minHorizontalUncertainty,
                 maxHorizontalUncertainty,
                 azimuthMaxHorizontalUncertainty,
                 confidenceEllipsoid,
                 preferredDescription,
                 confidenceLevel):
        self.horizontalUncertainty = horizontalUncertainty
        self.minHorizontalUncertainty = minHorizontalUncertainty
        self.maxHorizontalUncertainty = maxHorizontalUncertainty
        self.azimuthMaxHorizontalUncertainty = azimuthMaxHorizontalUncertainty
        self.confidenceEllipsoid = confidenceEllipsoid
        self.preferredDescription = preferredDescription
        self.confidenceLevel = confidenceLevel

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return OriginUncertainty(
            horizontalUncertainty=parser.float('horizontalUncertainty'),
            minHorizontalUncertainty=parser.float('minHorizontalUncertainty'),
            maxHorizontalUncertainty=parser.float('maxHorizontalUncertainty'),
            azimuthMaxHorizontalUncertainty=parser.float('azimuthMaxHorizontalUncertainty'),
            confidenceEllipsoid=parser.confidence_ellipsoid('confidenceEllipsoid'),
            preferredDescription=parser.origin_uncertainty_description('preferredDescription'),
            confidenceLevel=parser.float('confidenceLevel')
        )


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
                 comments,
                 creationInfo,
                 origin_uncertainties):
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
        self.comments = comments
        self.creationInfo = creationInfo
        self.origin_uncertainties = origin_uncertainties

    @staticmethod
    def from_element(element):
        comment_nodes = element.elementsByTagName('comment')
        comments = []
        for e in range(comment_nodes.length()):
            comments.append(Comment.from_element(comment_nodes.at(e).toElement()))

        origin_uncertainty_nodes = element.elementsByTagName('originUncertainty')
        origin_uncertainties = []
        for e in range(origin_uncertainty_nodes.length()):
            origin_uncertainties.append(OriginUncertainty.from_element(origin_uncertainty_nodes.at(e).toElement()))

        parser = ElementParser(element)
        return Origin(publicID=parser.string('publicID', optional=False, is_attribute=True),
                      time=parser.time_quantity('time'),
                      longitude=parser.real_quantity('longitude'),
                      latitude=parser.real_quantity('latitude'),
                      depth=parser.real_quantity('depth', optional=True),
                      depthType=parser.origin_depth_type('depthType', optional=True),
                      timeFixed=parser.boolean('timeFixed'),
                      epicenterFixed=parser.boolean('epicenterFixed'),
                      referenceSystemID=parser.resource_reference('referenceSystemID'),
                      methodID=parser.resource_reference('methodID'),
                      earthModeID=parser.resource_reference('earthModeID'),
                      compositeTime=parser.composite_time('compositeTime'),
                      quality=parser.origin_quality('quality'),
                      type=parser.origin_type('type'),
                      region=parser.string('region'),
                      evaluationMode=parser.string('evaluationMode'),
                      evaluationStatus=parser.string('evaluationStatus'),
                      comments=comments,
                      creationInfo=parser.creation_info('creationInfo'),
                      origin_uncertainties=origin_uncertainties)


class Comment:

    def __init__(self,
                 text,
                 id,
                 creationInfo):
        self.text = text
        self.id = id
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return Comment(text=parser.float('text', optional=False),
                       id=parser.resource_reference('id'),
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


class IntegerQuantity:

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
        return IntegerQuantity(value=parser.int('value', optional=False),
                               uncertainty=parser.int('uncertainty'),
                               lowerUncertainty=parser.int('lowerUncertainty'),
                               upperUncertainty=parser.int('upperUncertainty'),
                               confidenceLevel=parser.int('confidenceLevel'))


class CompositeTime:

    def __init__(self,
                 year,
                 month,
                 day,
                 hour,
                 minute,
                 second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        return CompositeTime(year=parser.int_quantity('year', optional=True),
                             month=parser.int_quantity('month', optional=True),
                             day=parser.int_quantity('day', optional=True),
                             hour=parser.int_quantity('hour', optional=True),
                             minute=parser.int_quantity('minute', optional=True),
                             second=parser.real_quantity('second', optional=True))


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
                 comments,
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
        self.comments = comments
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        comment_nodes = element.elementsByTagName('comment')
        comments = []
        for e in range(comment_nodes.length()):
            comments.append(Comment.from_element(comment_nodes.at(e).toElement()))

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
                         comments=comments,
                         creationInfo=parser.creation_info('creationInfo'))


class Event:

    def __init__(self,
                 publicID,
                 type,
                 typeCertainty,
                 description,
                 preferredOriginID,
                 preferredMagnitudeID,
                 preferredFocalMechanismID,
                 creationInfo,
                 origins,
                 magnitudes,
                 comments):
        self.publicID = publicID
        self.type = type
        self.typeCertainty = typeCertainty
        self.description = description
        self.preferredOriginID = preferredOriginID
        self.preferredMagnitudeID = preferredMagnitudeID
        self.preferredFocalMechanismID = preferredFocalMechanismID
        self.creationInfo = creationInfo
        self.origins = origins
        self.magnitudes = magnitudes
        self.comments = comments

    def to_features(self):
        fields = QgsFields()
        for k, v in fdsn_event_fields.items():
            fields.append(QgsField(k, v))

        assert False

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
                geom = QgsPoint(x=o.longitude.value, y=o.latitude.value, z=-o.depth.value * 1000)
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
        origins = {}
        for e in range(origin_nodes.length()):
            origin = Origin.from_element(origin_nodes.at(e).toElement())
            origins[origin.publicID] = origin

        magnitude_nodes = element.elementsByTagName('magnitude')
        magnitudes = {}
        for e in range(magnitude_nodes.length()):
            magnitude = Magnitude.from_element(magnitude_nodes.at(e).toElement())
            magnitudes[magnitude.publicID] = magnitude

        comment_nodes = element.elementsByTagName('comment')
        comments = []
        for e in range(comment_nodes.length()):
            comments.append(Comment.from_element(comment_nodes.at(e).toElement()))

        return Event(publicID=parser.string('publicID', is_attribute=True, optional=False),
                     type=parser.string('type'),
                     typeCertainty=parser.string('typeCertainty'),
                     description=descriptions,
                     preferredOriginID=parser.resource_reference('preferredOriginID'),
                     preferredMagnitudeID=parser.resource_reference('preferredMagnitudeID'),
                     preferredFocalMechanismID=parser.resource_reference('preferredFocalMechanismID'),
                     comments=comments,
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
