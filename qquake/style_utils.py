# -*- coding: utf-8 -*-
"""
Style utils
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

from typing import Optional

from qgis.PyQt.QtCore import (
    QDir,
    QUrl,
    QTemporaryFile
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    QgsVectorLayer,
    QgsMapLayer,
    QgsBlockingNetworkRequest,
    QgsGraduatedSymbolRenderer,
    QgsCategorizedSymbolRenderer
)

from qquake.services import SERVICE_MANAGER


class StyleUtils:
    """
    Layer styling utilities
    """

    @staticmethod
    def style_url(style_name: str) -> str:
        """
        Returns the URL for the matching style
        """
        return SERVICE_MANAGER.get_style(style_name)['url']

    @staticmethod
    def default_style_for_events_url() -> str:
        """
        Returns the URL for the default style to use for event layers
        """
        for _, v in SERVICE_MANAGER.PRESET_STYLES.items():
            if v['type'] == 'events':
                return v['url']

        assert False

    @staticmethod
    def default_style_for_macro_url() -> str:
        """
        Returns the URL for the default style to use for macro layers
        """
        for _, v in SERVICE_MANAGER.PRESET_STYLES.items():
            if v['type'] == 'macroseismic':
                return v['url']

        assert False

    @staticmethod
    def fetch_and_apply_style(layer: QgsMapLayer, url: str, style_attr: str = '') -> Optional[str]:
        """
        Fetches a QML style from the specified URL, and applies it to a layer.
        @param layer: target layer to apply style to
        @param url: URL for QML content
        @param style_attr: optional str specifying name of existing field in layer to automatically
        update classified references to
        @return: Returns a str if an error occurred, or None if the fetch and apply was successful
        """
        request = QgsBlockingNetworkRequest()
        if request.get(QNetworkRequest(QUrl(url))) != QgsBlockingNetworkRequest.NoError:
            return 'Error while fetching QML style: {}'.format(request.errorMessage())

        reply = request.reply().content()
        tmp_file = QTemporaryFile('{}/XXXXXX.qml'.format(QDir.tempPath()))
        tmp_file.open()
        tmp_file_name = tmp_file.fileName()
        tmp_file.close()
        with open(tmp_file_name, 'wt', encoding='utf8') as f:
            f.write(reply.data().decode())

        layer.loadNamedStyle(tmp_file_name)

        if style_attr:
            StyleUtils.update_class_attribute(layer, style_attr)

        layer.triggerRepaint()
        return None

    @staticmethod
    def update_class_attribute(layer: QgsVectorLayer, style_attr: str):
        """
        Updates a vector layer's renderer to apply a new attribute for classification.
        Useful when the attribute name in a predefined style (e.g. QML file) doesn't match
        the actual attribute name in a layer.

        @param layer: Layer with renderer to update
        @param style_attr: Actual name of field to use for classification
        """
        if isinstance(layer.renderer(), QgsGraduatedSymbolRenderer):
            layer.renderer().setClassAttribute(style_attr)
        elif isinstance(layer.renderer(), QgsCategorizedSymbolRenderer):
            layer.renderer().setClassAttribute(style_attr)
