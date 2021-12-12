# -*- coding: utf-8 -*-
"""
A widget for display of metadata relating to a service
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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsStringUtils

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('service_information_widget.ui'))


class ServiceInformationWidget(QWidget, FORM_CLASS):
    """
    A widget for display of metadata relating to a service
    """

    def __init__(self, iface, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.info_browser.viewport().setAutoFillBackground(False)

        self.layer_model = None
        self.service_type = None
        self.service_id = None
        self.service_config = None

    def set_service(self, service_id: str, service_type: str):  # pylint: disable=too-many-statements
        """
        Sets the associated service
        """
        self.service_type = service_type
        self.service_id = service_id
        self.service_config = SERVICE_MANAGER.service_details(service_type, service_id)

        html = f"""<p><b>Title</b><br>
        {self.service_config['title']}</p>"""

        if self.service_config.get('datadescription') or self.service_config.get('datadescriptionurl'):
            html += f"""<p><b>Data description</b><br>
                <a href="{self.service_config['datadescriptionurl']}">{self.service_config.get('datadescription') or self.service_config['datadescriptionurl']}</a></p>
                """

        if self.service_config.get('datalicenseurl') or self.service_config.get('datalicense'):
            html += f"""<p><b>Data license</b><br>
                <a href="{self.service_config['datalicenseurl']}">{self.service_config.get('datalicense') or self.service_config.get('datalicenseurl')}</a></p>
                """

        if self.service_config.get('publications'):
            html += """<p><b>Publications</b></p><ul>"""
            for p in self.service_config['publications']:
                html += f"""<li style="margin-bottom:10px;">{QgsStringUtils.insertLinks(p)[0]}</li>"""
            html += "</ul>"

        if self.service_config.get('servicedescriptionurl') or self.service_config.get('servicedescription'):
            html += f"""<p><b>Service description</b><br>
            <a href="{self.service_config['servicedescriptionurl']}">{self.service_config.get('servicedescription') or self.service_config['servicedescriptionurl']}</a></p>"""

        html += """<p><b>Service managed by</b><br>
            <a href="{dataproviderurl}">{dataprovider}</a></p>
            """.format(**self.service_config)

        if self.service_config.get('help'):
            html += """
            <p><b>Help</b><br>
            <a href="{help}">{help}</a></p>
            """.format(**self.service_config)

        capabilities = []

        if service_type in (SERVICE_MANAGER.MACROSEISMIC, SERVICE_MANAGER.FDSNSTATION, SERVICE_MANAGER.FDSNEVENT):
            if self.service_config['settings'].get('querylimitmaxentries'):
                capabilities.append('Allowed maximum number of returned entries: {}'.format(
                    self.service_config['settings'].get('querylimitmaxentries')))
            if self.service_config.get('datestart'):
                capabilities.append(
                    'Earliest date: {}'.format(self.service_config['datestart']))
            if self.service_config.get('dateend'):
                capabilities.append(
                    'Latest date: {}'.format(self.service_config['dateend']))

            def add_capability_string(title, source, key):
                capabilities.append(
                    '{}: {}'.format(title,
                                    'YES' if source.get(key) else 'NO'))

            add_capability_string('Support requests using event identifier', self.service_config['settings'],
                                  'queryeventid')
            add_capability_string(
                'Support requests using origin identifier', self.service_config['settings'], 'queryoriginid')
            add_capability_string(
                'Support requests using magnitude identifier', self.service_config['settings'], 'querymagnitudeid')
            add_capability_string(
                'Support requests using forcal mechanism identifier', self.service_config['settings'],
                'queryfocalmechanismid')
            add_capability_string(
                'Support requests of data published after a certain date', self.service_config['settings'],
                'queryupdatedafter')
            add_capability_string(
                'Support requests using source catalog identifier', self.service_config['settings'], 'querycatalog')
            add_capability_string(
                'Support requests using source contributor identifier', self.service_config['settings'],
                'querycontributorid')
            add_capability_string(
                'Support requests by event type', self.service_config['settings'], 'queryeventtype')
            add_capability_string(
                'Support requests by magnitude type', self.service_config['settings'], 'querymagnitudetype')
            add_capability_string(
                'Support retrieval of all origin estimates', self.service_config['settings'], 'queryincludeallorigins')
            add_capability_string(
                'Support retrieval of all magnitude estimates', self.service_config['settings'],
                'queryincludeallmagnitudes')
            add_capability_string(
                'Support retrieval of arrival times', self.service_config['settings'], 'queryincludearrivals')
            add_capability_string(
                'Support retrieval of all station magnitude estimates', self.service_config['settings'],
                'queryincludeallstationsmagnitudes')
            add_capability_string(
                'Support query limit', self.service_config['settings'], 'querylimit')
            add_capability_string(
                'Support filter using circular search', self.service_config['settings'], 'querycircular')
            add_capability_string(
                'Support search radius in kilometers', self.service_config['settings'], 'querycircularradiuskm')
            add_capability_string(
                'Support filter by hypocentral depth', self.service_config['settings'], 'querydepth')
            add_capability_string(
                'Support text output', self.service_config['settings'], 'outputtext')
            add_capability_string(
                'Support QuakeML output', self.service_config['settings'], 'outputxml')
            add_capability_string(
                'Support GeoJSON output', self.service_config['settings'], 'outputgeojson')
            add_capability_string(
                'Support JSON output', self.service_config['settings'], 'outputjson')
            add_capability_string(
                'Support KML output', self.service_config['settings'], 'outputkml')
            add_capability_string(
                'Support XLSX output', self.service_config['settings'], 'outputxlsx')

            if self.service_config.get('httpcodenodata'):
                capabilities.append(
                    'HTTP error code: {}'.format(self.service_config['settings'].get('httpcodenodata')))

        if capabilities:
            html += """<p><b>Service capabilities</b>"""
            html += ''.join(['<li>{}</li>'.format(c) for c in capabilities])
            html += """</p>"""

        self.info_browser.setHtml(html)
