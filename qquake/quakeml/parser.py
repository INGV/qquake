# -*- coding: utf-8 -*-
"""
QuakeML parser
"""

# .. note:: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

__author__ = 'Original authors: Mario Locati, Roberto Vallone, Matteo Ghetta, Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Istituto Nazionale di Geofisica e Vulcanologia (INGV)'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from typing import Optional, Dict, List

from qgis.PyQt.QtCore import (
    QByteArray
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    NULL,
    QgsUnitTypes,
    QgsFields,
    QgsFeature,
    QgsSettings,
    QgsPoint,
    QgsGeometry
)

from qquake.services import SERVICE_MANAGER
from .fields import (
    CONFIG_FIELDS,
    get_service_fields
)
from .fdsn_event import (
    Event
)
from .macroseismic import (
    MsPlace,
    MsEvent,
    MsMdp,
    MsMdpSet
)


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
