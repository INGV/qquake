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

from typing import Optional, List

from qgis.PyQt.QtXml import QDomElement
from qgis.core import (
    QgsField,
    QgsFields,
    QgsSettings,
)

from qquake.services import SERVICE_MANAGER
from .base_node import BaseNodeType


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
        from ..fields import FIELD_TYPE_MAP  # pylint: disable=import-outside-toplevel

        fields = QgsFields()
        settings = QgsSettings()

        short_field_names = settings.value('/plugins/qquake/output_short_field_names', True, bool)
        field_config_key = 'field_short' if short_field_names else 'field_long'

        for group in ['general', 'network', 'station']:
            for f in SERVICE_MANAGER.get_field_config(SERVICE_MANAGER.FDSNSTATION)['field_groups'][group]['fields']:
                if f.get('skip'):
                    continue

                if f.get('one_to_many'):
                    continue

                path = f['source']
                if selected_fields:
                    selected = path in selected_fields
                else:
                    path = path[len('FDSNStationXML>'):].replace('§', '>').replace('>', '_')
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
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
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
