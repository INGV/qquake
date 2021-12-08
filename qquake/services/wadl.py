# -*- coding: utf-8 -*-
"""
WADL to service configuration parser
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

from typing import Dict

from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtXml import QDomDocument

from .service_manager import ServiceManager


class WadlServiceParser:
    """
    WADL to service configuration parser
    """

    @staticmethod
    def find_url(url: str) -> str:
        """
        Tries to find a application url from a general url
        """
        if url.endswith('wadl'):
            return url

        if url.endswith('?'):
            url = url[:-1]

        last_part = url.rindex('/')
        strip_last_path = url[:last_part]
        return strip_last_path + '/application.wadl'

    PARAM_MAP = {
        'eventid': 'queryeventid',
        'mindepth': 'querydepth',
        'maxdepth': 'querydepth',
        'includeallorigins': 'queryincludeallorigins',
        'includeallmagnitudes': 'queryincludeallmagnitudes',
        'originid': 'queryoriginid',
        'magnitudeid': 'querymagnitudeid',
        'updatedafter': 'queryupdatedafter',
        'catalog': 'querycatalog',
        'contributorid': 'querycontributorid',
        'eventtype': 'queryeventtype',
        'includearrivals': 'queryincludearrivals',
        'minradius': 'querycircular',
        'maxradius': 'querycircular',
        'minradiuskm': 'querycircularradiuskm',
        'maxradiuskm': 'querycircularradiuskm',
        'text': 'outputtext',
        'json': 'outputjson',
        'geojson': 'outputgeojson',
        'kml': 'outputkml'
    }

    @staticmethod
    def parse_wadl(content: QByteArray,  # pylint:disable=too-many-locals,too-many-branches,too-many-statements
                   service_type: str,
                   wadl_url: str) -> Dict:
        """
        Parses a WADL document and converts to a service configuration
        """
        doc = QDomDocument()
        doc.setContent(content)
        resources_elements = doc.elementsByTagName('resources')
        assert resources_elements.length() == 1

        resources_element = resources_elements.at(0).toElement()

        query_element = None
        request_element = None
        resource_elements = resources_element.elementsByTagName('resource')
        for e in range(resource_elements.length()):
            resource_element = resource_elements.at(e).toElement()

            method_element = resource_element.firstChildElement('method').toElement()
            if method_element.isNull():
                continue

            request_element = method_element.firstChildElement('request').toElement()
            if request_element.isNull():
                continue

            query_element = resource_element
            break

        assert query_element
        assert not request_element.isNull()

        param_elements = request_element.elementsByTagName('param')
        min_latitude = None
        max_latitude = None
        min_longitude = None
        max_longitude = None

        settings = {}
        if service_type != ServiceManager.FDSNSTATION:
            settings = {v: False for _, v in WadlServiceParser.PARAM_MAP.items()}

        for e in range(param_elements.length()):
            param_element = param_elements.at(e).toElement()

            param_name = param_element.attribute('name')
            if param_name in WadlServiceParser.PARAM_MAP:
                mapped_name = WadlServiceParser.PARAM_MAP[param_name]
                if mapped_name in settings:
                    settings[mapped_name] = True
                continue

            if param_name == 'minlatitude':
                min_latitude = float(param_element.attribute('default', '-180'))
            elif param_name == 'maxlatitude':
                max_latitude = float(param_element.attribute('default', '180'))
            elif param_name == 'minlongitude':
                min_longitude = float(param_element.attribute('default', '-90'))
            elif param_name == 'maxlongitude':
                max_longitude = float(param_element.attribute('default', '90'))
            elif param_name == 'format':
                option_elements = param_element.elementsByTagName('option')
                for o in range(option_elements.length()):
                    option_element = option_elements.at(o).toElement()
                    option_name = option_element.attribute('value')
                    if option_name in WadlServiceParser.PARAM_MAP:
                        mapped_name = WadlServiceParser.PARAM_MAP[option_name]
                        if mapped_name in settings:
                            settings[mapped_name] = True
                        continue

        endpoint = resources_element.attribute('base')
        if not endpoint.endswith('/'):
            endpoint += '/'

        if endpoint.startswith('/'):
            base_url = wadl_url[:wadl_url.index('/', wadl_url.index(':') + 3)]
            endpoint = base_url + endpoint

        resource_path = resource_element.attribute('path') + "?"
        if resource_path.startswith('/'):
            resource_path = resource_path[1:]
        endpoint += resource_path

        return {
            "endpointurl": endpoint,
            "boundingbox": [
                min_longitude if min_longitude is not None else -180,
                min_latitude if min_latitude is not None else -90,
                max_longitude if max_longitude is not None else 180,
                max_latitude if max_latitude is not None else 90
            ],
            "settings": settings
        }
