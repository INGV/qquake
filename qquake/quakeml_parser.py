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

from qgis.PyQt.QtCore import QVariant, QDate, QDateTime, QTime, Qt
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
        def to_datetime(val):
            if not val:
                return NULL
            if 'T' in val:
                if '.' not in val:
                    val += '.000'
                dt = QDateTime.fromString((val + '000')[:23], 'yyyy-MM-ddThh:mm:ss.zzz')
                dt.setTimeSpec(Qt.UTC)
                return dt
            else:
                dt = QDateTime(QDate.fromString(val, 'yyyy-MM-dd'), QTime())
                dt.setTimeSpec(Qt.UTC)
                return dt

        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                return None
            else:
                return to_datetime(self.element.attribute(attribute))
        else:
            child = self.element.elementsByTagName(attribute).at(0).toElement()
            if optional and child.isNull():
                return None

            return to_datetime(child.text())

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

    def ms_expected_intensity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return MsExpectedItensity.from_element(child)

    def ms_intensity(self, attribute, optional=True):
        child = self.element.elementsByTagName(attribute).at(0).toElement()
        if optional and child.isNull():
            return None

        return MsIntensity.from_element(child)


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

        if not self.time or not self.time.is_valid() and self.compositeTime and self.compositeTime.can_convert_to_datetime():
            # upgrade composite time value to time value
            self.time = self.compositeTime.to_timequantity()

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

    def is_valid(self):
        return self.value and self.value.isValid()


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

    def can_convert_to_datetime(self):
        return self.year and self.year.value

    def to_timequantity(self):
        return TimeQuantity(value=QDateTime(self.year.value,
                                            self.month and self.month.value or 1,
                                            self.day and self.day.value or 1,
                                            self.hour and self.hour.value or 0,
                                            self.minute and self.minute.value or 0,
                                            self.second and self.second.value or 0),
                            uncertainty=None,
                            lowerUncertainty=None,
                            upperUncertainty=None,
                            confidenceLevel=None)


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


class MsPlace:

    def __init__(self,
                 publicID,
                 name,
                 latitude,
                 longitude):
        self.publicID = publicID
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)

        return MsPlace(publicID=parser.string('publicID', is_attribute=True, optional=False),
                       name=parser.string('ms:name', is_attribute=False, optional=True),
                       latitude=parser.real_quantity('ms:referenceLatitude'),
                       longitude=parser.real_quantity('ms:referenceLongitude'))


class MsExpectedItensity:

    def __init__(self,
                 msclass):
        self.msclass = msclass

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)

        return MsExpectedItensity(msclass=parser.string('ms:class', is_attribute=False, optional=False))


class MsIntensity:

    def __init__(self,
                 macroseismicScale,
                 expectedIntensity):
        self.macroseismicScale = macroseismicScale
        self.expectedIntensity = expectedIntensity

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)

        return MsIntensity(macroseismicScale=parser.string('ms:macroseismicScale', is_attribute=False, optional=False),
                           expectedIntensity=parser.ms_expected_intensity('ms:expectedIntensity'))

class MsMdp:

    def __init__(self,
                 publicID,
                 reportReference,
                 eventReference,
                 placeReference,
                 intensity):
        self.publicID = publicID
        self.reportReference = reportReference
        self.eventReference = eventReference
        self.placeReference = placeReference
        self.intensity = intensity

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)

        return MsMdp(publicID=parser.string('publicID', is_attribute=True, optional=False),
                     reportReference=parser.resource_reference('ms:reportReference'),
                     eventReference=parser.resource_reference('ms:eventReference'),
                     placeReference=parser.resource_reference('ms:placeReference'),
                     intensity=parser.ms_intensity('ms:intensity'))


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
        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

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

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

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

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

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

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

        return fields

    @staticmethod
    def add_origin_attributes(origin, feature, output_fields):
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for dest_field in CONFIG_FIELDS['field_groups']['origin']['fields']:
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
                selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True,
                                          bool)
            if not selected:
                continue

            assert source[0] == 'origin'
            source = source[1:]

            source_obj = origin
            for s in source:
                assert hasattr(source_obj, s)
                source_obj = getattr(source_obj, s)
                if source_obj is None:
                    break

            feature[dest_field[field_config_key]] = source_obj

        if origin.depth is not None:
            geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value,
                            z=-origin.depth.value * 1000)
        elif origin.longitude and origin.latitude:
            geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value)
        else:
            geom = QgsGeometry()
        feature.setGeometry(QgsGeometry(geom))

    @staticmethod
    def add_magnitude_attributes(magnitude, feature, output_fields):
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for dest_field in CONFIG_FIELDS['field_groups']['magnitude']['fields']:
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

            assert source[0] == 'magnitude'
            source = source[1:]

            source_obj = magnitude
            for s in source:
                assert hasattr(source_obj, s)
                source_obj = getattr(source_obj, s)

            feature[dest_field[field_config_key]] = source_obj

    def to_features(self, output_fields, preferred_origin_only, preferred_magnitudes_only, all_origins):
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

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

            f[dest_field[field_config_key]] = source_obj

        origins_handled = set()
        for _, m in self.magnitudes.items():

            if preferred_magnitudes_only and m.publicID != self.preferredMagnitudeID:
                continue

            magnitude_feature = QgsFeature(f)
            self.add_magnitude_attributes(m, magnitude_feature, output_fields)

            magnitude_origin = all_origins[m.originID]
            self.add_origin_attributes(magnitude_origin, magnitude_feature, output_fields)

            origins_handled.add(m.originID)

            yield magnitude_feature

        for _, o in self.origins.items():
            if preferred_origin_only and o.publicID != self.preferredOriginID:
                continue

            if o.publicID in origins_handled:
                continue

            origin_feature = QgsFeature(f)
            self.add_origin_attributes(o, origin_feature, output_fields)

            yield origin_feature

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

    def __init__(self):
        self.events = {}
        self.origins = {}
        self.magnitudes = {}
        self.macro_places = {}
        self.mdps = {}

    def parse_initial(self, content):
        self.events = []
        self.origins = {}
        self.magnitudes = {}
        self.macro_places = {}
        self.mdps = {}
        self.add_events(content)

    def add_events(self, content):
        doc = QDomDocument()
        doc.setContent(content)
        event_elements = doc.elementsByTagName('event')

        for e in range(event_elements.length()):
            event_element = event_elements.at(e).toElement()
            event = Event.from_element(event_element)
            self.events.append(event)
            for _, o in event.origins.items():
                if o not in self.origins:
                    self.origins[o.publicID] = o
            for _, m in event.magnitudes.items():
                if m not in self.magnitudes:
                    self.magnitudes[m.publicID] = m

        # macro places first
        macro_places = doc.elementsByTagName('ms:place')
        for e in range(macro_places.length()):
            macro_place = macro_places.at(e).toElement()
            place = MsPlace.from_element(macro_place)
            self.macro_places[place.publicID] = place

        macro_mdp = doc.elementsByTagName('ms:mdp')
        for e in range(macro_mdp.length()):
            mdp_element = macro_mdp.at(e).toElement()
            mdp = MsMdp.from_element(mdp_element)
            self.mdps[mdp.publicID] = mdp

    def parse_missing_origin(self, content):
        doc = QDomDocument()
        doc.setContent(content)

        event_elements = doc.elementsByTagName('event')

        for e in range(event_elements.length()):
            event_element = event_elements.at(e).toElement()
            event = Event.from_element(event_element)
            for _, o in event.origins.items():
                if o not in self.origins:
                    self.origins[o.publicID] = o
            for _, m in event.magnitudes.items():
                if m not in self.magnitudes:
                    self.magnitudes[m.publicID] = m

    def scan_for_missing_origins(self):
        missing_origins = set()
        for e in self.events:
            if e.preferredOriginID not in self.origins:
                missing_origins.add(e.preferredOriginID)

            for _, m in e.magnitudes.items():
                if m.originID not in self.origins:
                    missing_origins.add(m.originID)

        return list(missing_origins)

    @staticmethod
    def to_event_fields(selected_fields):
        return Event.to_fields(selected_fields)

    def create_event_features(self, output_fields, preferred_origin_only, preferred_magnitudes_only):
        for e in self.events:
            for f in e.to_features(output_fields, preferred_origin_only, preferred_magnitudes_only,
                                   all_origins=self.origins):
                yield f

    @staticmethod
    def create_mdp_fields():
        f = QgsFields()
        f.append(QgsField('publicID', QVariant.String))
        f.append(QgsField('reportReference', QVariant.String))
        f.append(QgsField('eventReference', QVariant.String))
        f.append(QgsField('placeReference', QVariant.String))
        f.append(QgsField('placeName', QVariant.String))
        f.append(QgsField('macroseismicScale', QVariant.String))
        f.append(QgsField('expectedIntensity', QVariant.String))
        return f

    def create_mdp_features(self):
        fields = self.create_mdp_fields()
        for _, m in self.mdps.items():
            if m.placeReference in self.macro_places:
                place = self.macro_places[m.placeReference]
            else:
                place = None

            f = QgsFeature(fields)
            f['publicID'] = m.publicID
            f['reportReference']=m.reportReference
            f['eventReference'] = m.eventReference
            f['placeReference'] = m.placeReference
            f['placeName'] = place.name if place else NULL
            f['macroseismicScale'] = m.intensity.macroseismicScale
            f['expectedIntensity'] = m.intensity.expectedIntensity.msclass
            if place and place.longitude and place.latitude:
                geom = QgsPoint(x=place.longitude.value, y=place.latitude.value)
                f.setGeometry(QgsGeometry(geom))

            yield f


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

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields']:
            if f.get('skip'):
                continue

            path = f['source']
            path = path[len('eventParameters>event>'):].replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))
        return fields

    def to_station_features(self, selected_fields):
        features = []
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

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

                f[dest_field[field_config_key]] = source_obj

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
                 StartDate,
                 EndDate,
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
        self.StartDate = StartDate
        self.EndDate = EndDate
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

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

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

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))
        return fields

    @staticmethod
    def from_element(element):
        parser = ElementParser(element)
        res = Station(
            StartDate=parser.datetime('startDate', is_attribute=True, optional=True),
            EndDate=parser.datetime('endDate', is_attribute=True, optional=True),
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
