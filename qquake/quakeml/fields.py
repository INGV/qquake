# -*- coding: utf-8 -*-
"""
Field configuration
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

import json
import os
from typing import Optional, List

from qgis.PyQt.QtCore import (
    QVariant
)
from qgis.core import (
    QgsField,
    QgsFields,
    QgsSettings
)

from qquake.services import SERVICE_MANAGER

CONFIG_FIELDS_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'config',
    'config_fields_fdsnevent.json')

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
