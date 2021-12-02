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

from typing import Dict

from qgis.PyQt.QtXml import QDomElement

from .base_node import BaseNodeType
from .station import Station


class Network(BaseNodeType):
    """
    This type represents the Network layer, all station metadata is contained within this element.
    The official name of the network or other descriptive information can be included in the
    Description element. The Network can contain 0 or more Stations.
    """

    def __init__(self,
                 stations,
                 operator,
                 total_number_stations,
                 selected_number_stations):
        super().__init__(None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None)
        self.stations = stations
        self.Operator = operator
        self.TotalNumberStations = total_number_stations
        self.SelectedNumberStations = selected_number_stations

    def to_dict(self) -> Dict[str, object]:
        """
        Returns a dictionary representing the network
        """
        res = super().to_dict()
        res['stations'] = [s.to_dict() for s in self.stations]
        return res

    @staticmethod
    def from_element(element: QDomElement) -> 'Network':
        """
        Constructs a Network from a DOM element
        """
        station_nodes = element.elementsByTagName('Station')
        stations = []
        for e in range(station_nodes.length()):
            stations.append(Station.from_element(station_nodes.at(e).toElement()))

        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        res = Network(stations=stations,
                      operator=parser.operator('Operator', optional=True),
                      total_number_stations=parser.int('TotalNumberStations', optional=True),
                      selected_number_stations=parser.int('SelectedNumberStations', optional=True),
                      )
        BaseNodeType._from_element(res, element)
        return res
