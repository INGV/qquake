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

from typing import Dict, List, Optional

from qgis.PyQt.QtXml import QDomElement
from qgis.core import (
    QgsFeature,
    QgsSettings,
    QgsPoint,
    QgsGeometry
)

from qquake.services import SERVICE_MANAGER
from .base_node import BaseNodeType
from .station import Station


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
