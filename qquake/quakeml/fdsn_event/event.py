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

from typing import Dict, Optional, List

from qgis.PyQt.QtXml import QDomElement
from qgis.core import (
    QgsFields,
    QgsFeature,
    QgsUnitTypes,
    QgsSettings,
    QgsPoint,
    QgsGeometry,
    NULL
)

from qquake.services import SERVICE_MANAGER
from .event_description import EventDescription
from .magnitude import Magnitude
from .origin import Origin
from ..common import Comment
from ..element import QuakeMlElement
from ..exceptions import MissingOriginException
from ..fields import (
    CONFIG_FIELDS,
    get_service_fields
)


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
    def add_origin_attributes(origin: Origin,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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

        # link associated components
        for dest_field in CONFIG_FIELDS['field_groups']['origin']['fields']:
            if dest_field.get('skip') or dest_field.get('one_to_many'):
                continue

            associated_components = dest_field.get('associated_components')
            if not associated_components:
                continue

            composite_value = feature[dest_field[field_config_key]]
            if not composite_value or not composite_value.isValid():
                continue

            # find field linked to associated component and populate if empty
            for component, source in associated_components.items():
                if output_fields:
                    selected = source in output_fields
                else:
                    selected = settings.value('/plugins/qquake/output_field_{}'.format('_'.join(source)), True,
                                              bool)
                if not selected:
                    continue

                matching_field = [field for field in CONFIG_FIELDS['field_groups']['origin']['fields'] if
                                  field['source'] == source]
                assert matching_field

                current_value = feature[matching_field[0][field_config_key]]
                if current_value and current_value != NULL:
                    continue

                if component == 'year':
                    component_value = composite_value.date().year()
                elif component == 'month':
                    component_value = composite_value.date().month()
                elif component == 'day':
                    component_value = composite_value.date().day()
                elif component == 'hour':
                    component_value = composite_value.time().hour()
                elif component == 'minute':
                    component_value = composite_value.time().minute()
                elif component == 'second':
                    component_value = composite_value.time().second()
                else:
                    assert False

                feature[matching_field[0][field_config_key]] = component_value

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
        from .element_parser import FDSNEventElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNEventElementParser(element)

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
