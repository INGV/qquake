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

import json
import os

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsSettings,
    NULL
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

CONFIG_FIELDS_PATH = os.path.join(
    os.path.dirname(__file__),
    'config',
    'config_fields_fsdnevent.json')

with open(CONFIG_FIELDS_PATH, 'r') as f:
    CONFIG_FIELDS = json.load(f)

FIELD_TYPE_MAP = {
    'String': QVariant.String,
    'Int': QVariant.Int,
    'Double': QVariant.Double,
    'Time': QVariant.Time,
    'DateTime': QVariant.DateTime,
    'Date': QVariant.Date
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

    def datetime(self, attribute, optional=True, is_attribute=False):
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                return None
            else:
                return self.element.attribute(attribute)
        else:
            child = self.element.elementsByTagName(attribute).at(0).toElement()
            if optional and child.isNull():
                return None

            # TODO - return as QDateTime
            return child.text()

    def time_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return TimeQuantity.from_element(child)

    def real_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional RealQuantities
        value_child = child.elementsByTagName('value').at(0).toElement()
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

        return RealQuantity.from_element(child)

    def int_quantity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional IntQuantities
        value_child = child.elementsByTagName('value').at(0).toElement()
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

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
                 earthModelID,
                 compositeTime,
                 quality,
                 type,
                 region,
                 evaluationMode,
                 evaluationStatus,
                 comments,
                 creationInfo,
                 originUncertainty):
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
        self.earthModelID = earthModelID
        self.compositeTime = compositeTime
        self.quality = quality
        self.type = type
        self.region = region
        self.evaluationMode = evaluationMode
        self.evaluationStatus = evaluationStatus
        self.comments = comments
        self.creationInfo = creationInfo
        self.originUncertainty = originUncertainty

    @staticmethod
    def from_element(element):
        comment_nodes = element.elementsByTagName('comment')
        comments = []
        for e in range(comment_nodes.length()):
            comments.append(Comment.from_element(comment_nodes.at(e).toElement()))

        origin_uncertainty_nodes = element.elementsByTagName('originUncertainty')
        origin_uncertainty = None
        if origin_uncertainty_nodes.length():
            OriginUncertainty.from_element(origin_uncertainty_nodes.at(0).toElement())

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
                      earthModelID=parser.resource_reference('earthModelID'),
                      compositeTime=parser.composite_time('compositeTime'),
                      quality=parser.origin_quality('quality'),
                      type=parser.origin_type('type'),
                      region=parser.string('region'),
                      evaluationMode=parser.string('evaluationMode'),
                      evaluationStatus=parser.string('evaluationStatus'),
                      comments=comments,
                      creationInfo=parser.creation_info('creationInfo'),
                      originUncertainty=origin_uncertainty)

    @staticmethod
    def to_fields(selected_fields):
        fields = QgsFields()
        settings = QgsSettings()
        for f in CONFIG_FIELDS['field_groups']['origin']['fields']:
            if f.get('skip'):
                continue

            path = f['source']
            if selected_fields:
                selected = path in selected_fields
            else:
                path = path[len('eventParameters>event>'):].replace('>', '_')
                selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f['field'], FIELD_TYPE_MAP[f['type']]))
        return fields


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


class TimeQuantity:

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
        return TimeQuantity(value=parser.datetime('value', optional=False),
                            uncertainty=parser.float('uncertainty'),
                            lowerUncertainty=parser.float('lowerUncertainty'),
                            upperUncertainty=parser.float('upperUncertainty'),
                            confidenceLevel=parser.float('confidenceLevel'))


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
                         evaluationMode=parser.string('evaluationMode'),
                         evaluationStatus=parser.string('evaluationStatus'),
                         comments=comments,
                         creationInfo=parser.creation_info('creationInfo'))

    @staticmethod
    def to_fields(selected_fields):
        fields = QgsFields()
        settings = QgsSettings()
        for f in CONFIG_FIELDS['field_groups']['magnitude']['fields']:
            if f.get('skip'):
                continue

            path = f['source']
            if selected_fields:
                selected = path in selected_fields
            else:
                path = path[len('eventParameters>event>'):].replace('>', '_')
                selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f['field'], FIELD_TYPE_MAP[f['type']]))
        return fields


class Event:

    def __init__(self,
                 publicID,
                 type,
                 typeCertainty,
                 descriptions,
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
        self.descriptions = descriptions
        self.preferredOriginID = preferredOriginID
        self.preferredMagnitudeID = preferredMagnitudeID
        self.preferredFocalMechanismID = preferredFocalMechanismID
        self.creationInfo = creationInfo
        self.origins = origins
        self.magnitudes = magnitudes
        self.comments = comments

    @staticmethod
    def to_fields(selected_fields=None):
        fields = QgsFields()
        settings = QgsSettings()
        for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields']:
            if f.get('skip'):
                continue

            path = f['source']

            if selected_fields:
                # use specified fields
                selected = path in selected_fields
            else:
                # use default settings
                path = path[len('eventParameters>event>'):].replace('>', '_')
                selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)

            if not selected:
                continue

            fields.append(QgsField(f['field'], FIELD_TYPE_MAP[f['type']]))
        return fields

    def to_feature(self, output_fields):
        settings = QgsSettings()

        f = QgsFeature(self.to_fields(output_fields))
        for dest_field in CONFIG_FIELDS['field_groups']['basic_event_info']['fields']:
            if dest_field.get('skip'):
                continue

            source = dest_field['source'].split('>')
            assert source[0] == 'eventParameters'
            source = source[1:]
            assert source[0] == 'event'
            source = source[1:]

            if output_fields:
                selected = dest_field['source'] in output_fields
            else:
                selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)

            if not selected:
                continue

            source_obj = self
            for s in source:
                if source_obj is None:
                    source_obj = NULL
                    break
                assert hasattr(source_obj, s)
                source_obj = getattr(source_obj, s)

            f[dest_field['field']] = source_obj

        preferred_origin = self.origins[self.preferredOriginID]
        if preferred_origin.latitude is None or preferred_origin.longitude is None:
            geom = QgsGeometry()
        elif preferred_origin.depth is not None:
            geom = QgsPoint(x=preferred_origin.longitude.value, y=preferred_origin.latitude.value,
                            z=-preferred_origin.depth.value * 1000)
        else:
            geom = QgsPoint(x=preferred_origin.longitude.value, y=preferred_origin.latitude.value)
        f.setGeometry(QgsGeometry(geom))

        return f

    def to_origin_features(self, selected_fields):
        features = []
        settings = QgsSettings()
        for _, o in self.origins.items():
            f = QgsFeature(Origin.to_fields(selected_fields))
            for dest_field in CONFIG_FIELDS['field_groups']['origin']['fields']:
                if dest_field.get('skip'):
                    continue

                source = dest_field['source'].split('>')
                assert source[0] == 'eventParameters'
                source = source[1:]
                assert source[0] == 'event'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)
                if not selected:
                    continue

                assert source[0] == 'origin'
                source = source[1:]

                source_obj = o
                for s in source:
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)
                    if source_obj is None:
                        break

                f[dest_field['field']] = source_obj

            if o.depth is not None:
                geom = QgsPoint(x=o.longitude.value, y=o.latitude.value,
                                z=-o.depth.value * 1000)
            elif o.longitude and o.latitude:
                geom = QgsPoint(x=o.longitude.value, y=o.latitude.value)
            else:
                geom = QgsGeometry()
            f.setGeometry(QgsGeometry(geom))

            features.append(f)

        return features

    def to_magnitude_features(self, selected_fields):
        features = []
        settings = QgsSettings()
        for _, o in self.magnitudes.items():

            f = QgsFeature(Magnitude.to_fields(selected_fields))
            for dest_field in CONFIG_FIELDS['field_groups']['magnitude']['fields']:
                if dest_field.get('skip'):
                    continue

                source = dest_field['source'].split('>')
                assert source[0] == 'eventParameters'
                source = source[1:]
                assert source[0] == 'event'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)
                if not selected:
                    continue

                assert source[0] == 'magnitude'
                source = source[1:]

                source_obj = o
                for s in source:
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field['field']] = source_obj

            origin = self.origins[o.originID]

            if origin.depth is not None:
                geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value,
                                z=-origin.depth.value * 1000)
            else:
                geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value)
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
                     descriptions=descriptions,
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


class BaseNodeType:
    """
    A base node type for derivation from: Network, Station and Channel types.
    """

    def __init__(self,
                 Code,
                 StartDate,
                 EndDate,
                 SourceID,
                 RestrictedStatus,
                 AlternateCode,
                 HistoricalCode,
                 Description=None):
        self.Code = Code
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.SourceID = SourceID
        self.RestrictedStatus = RestrictedStatus
        self.AlternateCode = AlternateCode
        self.HistoricalCode = HistoricalCode
        self.Description = Description

    @staticmethod
    def _from_element(obj, element):
        parser = ElementParser(element)
        obj.Code = parser.string('code', optional=False, is_attribute=True)
        obj.StartDate = parser.datetime('startDate', optional=False, is_attribute=True)
        obj.EndDate = parser.datetime('endDate', optional=False, is_attribute=True)
        obj.SourceID = parser.string('sourceID', optional=False, is_attribute=True)
        obj.RestrictedStatus = parser.string('restrictedStatus', is_attribute=True)
        obj.AlternateCode = parser.string('alternateCode', is_attribute=True)
        obj.HistoricalCode = parser.string('historicalCode', is_attribute=True)
        obj.Description = parser.string('Description')
        # Identifier
        # Comment
        # DataAvailability


class Network(BaseNodeType):
    """
    This type represents the Network layer, all station metadata is contained within this element.
    The official name of the network or other descriptive information can be included in the
    Description element. The Network can contain 0 or more Stations.
    """

    def __init__(self,
                 stations):
        super().__init__(None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None)
        self.stations = stations

    @staticmethod
    def to_fields():
        fields = QgsFields()
        settings = QgsSettings()
        for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields']:
            if f.get('skip'):
                continue

            path = f['source']
            path = path[len('eventParameters>event>'):].replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f['field'], FIELD_TYPE_MAP[f['type']]))
        return fields

    def to_station_features(self, selected_fields):
        features = []
        settings = QgsSettings()
        for o in self.stations:
            f = QgsFeature(Station.to_fields(selected_fields))
            for dest_field in CONFIG_FIELDS['field_groups']['station']['fields']:
                if dest_field.get('skip'):
                    continue

                source = dest_field['source'].split('>')
                assert source[0] == 'FDSNStationXML'
                source = source[1:]
                assert source[0] == 'Network'
                source = source[1:]
                source_obj = self

                if source[0] == 'Station':
                    source_obj = o
                    source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)
                if not selected:
                    continue

                for s in source:
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)
                    if source_obj is None:
                        break

                f[dest_field['field']] = source_obj

            geom = QgsPoint(x=o.Longitude, y=o.Latitude,
                            z=o.Elevation)
            f.setGeometry(QgsGeometry(geom))

            features.append(f)

        return features

    @staticmethod
    def from_element(element):
        station_nodes = element.elementsByTagName('Station')
        stations = []
        for e in range(station_nodes.length()):
            stations.append(Station.from_element(station_nodes.at(e).toElement()))

        res = Network(stations=stations)
        BaseNodeType._from_element(res, element)
        return res


class Station(BaseNodeType):
    """
    This type represents a Station epoch. It is common to only have a single station epoch with the
    station's creation and termination dates as the epoch start and end dates.
    """

    def __init__(self,
                 Latitude,
                 Longitude,
                 Elevation,
                 # site, - not supported
                 WaterLevel,
                 Vault,
                 Geology,
                 # equipment -  not supported
                 # operator - not supported
                 CreationDate,
                 TerminationDate,
                 TotalNumberChannels,
                 SelectedNumberChannels,
                 # ExternalReference - not supported
                 # Channel
                 ):
        super().__init__(None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None)
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Elevation = Elevation
        # self.site = site
        self.WaterLevel = WaterLevel
        self.Vault = Vault
        self.Geology = Geology
        self.CreationDate = CreationDate
        self.TerminationDate = TerminationDate
        self.TotalNumberChannels = TotalNumberChannels
        self.SelectedNumberChannels = SelectedNumberChannels

    @staticmethod
    def to_fields(selected_fields):
        fields = QgsFields()
        settings = QgsSettings()
        for f in CONFIG_FIELDS['field_groups']['station']['fields']:
            if f.get('skip'):
                continue

            path = f['source']
            if selected_fields:
                selected = path in selected_fields
            else:
                path = path[len('FDSNStationXML>Network>'):].replace('>', '_')
                selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f['field'], FIELD_TYPE_MAP[f['type']]))
        return fields

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        res = Station(
            Latitude=parser.float('Latitude', optional=False),
            Longitude=parser.float('Longitude', optional=False),
            Elevation=parser.float('Elevation', optional=False),
            WaterLevel=parser.float('WaterLevel'),
            Vault=parser.string('Vault'),
            Geology=parser.string('Geology'),
            CreationDate=parser.datetime('CreationDate'),
            TerminationDate=parser.datetime('TerminationDate'),
            TotalNumberChannels=parser.int('TotalNumberChannels'),
            SelectedNumberChannels=parser.int('SelectedNumberChannels')
        )
        BaseNodeType._from_element(res, element)
        return res


class FDSNStationXMLParser:
    """
    FDSNStationXML parser
    """

    @staticmethod
    def parse(content):
        doc = QDomDocument()
        doc.setContent(content)
        network_elements = doc.elementsByTagName('Network')

        networks = []
        for e in range(network_elements.length()):
            network_element = network_elements.at(e).toElement()
            networks.append(Network.from_element(network_element))

        return networks
