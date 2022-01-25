# -*- coding: utf-8 -*-
"""
Service manager
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
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.core import (
    QgsApplication,
    QgsMessageLog,
    Qgis
)

_CONFIG_SERVICES_PATH = os.path.join(
    os.path.dirname(__file__),
    '../config',
    'config.json')


def load_field_config(filename: str) -> dict:
    """
    Loads a configuration JSON file and returns as a dict
    """
    path = os.path.join(
        os.path.dirname(__file__),
        '../config', filename)

    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


class ServiceManager(QObject):  # pylint:disable=too-many-public-methods
    """
    Manages available services
    """

    FDSNEVENT = 'fdsnevent'
    FDSNSTATION = 'fdsnstation'
    MACROSEISMIC = 'macroseismic'
    WMS = 'wms'
    WFS = 'wfs'
    WCS = 'wcs'

    _SERVICE_TYPES = [FDSNEVENT, FDSNSTATION, MACROSEISMIC, WMS, WFS, WCS]

    _CONFIG_FIELDS = {
        FDSNEVENT: load_field_config('config_fields_fdsnevent.json'),
        MACROSEISMIC: load_field_config('config_fields_macroseismic.json'),
        FDSNSTATION: load_field_config('config_fields_station.json')
    }

    PRESET_STYLES = {}

    refreshed = pyqtSignal()
    areasChanged = pyqtSignal()
    user_styles_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.services = {}
        self._user_styles = {}
        self.contributors = defaultdict(dict)
        self.refresh_services()
        self._load_predefined_areas()
        self._load_user_styles()

    def refresh_services(self):
        """
        Refreshes the available services
        """

        # load the default services
        with open(_CONFIG_SERVICES_PATH, 'r', encoding='utf8') as f:
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
        for _, v in self._predefined_bounding_boxes.items():
            v['read_only'] = True

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

        self._load_predefined_areas()
        self.refreshed.emit()

    @staticmethod
    def create_from_file(path) -> Optional[dict]:
        """
        Creates a service from a file
        """
        with open(path, 'r', encoding='utf8') as f:
            try:
                service = json.load(f)
            except json.JSONDecodeError:
                return None

        return service

    @staticmethod
    def user_service_path() -> Path:
        """
        Returns the path to the user settings folder
        """
        return Path(QgsApplication.qgisSettingsDirPath()) / 'QQuake'

    def available_services(self, service_type: str) -> List[str]:
        """
        Returns a list of services of the specified type
        """
        return self.services[service_type].keys()

    def service_details(self, service_type: str, service_id: str) -> dict:
        """
        Returns the details of a specific service
        """
        details = self.services[service_type][service_id]

        # auto update older formats
        if details.get('info') and not details.get('servicedescription'):
            details['servicedescription'] = details['info']
        if details.get('infourl') and not details.get('servicedescriptionurl'):
            details['servicedescriptionurl'] = details['infourl']

        return details

    def available_predefined_bounding_boxes(self) -> List[str]:
        """
        Returns the names of the available predefined bounding boxes
        """
        return self._predefined_bounding_boxes.keys()

    def predefined_bounding_box(self, name: str) -> dict:
        """
        Returns the definition of a predefined bounding box
        """
        return self._predefined_bounding_boxes[name]

    def _load_predefined_areas(self):
        """
        Loads all predefined areas
        """
        path = self.user_service_path() / 'predefined_areas.json'
        try:
            with open(path, 'rt', encoding='utf8') as f:
                try:
                    areas = json.load(f)
                except json.JSONDecodeError:
                    return

                new_areas = {k: v for k, v in self._predefined_bounding_boxes.items() if v.get('read_only')}

                for k, v in areas.items():
                    new_areas[k] = v

                self._predefined_bounding_boxes = new_areas
                self.areasChanged.emit()
        except FileNotFoundError:
            return

    def _load_user_styles(self):
        """
        Loads all user styles
        """
        path = self.user_service_path() / 'user_styles.json'
        try:
            with open(path, 'rt', encoding='utf8') as f:
                try:
                    self._user_styles = json.load(f)
                except json.JSONDecodeError:
                    return

                self.user_styles_changed.emit()
        except FileNotFoundError:
            return

    def set_user_styles(self, styles: Dict[str, dict]):
        """
        Sets all users styles
        """
        self._user_styles = deepcopy(styles)
        self._save_user_styles()
        self.user_styles_changed.emit()

    def _save_user_styles(self):
        """
        Saves all user styles
        """
        path = self.user_service_path() / 'user_styles.json'
        with open(path, 'wt', encoding='utf8') as f:
            f.write(json.dumps(self._user_styles, indent=4))

    def add_user_style(self,
                       name: str,
                       service_type: str,
                       url: str):
        """
        Adds a new user style
        """
        if service_type == ServiceManager.MACROSEISMIC:
            style_type = 'macroseismic'
        elif service_type == ServiceManager.FDSNEVENT:
            style_type = 'events'
        else:
            style_type = 'stations'

        self._user_styles[name] = {
            "label": name,
            "type": style_type,
            "url": url
        }
        self._save_user_styles()
        self.user_styles_changed.emit()

    def remove_user_style(self, name: str) -> bool:
        """
        Removes an existing user defined style
        """
        if name not in self._user_styles:
            return False

        del self._user_styles[name]
        self._save_user_styles()
        self.user_styles_changed.emit()
        return True

    def get_style(self, name: str) -> Dict[str, str]:
        """
        Gets a style definition
        """
        if name in self.PRESET_STYLES:
            return self.PRESET_STYLES[name]

        return self._user_styles[name]

    def _save_predefined_areas(self):
        """
        Saves all predefined areas
        """
        areas_to_save = {k: v for k, v in self._predefined_bounding_boxes.items() if not v.get('read_only')}
        path = self.user_service_path() / 'predefined_areas.json'
        with open(path, 'wt', encoding='utf8') as f:
            f.write(json.dumps(areas_to_save, indent=4))

    def add_predefined_bounding_box(self, name: str, configuration: dict):
        """
        Adds a new predefined bounding box
        """
        self._predefined_bounding_boxes[name] = configuration
        self._save_predefined_areas()
        self.areasChanged.emit()

    def remove_predefined_bounding_box(self, name: str) -> bool:
        """
        Removes an existing predefined bounding box, or returns False if it cannot be removed
        """
        if name not in self._predefined_bounding_boxes:
            return False

        if self._predefined_bounding_boxes[name].get('read_only', False):
            return False

        del self._predefined_bounding_boxes[name]
        self._save_predefined_areas()
        self.areasChanged.emit()
        return True

    def custom_service_path(self, service_type: str, service_id: str) -> Path:
        """
        Returns the path to a custom service definition file
        """
        return (self.user_service_path() / service_type / service_id).with_suffix('.json')

    def remove_service(self, service_type: str, service_id: str):
        """
        Removes a service definition
        """
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.unlink()
            self.refresh_services()

    def rename_service(self, service_type: str, service_id: str, new_name: str):
        """
        Renames an existing service
        """
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.rename(self.custom_service_path(service_type, new_name))
            self.refresh_services()

    def export_service(self, service_type: str, service_id: str, path: str) -> bool:
        """
        Exports a service to a file
        """
        config = deepcopy(self.service_details(service_type, service_id))
        config['servicetype'] = service_type
        config['serviceid'] = service_id

        with open(path, 'wt', encoding='utf8') as f:
            f.write(json.dumps(config, indent=4))
        return True

    def import_service(self, path: str) -> Tuple[bool, str]:
        """
        Imports a service from a path
        Returns success flag and error message
        """
        service = self.create_from_file(path)
        if not service:
            return False, 'Error reading service definition'

        service['read_only'] = False

        if 'serviceid' in service:
            service_id = service['serviceid']
        else:
            service_id = Path(path).stem

        if 'servicetype' not in service:
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

    def save_service(self, service_type: str, service_id: str, configuration: dict):
        """
        Saves a service definition
        """
        path = self.custom_service_path(service_type, service_id)
        if path.exists():
            path.unlink()

        with open(path, 'wt', encoding='utf8') as f:
            f.write(json.dumps(configuration, indent=4))
        self.refresh_services()

    def get_field_config(self, service_type: str) -> dict:
        """
        Returns the field configuration dictionary for a specific service type
        """
        return self._CONFIG_FIELDS[service_type]

    def get_contributor_endpoint(self, service_type: str, service_id: str) -> Optional[str]:
        """
        Returns the get contributor endpoint URL for the specified service
        """
        default_endpoint = self.service_details(service_type, service_id)['endpointurl']
        if service_type == SERVICE_MANAGER.FDSNEVENT:
            return default_endpoint[:default_endpoint.index('event/1') + 7] + '/contributors'
        if service_type == SERVICE_MANAGER.MACROSEISMIC:
            return default_endpoint[:default_endpoint.index('/query')] + '/contributors'

        return None

    def get_contributors(self, service_type: str, service_id: str) -> List[str]:
        """
        Returns a list of previously retrieved contributors for the specified service and service ID
        """
        return self.contributors[service_type].get(service_id, [])

    def set_contributors(self, service_type: str, service_id: str, contributors: List[str]):
        """
        Sets a list of previously retrieved contributors for the specified service and service ID
        """
        self.contributors[service_type][service_id] = contributors

    def user_styles(self) -> List[str]:
        """
        Returns a list of the available user styles
        """
        return list(self._user_styles.keys())

    def styles_for_service_type(self, service_type: str) -> List[str]:
        """
        Returns a list of available styles for the specified service type
        """
        res = []
        for name, style in self.PRESET_STYLES.items():
            style_type = style.get('type')
            if not style_type:
                continue

            if service_type == ServiceManager.FDSNSTATION and style_type == "stations":
                res.append(name)
            elif service_type == ServiceManager.FDSNEVENT and style_type == "events":
                res.append(name)
            elif service_type == ServiceManager.MACROSEISMIC and style_type == "macroseismic":
                res.append(name)

        for name, style in self._user_styles.items():
            style_type = style.get('type')
            if not style_type:
                continue

            if service_type == ServiceManager.FDSNSTATION and style_type == "stations":
                res.append(name)
            elif service_type == ServiceManager.FDSNEVENT and style_type == "events":
                res.append(name)
            elif service_type == ServiceManager.MACROSEISMIC and style_type == "macroseismic":
                res.append(name)

        return res


SERVICE_MANAGER = ServiceManager()
