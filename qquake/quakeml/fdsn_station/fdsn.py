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

from typing import List, Optional

from qgis.PyQt.QtXml import QDomElement
from qgis.core import (
    QgsFeature,
    QgsSettings,
    QgsPoint,
    QgsGeometry
)

from qquake.services import SERVICE_MANAGER
from .station import Station
from ..element import QuakeMlElement


class Fdsn(QuakeMlElement):
    """
    Root type for FDSN
    """

    def __init__(self,
                 source,
                 sender,
                 module,
                 module_uri,
                 created,
                 networks,
                 schema_version
                 ):
        self.Source = source
        self.Sender = sender
        self.Module = module
        self.ModuleURI = module_uri
        self.Created = created
        self.networks = networks
        self.schemaVersion = schema_version

    @staticmethod
    def from_element(element: QDomElement) -> 'Fdsn':
        """
        Constructs a DataAvailability from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)

        network_elements = element.elementsByTagName('Network')

        from .network import Network  # pylint: disable=import-outside-toplevel
        networks = []
        for e in range(network_elements.length()):
            network_element = network_elements.at(e).toElement()
            networks.append(Network.from_element(network_element))

        return Fdsn(
            source=parser.string('Source'),
            sender=parser.string('Sender', optional=True),
            module=parser.string('Module', optional=True),
            module_uri=parser.string('ModuleURI', optional=True),
            created=parser.datetime('Created', optional=False),
            networks=networks,
            schema_version=parser.float('schemaVersion', is_attribute=True)
        )

    def to_station_features(self, selected_fields: Optional[List[str]]) -> List[QgsFeature]:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Converts the network to a list of station features
        """
        features = []
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        general_feature = QgsFeature(Station.to_fields(selected_fields))

        for dest_field in SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.FDSNSTATION)['field_groups']['general'][
            'fields']:
            if dest_field.get('skip'):
                continue

            if dest_field.get('one_to_many'):
                continue

            source = dest_field['source'].replace('§', '>').split('>')
            assert source[0] == 'FDSNStationXML'
            source = source[1:]
            source_obj = self

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

            general_feature[dest_field[field_config_key]] = source_obj

        for network in self.networks:
            network_feature = QgsFeature(general_feature)

            for dest_field in SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.FDSNSTATION)['field_groups']['network'][
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
                source_obj = network

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

                network_feature[dest_field[field_config_key]] = source_obj

            for o in network.stations:
                f = QgsFeature(network_feature)
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
