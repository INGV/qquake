# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuakeDialog
                                 A QGIS plugin
 QQuake plugin to download seismologic data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Faunalia
        email                : matteo.ghetta@faunalia.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import json
from copy import deepcopy
from pathlib import Path
from qgis.core import (
    QgsApplication,
    QgsMessageLog,
    Qgis
)
from qgis.PyQt.QtCore import QObject, pyqtSignal

_CONFIG_SERVICES_PATH = os.path.join(
    os.path.dirname(__file__),
    'config',
    'config.json')


def load_field_config(filename):
    path = os.path.join(
        os.path.dirname(__file__),
        'config', filename)

    with open(path, 'r') as f:
        return json.load(f)


class ServiceManager(QObject):
    FDSNEVENT = 'fdsnevent'
    FDSNSTATION = 'fdsnstation'
    MACROSEISMIC = 'macroseismic'
    WMS = 'wms'
    WFS = 'wfs'

    _SERVICE_TYPES = [FDSNEVENT, FDSNSTATION, MACROSEISMIC, WMS, WFS]

    _CONFIG_FIELDS = {
        FDSNEVENT: load_field_config('config_fields_fsdnevent.json'),
        MACROSEISMIC: load_field_config('config_fields_macroseismic.json'),
        FDSNSTATION: load_field_config('config_fields_station.json')
    }

    PRESET_STYLES = {}

    refreshed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.services = {}
        self.refresh_services()

    def refresh_services(self):
        # load the default services
        with open(_CONFIG_SERVICES_PATH, 'r') as f:
            default_services = json.load(f)

        self.services = {}
        for service_type in self._SERVICE_TYPES:
            self.services[service_type] = {}
            for service_id, service in default_services[service_type].items():
                service['read_only'] = True

                self.services[service_type][service_id] = service

        for name, style in default_services['styles'].items():
            self.PRESET_STYLES[name] = style

        self._predefined_bounding_boxes = default_services['boundingboxpredefined']

        # next load user services
        user_path = self.user_service_path()
        if not user_path.exists():
            user_path.mkdir(parents=True)

        for service_type in self._SERVICE_TYPES:
            service_path = user_path / service_type
            if not service_path.exists():
                service_path.mkdir(parents=True)

            for p in service_path.glob('**/*.json'):
                service = self.create_from_file(p)
                if not service:
                    continue

                service['read_only'] = False

                if p.stem in self.services[service_type]:
                    # duplicate service, skip it
                    QgsMessageLog.logMessage(
                        'Duplicate service name found, service will not be loaded: {}'.format(p.stem), 'QQuake',
                        Qgis.Warning)
                    continue

                self.services[service_type][p.stem] = service

        self.refreshed.emit()

    def create_from_file(self, path):
        with open(path, 'r') as f:
            try:
                service = json.load(f)
            except json.JSONDecodeError:
                return None

        return service

    @staticmethod
    def user_service_path():
        return Path(QgsApplication.qgisSettingsDirPath()) / 'QQuake'

    def available_services(self, service_type):
        return self.services[service_type].keys()

    def service_details(self, service_type, service_id):
        return self.services[service_type][service_id]

    def available_predefined_bounding_boxes(self):
        return self._predefined_bounding_boxes.keys()

    def predefined_bounding_box(self, name):
        return self._predefined_bounding_boxes[name]

    def custom_service_path(self, service_type, service_id):
        return (self.user_service_path() / service_type / service_id).with_suffix('.json')

    def remove_service(self, service_type, service_id):
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.unlink()
            self.refresh_services()

    def rename_service(self, service_type, service_id, new_name):
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.rename(self.custom_service_path(service_type, new_name))
            self.refresh_services()

    def export_service(self, service_type, service_id, path):
        config = deepcopy(self.service_details(service_type, service_id))
        config['servicetype'] = service_type
        config['serviceid'] = service_id

        with open(path, 'wt') as f:
            f.write(json.dumps(config, indent=4))
        return True

    def import_service(self, path):
        service = self.create_from_file(path)
        if not service:
            return False, 'Error reading service definition'

        service['read_only'] = False

        if 'serviceid' in service:
            service_id = service['serviceid']
        else:
            service_id = Path(path).stem

        if not 'servicetype' in service:
            return False, 'Incomplete service definition'

        service_type = service['servicetype']

        if service_id in self.services[service_type]:
            # duplicate service, skip it
            QgsMessageLog.logMessage(
                'Duplicate service name found, service will not be loaded: {}'.format(service_id), 'QQuake',
                Qgis.Warning)
            return False, 'A duplicate service name was found'

        self.save_service(service_type, service_id, service)

        return True, ''

    def save_service(self, service_type, service_id, configuration):
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.unlink()

        with open(path, 'wt') as f:
            f.write(json.dumps(configuration, indent=4))
        self.refresh_services()

    def get_field_config(self, service_type):
        return self._CONFIG_FIELDS[service_type]


SERVICE_MANAGER = ServiceManager()
