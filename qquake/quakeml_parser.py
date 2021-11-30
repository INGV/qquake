# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
"""QQuake- QuakeML Parser

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

import json
import os
from typing import List, Optional, Dict

from qgis.PyQt.QtCore import (
    QVariant,
    QByteArray,
    QDate,
    QDateTime,
    QTime,
    Qt
)
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement
)
from qgis.core import (
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsSettings,
    NULL,
    QgsUnitTypes
)

from qquake.services import SERVICE_MANAGER


class MissingOriginException(Exception):
    """
    Raised when a referenced origin is not present
    """


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

with open(CONFIG_FIELDS_PATH, 'r', encoding='utf8') as config_file:
    CONFIG_FIELDS = json.load(config_file)

FIELD_TYPE_MAP = {
    'String': QVariant.String,
    'Int': QVariant.Int,
    'Double': QVariant.Double,
    'Time': QVariant.Time,
    'DateTime': QVariant.DateTime,
    'Date': QVariant.Date,
    'Boolean': QVariant.Bool
}


def get_service_fields(service_type: str,  # pylint: disable=too-many-branches,too-many-statements
                       selected_fields: Optional[List[str]]) -> QgsFields:
    """
    Gets the field configuration for a service
    """
    fields = QgsFields()
    settings = QgsSettings()
    short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
    field_config_key = 'field_short' if short_field_names else 'field_long'

    include_quake_details_in_mdp = settings.value('/plugins/qquake/include_quake_details_in_mdp', True, bool)

    field_config = SERVICE_MANAGER.get_field_config(service_type)
    for f in field_config['field_groups'].get('basic_event_info', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if service_type == SERVICE_MANAGER.MACROSEISMIC and not include_quake_details_in_mdp and '>event' in path and path != 'eventParameters>event§publicID':
            continue

        if selected_fields:
            # use specified fields
            selected = path in selected_fields
        else:
            # use default settings
            path = path[len('eventParameters>event>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)

        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('origin', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if service_type == SERVICE_MANAGER.MACROSEISMIC and not include_quake_details_in_mdp:
            continue

        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('eventParameters>event>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('magnitude', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        if service_type == SERVICE_MANAGER.MACROSEISMIC and not include_quake_details_in_mdp:
            continue

        path = f['source']
        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('eventParameters>event>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('macro_basic_event_info', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('macroseismicParameters>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('mdpSet', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('macroseismicParameters>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('mdp', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('macroseismicParameters>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    for f in field_config['field_groups'].get('place', {}).get('fields', []):
        if f.get('skip'):
            continue

        if f.get('one_to_many'):
            continue

        path = f['source']
        if selected_fields:
            selected = path in selected_fields
        else:
            path = path[len('macroseismicParameters>'):].replace('§', '>').replace('>', '_')
            selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
        if not selected:
            continue

        fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))

    return fields


class ElementParser:  # pylint: disable=too-many-public-methods
    """
    QuakeML Element parser
    """

    def __init__(self, element):
        self.element = element

    def string(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[str]:
        """
        Returns an attribute as a string
        """
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = self.element.attribute(attribute)
        else:
            child = self.element.firstChildElement(attribute)
            if optional and child.isNull():
                res = None
            else:
                res = child.text()
        return res

    def resource_reference(self, attribute: str, optional: bool = True) -> Optional[str]:
        """
        Returns a resource reference as a string
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def datetime(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[QDateTime]:
        """
        Returns an attribute as a QDateTime
        """

        def to_datetime(val):
            if not val:
                return NULL
            if 'T' in val:
                if '.' not in val:
                    val += '.000'
                if val[-1].upper() == 'Z':
                    val = val[:-1]
                dt = QDateTime.fromString((val + '000')[:23], 'yyyy-MM-ddThh:mm:ss.zzz')
                dt.setTimeSpec(Qt.UTC)
                return dt

            dt = QDateTime(QDate.fromString(val, 'yyyy-MM-dd'), QTime())
            dt.setTimeSpec(Qt.UTC)
            return dt

        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = to_datetime(self.element.attribute(attribute))
        else:
            child = self.element.firstChildElement(attribute)
            if optional and child.isNull():
                res = None
            else:
                res = to_datetime(child.text())
        return res

    def time_quantity(self, attribute: str, optional: bool = True) -> Optional['TimeQuantity']:
        """
        Returns an attribute as a TimeQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return TimeQuantity.from_element(child)

    def real_quantity(self, attribute: str, optional: bool = True) -> Optional['RealQuantity']:
        """
        Returns an attribute as a RealQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional RealQuantities
        value_child = child.firstChildElement('value')
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

        return RealQuantity.from_element(child)

    def int_quantity(self, attribute: str, optional: bool = True) -> Optional['IntegerQuantity']:
        """
        Returns an attributes as an IntegerQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional IntQuantities
        value_child = child.firstChildElement('value')
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

        return IntegerQuantity.from_element(child)

    def float(self, attribute: str, optional: bool = True) -> Optional[float]:
        """
        Returns an attribute as a float value
        """
        child = self.element.firstChildElement(attribute)
        if optional:
            return float(child.text()) if not child.isNull() else None

        return float(child.text())

    def int(self, attribute: str, optional: bool = True) -> Optional[int]:
        """
        Returns an attribute as an integer value
        """
        child = self.element.firstChildElement(attribute)
        if optional:
            return int(child.text()) if not child.isNull() else None

        return int(child.text())

    def boolean(self, attribute: str, optional: bool = True) -> Optional[bool]:
        """
        Returns an attribute as a boolean value
        """
        child = self.element.firstChildElement(attribute)
        if optional:
            return bool(child.text()) if not child.isNull() else None

        return bool(child.text())

    def creation_info(self, attribute: str, optional: bool = True) -> Optional['CreationInfo']:
        """
        Returns an attribute as an CreationInfo
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return CreationInfo.from_element(child)

    def composite_time(self, attribute, optional=True) -> Optional['CompositeTime']:
        """
        Returns an attribute as a CompositeTime
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return CompositeTime.from_element(child)

    def epoch(self, attribute, optional=True) -> Optional['Epoch']:
        """
        Returns an attribute as a Epoch
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return Epoch.from_element(child)

    def origin_depth_type(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attribute as an origin depth type
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def origin_type(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attribute as a origin type
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def origin_quality(self, attribute, optional=True) -> Optional['OriginQuality']:
        """
        Returns an attribute as a OriginQuality
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return OriginQuality.from_element(child)

    def origin_uncertainty_description(self, attribute, optional=True) -> Optional[str]:
        """
        Returns an attributes as an origin uncertainty string
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def confidence_ellipsoid(self, attribute, optional=True) -> Optional['ConfidenceEllipsoid']:
        """
        Returns an attributes as a ConfidenceEllipsoid
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return ConfidenceEllipsoid.from_element(child)

    def ms_intensity_value_type(self, attribute, optional=True) -> Optional['MsItensityValueType']:
        """
        Returns an attribute as a MsItensityValueType
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return MsItensityValueType.from_element(child)

    def ms_intensity(self, attribute, optional=True) -> Optional['MsIntensity']:
        """
        Returns an attribute as a MsIntensity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return MsIntensity.from_element(child)

    def ms_placename(self, attribute, optional=True) -> Optional['MsPlaceName']:
        """
        Returns an attribute as a MsPlaceName
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return MsPlaceName.from_element(child)

    def ms_sitemorphology(self, attribute, optional=True) -> Optional['MsSiteMorphology']:
        """
        Returns an attribute as a MsSiteMorphology
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return MsSiteMorphology.from_element(child)

    def site(self, attribute, optional=True) -> Optional['Site']:
        """
        Returns an attribute as a Site
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return Site.from_element(child)

    def equipment(self, attribute, optional=True) -> Optional['Equipment']:
        """
        Returns an attribute as a Equipment
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return Equipment.from_element(child)

    def operator(self, attribute, optional=True) -> Optional['Operator']:
        """
        Returns an attribute as a Operator
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return Operator.from_element(child)

    def person(self, attribute, optional=True) -> Optional['Person']:
        """
        Returns an attribute as a Person
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return Person.from_element(child)

    def phone_number(self, attribute, optional=True) -> Optional['PhoneNumber']:
        """
        Returns an attribute as a PhoneNumber
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return PhoneNumber.from_element(child)

    def external_reference(self, attribute, optional=True) -> Optional['ExternalReference']:
        """
        Returns an attribute as a ExternalReference
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return ExternalReference.from_element(child)


class QuakeMlElement:
    """
    Base class for QuakeML elements
    """

    def to_dict(self) -> Dict[str, object]:
        """
        Converts the element to a python dictionary
        """
        res = {
            'type': self.__class__.__name__
        }

        def convert_value(value):
            """
            Converts a value for storage in a dictionary
            """
            if value is None or value == NULL:
                return None
            if isinstance(value, (str, float, bool, int)):
                return value
            if isinstance(value, QDateTime):
                return value.toString(Qt.ISODate)
            if isinstance(value, QuakeMlElement):
                return value.to_dict()
            if isinstance(value, list):
                return [convert_value(v) for v in value]
            if isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}

            raise NotImplementedError()

        for _attr in dir(self):
            if _attr.startswith('__'):
                continue

            val = getattr(self, _attr)
            if callable(val):
                continue

            try:
                res[_attr] = convert_value(val)
            except NotImplementedError:
                assert False, (_attr, val)

        return res


class CreationInfo(QuakeMlElement):
    """
    CreationInfo
    """

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
    def from_element(element: QDomElement) -> 'CreationInfo':
        """
        Constructs a CreationInfo from a DOM element
        """
        parser = ElementParser(element)
        return CreationInfo(agencyID=parser.string('agencyID'),
                            agencyURI=parser.string('agencyURI'),
                            author=parser.string('author'),
                            authorURI=parser.string('authorURI'),
                            creationTime=parser.datetime('creationTime'),
                            version=parser.string('version'))


class ConfidenceEllipsoid(QuakeMlElement):
    """
    ConfidenceEllipsoid
    """

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
    def from_element(element: QDomElement) -> 'ConfidenceEllipsoid':
        """
        Constructs a ConfidenceEllipsoid from a DOM element
        """
        parser = ElementParser(element)
        return ConfidenceEllipsoid(
            semiMajorAxisLength=parser.float('semiMajorAxisLength', optional=False),
            semiMinorAxisLength=parser.float('semiMinorAxisLength', optional=False),
            semiIntermediateAxisLength=parser.float('semiIntermediateAxisLength', optional=False),
            majorAxisPlunge=parser.float('majorAxisPlunge', optional=False),
            majorAxisAzimuth=parser.float('majorAxisAzimuth', optional=False),
            majorAxisRotation=parser.float('majorAxisRotation', optional=False))


class OriginQuality(QuakeMlElement):
    """
    OriginQuality
    """

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
    def from_element(element: QDomElement) -> 'OriginQuality':
        """
        Constructs a OriginQuality from a DOM element
        """
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


class OriginUncertainty(QuakeMlElement):
    """
    OriginUncertainty
    """

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
    def from_element(element: QDomElement) -> 'OriginUncertainty':
        """
        Constructs a OriginUncertainty from a DOM element
        """
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


class EventDescription(QuakeMlElement):
    """
    EventDescription
    """

    def __init__(self, text, event_description_type):
        self.text = text
        self.type = event_description_type

    @staticmethod
    def from_element(element: QDomElement) -> 'EventDescription':
        """
        Constructs a EventDescription from a DOM element
        """
        parser = ElementParser(element)
        return EventDescription(text=parser.string('text'), event_description_type=parser.string('type'))


class Site(QuakeMlElement):
    """
    Site
    """

    def __init__(self, Name, Description, Town, County, Region, Country):
        self.Name = Name
        self.Description = Description
        self.Town = Town
        self.County = County
        self.Region = Region
        self.Country = Country

    @staticmethod
    def from_element(element: QDomElement) -> 'Site':
        """
        Constructs a Site from a DOM element
        """
        parser = ElementParser(element)
        return Site(Name=parser.string('Name'),
                    Description=parser.string('Description', optional=True),
                    Town=parser.string('Town', optional=True),
                    County=parser.string('County', optional=True),
                    Region=parser.string('Region', optional=True),
                    Country=parser.string('Country', optional=True))


class Equipment(QuakeMlElement):
    """
    Equipment
    """

    def __init__(self, Type, Description, Manufacturer, Vendor, Model, SerialNumber, InstallationDate, RemovalDate,
                 CalibrationDate, resourceId):
        self.Type = Type
        self.Description = Description
        self.Manufacturer = Manufacturer
        self.Vendor = Vendor
        self.Model = Model
        self.SerialNumber = SerialNumber
        self.InstallationDate = InstallationDate
        self.RemovalDate = RemovalDate
        self.CalibrationDate = CalibrationDate
        self.resourceId = resourceId

    @staticmethod
    def from_element(element: QDomElement) -> 'Equipment':
        """
        Constructs Equipment from a DOM element
        """
        parser = ElementParser(element)
        return Equipment(Type=parser.string('Type', optional=True),
                         Description=parser.string('Description', optional=True),
                         Manufacturer=parser.string('Manufacturer', optional=True),
                         Vendor=parser.string('Vendor', optional=True),
                         Model=parser.string('Model', optional=True),
                         SerialNumber=parser.string('SerialNumber', optional=True),
                         InstallationDate=parser.datetime('InstallationDate', optional=True),
                         RemovalDate=parser.datetime('RemovalDate', optional=True),
                         CalibrationDate=parser.datetime('CalibrationDate', optional=True),
                         resourceId=parser.string('resourceId', optional=True, is_attribute=True))


class Operator(QuakeMlElement):
    """
    Operator
    """

    def __init__(self, Agency, Contact, Website):
        self.Agency = Agency
        self.Contact = Contact
        self.Website = Website

    @staticmethod
    def from_element(element: QDomElement) -> 'Operator':
        """
        Constructs an Operator from a DOM element
        """
        parser = ElementParser(element)
        return Operator(Agency=parser.string('Agency'),
                        Contact=parser.person('Contact', optional=True),
                        Website=parser.string('Website', optional=True))


class Person(QuakeMlElement):
    """
    Person
    """

    def __init__(self, Name, Agency, Email, Phone):
        self.Name = Name
        self.Agency = Agency
        self.Email = Email
        self.Phone = Phone

    @staticmethod
    def from_element(element: QDomElement) -> 'Person':
        """
        Constructs a Person from a DOM element
        """
        parser = ElementParser(element)
        return Person(Name=parser.string('Name', optional=True),
                      Agency=parser.string('Agency', optional=True),
                      Email=parser.string('Email', optional=True),
                      Phone=parser.phone_number('Phone', optional=True))


class PhoneNumber(QuakeMlElement):
    """
    PhoneNumber
    """

    def __init__(self, country_code, area_code, phone_number, description):
        self.CountryCode = country_code
        self.AreaCode = area_code
        self.PhoneNumber = phone_number
        self.Description = description

    @staticmethod
    def from_element(element: QDomElement) -> 'PhoneNumber':
        """
        Constructs a PhoneNumber from a DOM element
        """
        parser = ElementParser(element)
        return PhoneNumber(country_code=parser.int('CountryCode', optional=True),
                           area_code=parser.int('AreaCode'),
                           phone_number=parser.string('PhoneNumber'),
                           description=parser.string('Description', optional=True, is_attribute=True))


class ExternalReference(QuakeMlElement):
    """
    ExternalReference
    """

    def __init__(self, URI, Description):
        self.URI = URI
        self.Description = Description

    @staticmethod
    def from_element(element: QDomElement) -> 'ExternalReference':
        """
        Constructs an ExternalReference from a DOM element
        """
        parser = ElementParser(element)
        return ExternalReference(URI=parser.string('URI'),
                                 Description=parser.string('Description'))


class Origin(QuakeMlElement):
    """
    Origin
    """

    def __init__(self,  # pylint: disable=too-many-locals
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
                 origin_type,
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
        self.type = origin_type
        self.region = region
        self.evaluationMode = evaluationMode
        self.evaluationStatus = evaluationStatus
        self.comments = comments
        self.creationInfo = creationInfo
        self.originUncertainty = originUncertainty

        if (
                not self.time or not self.time.is_valid()) and self.compositeTime and self.compositeTime.can_convert_to_datetime():
            # upgrade composite time value to time value
            self.time = self.compositeTime.to_timequantity()

    @staticmethod
    def from_element(element: QDomElement) -> 'Origin':
        """
        Constructs an Origin from a DOM element
        """
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
                      origin_type=parser.origin_type('type'),
                      region=parser.string('region'),
                      evaluationMode=parser.string('evaluationMode'),
                      evaluationStatus=parser.string('evaluationStatus'),
                      comments=comments,
                      creationInfo=parser.creation_info('creationInfo'),
                      originUncertainty=origin_uncertainty)


class Comment(QuakeMlElement):
    """
    Comment
    """

    def __init__(self,
                 text,
                 comment_id,
                 creationInfo):
        self.text = text
        self.id = comment_id
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element: QDomElement) -> 'Comment':
        """
        Constructs a Comment from a DOM element
        """
        parser = ElementParser(element)
        return Comment(text=parser.string('text', optional=False),
                       comment_id=parser.resource_reference('id'),
                       creationInfo=parser.creation_info('creationInfo'))


class RealQuantity(QuakeMlElement):
    """
    RealQuantity
    """

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
    def from_element(element: QDomElement) -> 'RealQuantity':
        """
        Constructs a RealQuantity from a DOM element
        """
        parser = ElementParser(element)
        return RealQuantity(value=parser.float('value', optional=False),
                            uncertainty=parser.float('uncertainty'),
                            lowerUncertainty=parser.float('lowerUncertainty'),
                            upperUncertainty=parser.float('upperUncertainty'),
                            confidenceLevel=parser.float('confidenceLevel'))


class IntegerQuantity(QuakeMlElement):
    """
    IntegerQuantity
    """

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
    def from_element(element: QDomElement) -> 'IntegerQuantity':
        """
        Constructs an IntegerQuantity from a DOM element
        """
        parser = ElementParser(element)
        return IntegerQuantity(value=parser.int('value', optional=False),
                               uncertainty=parser.int('uncertainty'),
                               lowerUncertainty=parser.int('lowerUncertainty'),
                               upperUncertainty=parser.int('upperUncertainty'),
                               confidenceLevel=parser.int('confidenceLevel'))


class TimeQuantity(QuakeMlElement):
    """
    TimeQuantity
    """

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
    def from_element(element: QDomElement) -> 'TimeQuantity':
        """
        Constructs a TimeQuantity from a DOM element
        """
        parser = ElementParser(element)
        return TimeQuantity(value=parser.datetime('value', optional=False),
                            uncertainty=parser.float('uncertainty'),
                            lowerUncertainty=parser.float('lowerUncertainty'),
                            upperUncertainty=parser.float('upperUncertainty'),
                            confidenceLevel=parser.float('confidenceLevel'))

    def is_valid(self) -> bool:
        """
        Returns True if the time is valid
        """
        return self.value and self.value.isValid()


class Epoch(QuakeMlElement):
    """
    Epoch
    """

    def __init__(self,
                 startTime,
                 endTime):
        self.startTime = startTime
        self.endTime = endTime

    @staticmethod
    def from_element(element: QDomElement) -> 'Epoch':
        """
        Constructs a Epoch from a DOM element
        """
        parser = ElementParser(element)
        return Epoch(startTime=parser.datetime('startTime', optional=True),
                     endTime=parser.datetime('endTime', optional=True))


class CompositeTime(QuakeMlElement):
    """
    CompositeTime
    """

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
    def from_element(element) -> 'CompositeTime':
        """
        Constructs a CompositeTime from a DOM element
        """
        parser = ElementParser(element)
        return CompositeTime(year=parser.int_quantity('year', optional=True),
                             month=parser.int_quantity('month', optional=True),
                             day=parser.int_quantity('day', optional=True),
                             hour=parser.int_quantity('hour', optional=True),
                             minute=parser.int_quantity('minute', optional=True),
                             second=parser.real_quantity('second', optional=True))

    def can_convert_to_datetime(self) -> bool:
        """
        Returns True if the time can be converted to a date time
        """
        return bool(self.year and self.year.value)

    def to_timequantity(self) -> TimeQuantity:
        """
        Converts the composite time to a TimeQuantity
        """
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

        parser = ElementParser(element)
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


class MsParameters(QuakeMlElement):
    """
    MacroseismicParameters
    """

    def __init__(self,
                 publicID,
                 macroseismicEvent: List, ):
        self.publicID = publicID
        self.macroseismicEvent = macroseismicEvent  # one to many

    @staticmethod
    def from_element(element: QDomElement) -> 'MsParameters':
        """
        Constructs MsParameters from a DOM element
        """
        parser = ElementParser(element)

        events = []
        event_node = element.firstChildElement('ms:macroseismicEvent')
        while not event_node.isNull():
            events.append(MsEvent.from_element(event_node))
            event_node = event_node.nextSiblingElement('ms:macroseismicEvent')

        return MsParameters(publicID=parser.string('publicID', is_attribute=True, optional=False),
                            macroseismicEvent=events)


class MsEvent(QuakeMlElement):
    """
    MacroseismicEvent
    """

    def __init__(self,
                 publicID,
                 mdpSetReference,
                 eventReference,
                 preferredMDPSetID,
                 preferredMacroseismicOriginID,
                 creationInfo):
        self.publicID = publicID
        self.mdpSetReference = mdpSetReference
        self.eventReference = eventReference
        self.preferredMDPSetID = preferredMDPSetID
        self.preferredMacroseismicOriginID = preferredMacroseismicOriginID
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element: QDomElement) -> 'MsEvent':
        """
        Constructs a MsEvent from a DOM element
        """
        parser = ElementParser(element)

        return MsEvent(publicID=parser.string('publicID', is_attribute=True, optional=False),
                       mdpSetReference=parser.string('ms:mdpSetReference', optional=True),
                       eventReference=parser.string('ms:eventReference', optional=True),
                       preferredMDPSetID=parser.string('ms:preferredMDPSetID', optional=True),
                       preferredMacroseismicOriginID=parser.string('ms:preferredMacroseismicOriginID', optional=True),
                       creationInfo=parser.creation_info('ms:creationInfo', optional=True))


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
        parser = ElementParser(element)

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


class MsItensityValueType(QuakeMlElement):
    """
    MsItensityValueType
    """

    def __init__(self,
                 _class,
                 numeric,
                 text):
        self._class = _class
        self.numeric = numeric
        self.text = text

    @staticmethod
    def from_element(element: QDomElement) -> 'MsItensityValueType':
        """
        Constructs a MsItensityValueType from a DOM element
        """
        parser = ElementParser(element)

        return MsItensityValueType(_class=parser.string('ms:class', is_attribute=False, optional=True),
                                   numeric=parser.float('ms:numeric', optional=True),
                                   text=parser.string('ms:text', is_attribute=False, optional=True),
                                   )


class MsIntensity(QuakeMlElement):
    """
    MsIntensity
    """

    def __init__(self,
                 macroseismicScale,
                 expectedIntensity,
                 maximalCredibleIntensity,
                 minimalCredibleIntensity):
        self.macroseismicScale = macroseismicScale
        self.expectedIntensity = expectedIntensity
        self.maximalCredibleIntensity = maximalCredibleIntensity
        self.minimalCredibleIntensity = minimalCredibleIntensity

    @staticmethod
    def from_element(element: QDomElement) -> 'MsIntensity':
        """
        Constructs an MsIntensity from a DOM element
        """
        parser = ElementParser(element)

        return MsIntensity(macroseismicScale=parser.string('ms:macroseismicScale', is_attribute=False, optional=False),
                           expectedIntensity=parser.ms_intensity_value_type('ms:expectedIntensity'),
                           maximalCredibleIntensity=parser.ms_intensity_value_type('ms:maximalCredibleIntensity',
                                                                                   optional=True),
                           minimalCredibleIntensity=parser.ms_intensity_value_type('ms:minimalCredibleIntensity',
                                                                                   optional=True))


class MsPlaceName(QuakeMlElement):
    """
    MsPlaceName
    """

    def __init__(self,
                 name,
                 ms_type,
                 alternateType,
                 language,
                 epoch):
        self.name = name
        self.type = ms_type
        self.alternateType = alternateType
        self.language = language
        self.epoch = epoch

    @staticmethod
    def from_element(element: QDomElement) -> 'MsPlaceName':
        """
        Constructs a MsPlaceName from a DOM element
        """
        parser = ElementParser(element)

        return MsPlaceName(name=parser.string('ms:name', is_attribute=False, optional=False),
                           ms_type=parser.string('ms:type', is_attribute=False, optional=True),
                           alternateType=parser.string('ms:alternateType', is_attribute=False, optional=True),
                           language=parser.string('ms:language', is_attribute=False, optional=True),
                           epoch=parser.string('ms:epoch', is_attribute=False, optional=True))


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
        parser = ElementParser(element)

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
        parser = ElementParser(element)

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
        parser = ElementParser(element)

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


class Event(QuakeMlElement):
    """
    QuakeML Event
    """

    def __init__(self,
                 publicID,
                 event_type,
                 typeCertainty,
                 description,
                 preferredOriginID,
                 preferredMagnitudeID,
                 preferredFocalMechanismID,
                 creationInfo,
                 origins: Dict[str, Origin],
                 magnitudes: Dict[str, Magnitude],
                 comments):
        self.publicID = publicID
        self.type = event_type
        self.typeCertainty = typeCertainty

        # One to many join
        self.description = description

        self.preferredOriginID = preferredOriginID
        self.preferredMagnitudeID = preferredMagnitudeID
        self.preferredFocalMechanismID = preferredFocalMechanismID
        self.creationInfo = creationInfo
        self.origins: Dict[str, Origin] = origins
        self.magnitudes: Dict[str, Magnitude] = magnitudes
        self.comments = comments

    @staticmethod
    def to_fields(selected_fields: Optional[List[str]] = None) -> QgsFields:
        """
        Returns the event field definition
        """
        return get_service_fields(SERVICE_MANAGER.FDSNEVENT, selected_fields)

    @staticmethod
    def add_origin_attributes(origin: Origin,  # pylint: disable=too-many-locals,too-many-branches
                              feature: QgsFeature,
                              output_fields: Optional[List[str]],
                              convert_negative_depths: bool,
                              depth_unit: QgsUnitTypes.DistanceUnit,
                              is_preferred_origin: bool):
        """
        Adds origin related attributes to a feature
        """
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        if output_fields:
            output_is_preferred_origin = '!IsPrefOrigin' in output_fields
        else:
            output_is_preferred_origin = settings.value('/plugins/qquake/output_field_!IsPrefOrigin', False, bool)
        if output_is_preferred_origin:
            dest_field = \
                [f for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields'] if
                 f['source'] == '!IsPrefOrigin'][
                    0]
            feature[dest_field[field_config_key]] = is_preferred_origin or NULL

        for dest_field in CONFIG_FIELDS['field_groups']['origin']['fields']:
            if dest_field.get('skip'):
                continue

            if dest_field.get('one_to_many'):
                continue

            is_depth_field = dest_field['source'] == "eventParameters>event>origin>depth>value"

            source = dest_field['source'].replace('§', '>').split('>')
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

            if is_depth_field and source_obj != NULL and source_obj is not None:
                if depth_unit == QgsUnitTypes.DistanceKilometers:
                    source_obj /= 1000
                if convert_negative_depths:
                    source_obj = -source_obj

            feature[dest_field[field_config_key]] = source_obj

        if origin.depth is not None and origin.longitude is not None and origin.latitude is not None:
            geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value,
                            z=-origin.depth.value * 1000)
        elif origin.longitude is not None and origin.latitude is not None:
            geom = QgsPoint(x=origin.longitude.value, y=origin.latitude.value)
        else:
            geom = QgsGeometry()
        feature.setGeometry(QgsGeometry(geom))

    @staticmethod
    def add_magnitude_attributes(magnitude: Magnitude,
                                 feature: QgsFeature,
                                 output_fields: Optional[List[str]],
                                 is_preferred_magnitude: bool):
        """
        Adds magnitude related attributes to a feature
        """
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        if output_fields:
            output_is_preferred_mag = '!IsPrefMag' in output_fields
        else:
            output_is_preferred_mag = settings.value('/plugins/qquake/output_field_!IsPrefMag', False, bool)
        if output_is_preferred_mag:
            dest_field = \
                [f for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields'] if f['source'] == '!IsPrefMag'][
                    0]
            feature[dest_field[field_config_key]] = is_preferred_magnitude or NULL

        for dest_field in CONFIG_FIELDS['field_groups']['magnitude']['fields']:
            if dest_field.get('skip'):
                continue

            if dest_field.get('one_to_many'):
                continue

            source = dest_field['source'].replace('§', '>').split('>')
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
                if source_obj is None:
                    source_obj = NULL
                    break

            feature[dest_field[field_config_key]] = source_obj

    def to_features(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                    output_fields: Optional[List[str]],
                    preferred_origin_only: bool,
                    preferred_magnitudes_only: bool, all_origins,
                    convert_negative_depths, depth_unit) -> QgsFeature:
        """
        Yields event features
        """
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        f = QgsFeature(self.to_fields(output_fields))
        for dest_field in CONFIG_FIELDS['field_groups']['basic_event_info']['fields']:
            if dest_field.get('skip'):
                continue

            if dest_field.get('one_to_many'):
                continue

            if dest_field['source'].startswith('!'):
                continue

            source = dest_field['source'].replace('§', '>').split('>')
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
                if isinstance(source_obj, list):
                    # hack to handle 1:many joins for now -- discard all but first
                    source_obj = source_obj[0]

            f[dest_field[field_config_key]] = source_obj

        origins_handled = set()
        for _, m in self.magnitudes.items():

            is_preferred_magnitude = m.publicID == self.preferredMagnitudeID
            if preferred_magnitudes_only and not is_preferred_magnitude:
                continue

            if m.originID not in all_origins:
                raise MissingOriginException(
                    f'Origin with ID {m.originID} is not present in QuakeML file -- cannot be parsed')

            magnitude_origin = all_origins[m.originID]

            is_preferred_origin = magnitude_origin.publicID == self.preferredOriginID
            if preferred_origin_only and not is_preferred_origin:
                continue

            magnitude_feature = QgsFeature(f)

            self.add_magnitude_attributes(m, magnitude_feature, output_fields, is_preferred_magnitude)
            self.add_origin_attributes(magnitude_origin, magnitude_feature, output_fields,
                                       convert_negative_depths=convert_negative_depths,
                                       depth_unit=depth_unit, is_preferred_origin=is_preferred_origin)

            origins_handled.add(m.originID)

            yield magnitude_feature

        for _, o in self.origins.items():
            is_preferred_origin = o.publicID == self.preferredOriginID
            if preferred_origin_only and not is_preferred_origin:
                continue

            if o.publicID in origins_handled:
                continue

            origin_feature = QgsFeature(f)
            self.add_origin_attributes(o, origin_feature, output_fields,
                                       convert_negative_depths=convert_negative_depths,
                                       depth_unit=depth_unit, is_preferred_origin=is_preferred_origin)

            yield origin_feature

    @staticmethod
    def from_element(element: QDomElement) -> 'Event':
        """
        Constructs an Event from a DOM element
        """
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
                     event_type=parser.string('type'),
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

    def __init__(self,
                 convert_negative_depths=False,
                 depth_unit=QgsUnitTypes.DistanceMeters):
        self.events = []
        self.origins = {}
        self.magnitudes = {}
        self.macro_places = {}
        self.macro_events = {}
        self.mdps = {}
        self.mdpsets = {}
        self.convert_negative_depths = convert_negative_depths
        self.depth_unit = depth_unit

    def to_dict(self) -> Dict[str, object]:
        """
        Returns the results as a dictionary
        """
        return {
            'events': [v.to_dict() for v in self.events],
            'origins': {k: v.to_dict() for k, v in self.origins.items()},
            'magnitudes': {k: v.to_dict() for k, v in self.magnitudes.items()},
            'macro_places': {k: v.to_dict() for k, v in self.macro_places.items()},
            'macro_events': {k: v.to_dict() for k, v in self.macro_events.items()},
            'mdps': {k: v.to_dict() for k, v in self.mdps.items()},
            'mdpsets': {k: v.to_dict() for k, v in self.mdpsets.items()},
        }

    def parse_initial(self, content: QByteArray):
        """
        Parses the initial first reply
        """
        self.events = []
        self.origins = {}
        self.magnitudes = {}
        self.macro_events = {}
        self.macro_places = {}
        self.mdps = {}
        self.mdpsets = {}
        self.add_events(content)

    def remap_attribute_name(self, service_type: str, attribute: str) -> str:
        """
        Returns a remapped attribute name (i.e. accounting for user-defined output attribute names)
        """
        if not attribute:
            return attribute

        return get_service_fields(service_type, [attribute]).at(0).name()

    def add_events(self, content: QByteArray):  # pylint:disable=too-many-locals
        """
        Adds events from a reply
        """
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

        macro_events = doc.elementsByTagName('ms:macroseismicEvent')
        for e in range(macro_events.length()):
            macro_event_element = macro_events.at(e).toElement()
            macro_event = MsEvent.from_element(macro_event_element)
            self.macro_events[macro_event.publicID] = macro_event

        mdpset_elements = doc.elementsByTagName('ms:mdpSet')
        for e in range(mdpset_elements.length()):
            mdpset_element = mdpset_elements.at(e).toElement()
            mdpset = MsMdpSet.from_element(mdpset_element)
            self.mdpsets[mdpset.publicID] = mdpset

    def mdp_set_for_mdp(self, mdp: MsMdp) -> MsMdpSet:
        """
        Returns the MDP set associated with an mdp
        """
        return [v for k, v in self.mdpsets.items() if mdp.publicID in v.mdpReferences][0]

    def parse_missing_origin(self, content: QByteArray):
        """
        Parses for missing origins from a reply
        """
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

    def scan_for_missing_origins(self) -> List[str]:
        """
        Returns a list of events missing the origin
        """
        missing_origins = set()
        for e in self.events:
            if e.preferredOriginID not in self.origins:
                missing_origins.add(e.preferredOriginID)

            for _, m in e.magnitudes.items():
                if m.originID not in self.origins:
                    missing_origins.add(m.originID)

        return list(missing_origins)

    @staticmethod
    def to_event_fields(selected_fields: Optional[List[str]]) -> QgsFields:
        """
        Returns the field definition for events
        """
        return Event.to_fields(selected_fields)

    def create_event_features(self, output_fields: List[str], preferred_origin_only: bool,
                              preferred_magnitudes_only: bool) -> QgsFeature:
        """
        Yields event features
        """
        for e in self.events:
            for f in e.to_features(output_fields, preferred_origin_only, preferred_magnitudes_only,
                                   all_origins=self.origins,
                                   convert_negative_depths=self.convert_negative_depths,
                                   depth_unit=self.depth_unit):
                yield f

    @staticmethod
    def create_mdp_fields(selected_fields: Optional[List[str]]) -> QgsFields:
        """
        Creates the MDP field definitions
        """
        return get_service_fields(SERVICE_MANAGER.MACROSEISMIC, selected_fields)

    def create_mdp_features(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                            selected_fields: Optional[List[str]],
                            preferred_mdp_set_only: bool) -> QgsFeature:
        """
        Yields MDP features
        """
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'
        field_config = SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.MACROSEISMIC)

        include_quake_details_in_mdp = settings.value('/plugins/qquake/include_quake_details_in_mdp', True, bool)

        fields = self.create_mdp_fields(selected_fields)
        for _, m in self.mdps.items():
            if m.placeReference in self.macro_places:
                place = self.macro_places[m.placeReference]
            else:
                place = None

            event_reference = m.eventReference
            # try to get macroseismicEvent
            macro_events = [m for m in self.macro_events.values() if m.eventReference == event_reference]
            macro_event = macro_events[0] if macro_events else None

            mdpset = self.mdp_set_for_mdp(m)

            is_preferred_mdp_set = False
            if macro_event is not None:
                preferred_mdp_set_id = macro_event.preferredMDPSetID
                is_preferred_mdp_set = mdpset.publicID == preferred_mdp_set_id

            if preferred_mdp_set_only and not is_preferred_mdp_set:
                # not in the preferred mdp set, so skip
                continue

            f = QgsFeature(fields)

            if selected_fields:
                output_is_preferred_mdpset = '!IsPrefMdpset' in selected_fields
            else:
                output_is_preferred_mdpset = settings.value('/plugins/qquake/output_field_!IsPrefMdpset', False,
                                                            bool)
            if output_is_preferred_mdpset:
                dest_field = [f for f in field_config['field_groups']['basic_event_info']['fields'] if
                              f['source'] == '!IsPrefMdpset'][0]
                f[dest_field[field_config_key]] = is_preferred_mdp_set or NULL

            for dest_field in field_config['field_groups']['basic_event_info']['fields']:
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                if not include_quake_details_in_mdp and '>event>' in dest_field['source'] and dest_field[
                    'source'] != 'eventParameters>event§publicID':
                    continue

                if dest_field['source'].startswith('!'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')

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

                source_obj = [e for e in self.events if e.publicID == m.eventReference][0]
                for s in source:
                    if source_obj is None:
                        source_obj = NULL
                        break
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field[field_config_key]] = source_obj

            if include_quake_details_in_mdp:

                if selected_fields:
                    output_is_preferred_origin = '!IsPrefOrigin' in selected_fields
                else:
                    output_is_preferred_origin = settings.value('/plugins/qquake/output_field_!IsPrefOrigin', False,
                                                                bool)
                if output_is_preferred_origin:
                    dest_field = [f for f in field_config['field_groups']['basic_event_info']['fields'] if
                                  f['source'] == '!IsPrefOrigin'][0]
                    f[dest_field[field_config_key]] = True

                for dest_field in field_config['field_groups']['origin']['fields']:
                    if dest_field.get('skip'):
                        continue

                    if dest_field.get('one_to_many'):
                        continue

                    source = dest_field['source'].replace('§', '>').split('>')
                    assert source[0] == 'eventParameters'
                    source = source[1:]
                    assert source[0] == 'event'
                    source = source[1:]
                    assert source[0] == 'origin'
                    source = source[1:]

                    if selected_fields:
                        selected = dest_field['source'] in selected_fields
                    else:
                        selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True,
                                                  bool)

                    if not selected:
                        continue

                    event = [e for e in self.events if e.publicID == m.eventReference][0]
                    origin = self.origins[event.preferredOriginID]

                    source_obj = origin

                    for s in source:
                        if source_obj is None:
                            source_obj = NULL
                            break
                        assert hasattr(source_obj, s)
                        source_obj = getattr(source_obj, s)

                    f[dest_field[field_config_key]] = source_obj

            if include_quake_details_in_mdp:

                if selected_fields:
                    output_is_preferred_mag = '!IsPrefMag' in selected_fields
                else:
                    output_is_preferred_mag = settings.value('/plugins/qquake/output_field_!IsPrefMag', False, bool)
                if output_is_preferred_mag:
                    dest_field = [f for f in CONFIG_FIELDS['field_groups']['basic_event_info']['fields'] if
                                  f['source'] == '!IsPrefMag'][0]
                    f[dest_field[field_config_key]] = True

                for dest_field in field_config['field_groups']['magnitude']['fields']:
                    if dest_field.get('skip'):
                        continue

                    if dest_field.get('one_to_many'):
                        continue

                    source = dest_field['source'].replace('§', '>').split('>')
                    assert source[0] == 'eventParameters'
                    source = source[1:]
                    assert source[0] == 'event'
                    source = source[1:]
                    assert source[0] == 'magnitude'
                    source = source[1:]

                    if selected_fields:
                        selected = dest_field['source'] in selected_fields
                    else:
                        selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True,
                                                  bool)

                    if not selected:
                        continue

                    event = [e for e in self.events if e.publicID == m.eventReference][0]
                    source_obj = self.magnitudes[event.preferredMagnitudeID]
                    for s in source:
                        if source_obj is None:
                            source_obj = NULL
                            break
                        assert hasattr(source_obj, s)
                        source_obj = getattr(source_obj, s)

                    f[dest_field[field_config_key]] = source_obj

            for dest_field in field_config['field_groups'].get('mdp', {}).get('fields', []):
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')
                assert source[0] == 'macroseismicParameters'
                source = source[1:]
                assert source[0] == 'mdp'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)

                if not selected:
                    continue

                source_obj = m
                for s in source:
                    if source_obj is None:
                        source_obj = NULL
                        break

                    if s == 'class':
                        # reserved keyword, can't use!
                        s = '_class'

                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field[field_config_key]] = source_obj

            for dest_field in field_config['field_groups'].get('place', {}).get('fields', []):
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')
                assert source[0] == 'macroseismicParameters'
                source = source[1:]
                assert source[0] == 'place'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)

                if not selected:
                    continue

                source_obj = place
                for s in source:
                    if source_obj is None:
                        source_obj = NULL
                        break
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field[field_config_key]] = source_obj

            for dest_field in field_config['field_groups'].get('macro_basic_event_info', {}).get('fields', []):
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')
                assert source[0] == 'macroseismicParameters'
                source = source[1:]
                assert source[0] == 'macroseismicEvent'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)

                if not selected:
                    continue

                source_obj = macro_event
                if source_obj is None:
                    continue

                for s in source:
                    if source_obj is None:
                        source_obj = NULL
                        break
                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field[field_config_key]] = source_obj

            for dest_field in field_config['field_groups'].get('mdpSet', {}).get('fields', []):
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')
                assert source[0] == 'macroseismicParameters'
                source = source[1:]
                assert source[0] == 'mdpSet'
                source = source[1:]

                if selected_fields:
                    selected = dest_field['source'] in selected_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True, bool)

                if not selected:
                    continue

                source_obj = mdpset
                for s in source:
                    if source_obj is None:
                        source_obj = NULL
                        break

                    if s == 'class':
                        # reserved keyword, can't use!
                        s = '_class'

                    assert hasattr(source_obj, s)
                    source_obj = getattr(source_obj, s)

                f[dest_field[field_config_key]] = source_obj

            if place and place.referenceLongitude and place.referenceLatitude:
                geom = QgsPoint(x=place.referenceLongitude.value, y=place.referenceLatitude.value)
                f.setGeometry(QgsGeometry(geom))

            yield f


class BaseNodeType(QuakeMlElement):
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
    def _from_element(obj: 'BaseNodeType', element: QDomElement):
        """
        Populates the base node attributes from a DOM element
        """
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

    def to_dict(self) -> Dict[str, object]:
        """
        Returns a dictionary representing the network
        """
        return {
            'stations': [s.to_dict() for s in self.stations]
        }

    def to_station_features(self, selected_fields: Optional[List[str]]) -> List[QgsFeature]:
        """
        Converts the network to a list of station features
        """
        features = []
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for o in self.stations:
            f = QgsFeature(Station.to_fields(selected_fields))
            for dest_field in SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.FDSNSTATION)['field_groups']['station'][
                'fields']:
                if dest_field.get('skip'):
                    continue

                if dest_field.get('one_to_many'):
                    continue

                source = dest_field['source'].replace('§', '>').split('>')
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
    def from_element(element: QDomElement) -> 'Network':
        """
        Constructs a Network from a DOM element
        """
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

    def __init__(self,  # pylint: disable=too-many-locals
                 start_date,
                 end_date,
                 latitude,
                 longitude,
                 elevation,
                 site,
                 water_level,
                 vault,
                 geology,
                 equipment,
                 operator,
                 creation_date,
                 termination_date,
                 total_number_channels,
                 selected_number_channels,
                 external_reference
                 # Channel
                 ):
        super().__init__(None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None)
        self.StartDate = start_date
        self.EndDate = end_date
        self.Latitude = latitude
        self.Longitude = longitude
        self.Elevation = elevation
        self.Site = site
        self.WaterLevel = water_level
        self.Vault = vault
        self.Geology = geology
        self.CreationDate = creation_date
        self.TerminationDate = termination_date
        self.TotalNumberChannels = total_number_channels
        self.SelectedNumberChannels = selected_number_channels
        self.Equipment = equipment
        self.Operator = operator
        self.ExternalReference = external_reference

    @staticmethod
    def to_fields(selected_fields: Optional[List[str]]) -> QgsFields:
        """
        Returns station fields
        """
        fields = QgsFields()
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for f in SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.FDSNSTATION)['field_groups']['station']['fields']:
            if f.get('skip'):
                continue

            if f.get('one_to_many'):
                continue

            path = f['source']
            if selected_fields:
                selected = path in selected_fields
            else:
                path = path[len('FDSNStationXML>Network>'):].replace('§', '>').replace('>', '_')
                selected = settings.value('/plugins/qquake/output_field_{}'.format(path), True, bool)
            if not selected:
                continue

            fields.append(QgsField(f[field_config_key], FIELD_TYPE_MAP[f['type']]))
        return fields

    @staticmethod
    def from_element(element: QDomElement) -> 'Station':
        """
        Constructs a Station from a DOM element
        """
        parser = ElementParser(element)
        res = Station(
            start_date=parser.datetime('startDate', is_attribute=True, optional=True),
            end_date=parser.datetime('endDate', is_attribute=True, optional=True),
            latitude=parser.float('Latitude', optional=False),
            longitude=parser.float('Longitude', optional=False),
            elevation=parser.float('Elevation', optional=False),
            site=parser.site('Site', optional=False),
            equipment=parser.equipment('Equipment', optional=True),
            water_level=parser.float('WaterLevel'),
            vault=parser.string('Vault'),
            geology=parser.string('Geology'),
            creation_date=parser.datetime('CreationDate'),
            termination_date=parser.datetime('TerminationDate'),
            total_number_channels=parser.int('TotalNumberChannels'),
            selected_number_channels=parser.int('SelectedNumberChannels'),
            operator=parser.operator('Operator', optional=True),
            external_reference=parser.external_reference('ExternalReference', optional=True)
        )
        BaseNodeType._from_element(res, element)
        return res


class FDSNStationXMLParser:
    """
    FDSNStationXML parser
    """

    @staticmethod
    def parse(content: QByteArray) -> List[Network]:
        """
        Parses content
        """
        doc = QDomDocument()
        doc.setContent(content)
        network_elements = doc.elementsByTagName('Network')

        networks = []
        for e in range(network_elements.length()):
            network_element = network_elements.at(e).toElement()
            networks.append(Network.from_element(network_element))

        return networks

    @staticmethod
    def remap_attribute_name(attribute: str) -> str:
        """
        Returns a remapped attribute name (i.e. accounting for user-defined output attribute names)
        """
        if not attribute:
            return attribute
        return get_service_fields(SERVICE_MANAGER.FDSNSTATION, [attribute]).at(0).name()
