# -*- coding: utf-8 -*-
"""QQuake- Data Fetcher

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2020 by Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Copyright 2020, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (
    Qt,
    QUrl,
    QObject,
    pyqtSignal
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsNetworkAccessManager,
    QgsVectorLayer,
    QgsFields,
    QgsField
)

from qquake.quakeml_parser import QuakeMlParser
from qquake.qquake_defs import (
    fdsn_events_capabilities,
    fdsn_event_fields
)


class Fetcher(QObject):
    """
    Fetcher for feeds
    """

    progress = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, event_service,
                 event_start_date=None,
                 event_end_date=None,
                 event_min_magnitude=None,
                 event_max_magnitude=None,
                 extent=None,
                 limit=1000,
                 parent=None
                 ):
        super().__init__(parent=parent)

        self.event_service = event_service
        self.event_start_date = event_start_date
        self.event_end_date = event_end_date
        self.event_min_magnitude = event_min_magnitude
        self.event_max_magnitude = event_max_magnitude
        self.extent = extent
        self.limit = limit

        self.result = None

    def generate_url(self, format='text'):
        """
        Returns the URL request for the query
        """
        service = fdsn_events_capabilities[self.event_service]['ws']

        query = []
        # append to the string the parameter of the UI (starttime, endtime, etc)
        if self.event_start_date is not None and self.event_start_date.isValid():
            query.append('starttime={}'.format(self.event_start_date.toString(Qt.ISODate)))

        if self.event_end_date is not None and self.event_end_date.isValid():
            query.append('endtime={}'.format(self.event_end_date.toString(Qt.ISODate)))

        if self.event_min_magnitude is not None:
            query.append('minmag={}'.format(self.event_min_magnitude))

        if self.event_max_magnitude is not None:
            query.append('maxmag={}'.format(self.event_max_magnitude))

        if self.extent is not None:
            query.append('minlat={ymin}&maxlat={ymax}&minlon={xmin}&maxlon={xmax}'.format(
                ymin=self.extent.yMinimum(),
                ymax=self.extent.yMaximum(),
                xmin=self.extent.xMinimum(),
                xmax=self.extent.xMaximum()
            ))

        if self.limit:
            query.append('limit={}'.format(self.limit))

        query.append('format={}'.format(format))

        return service + '&'.join(query)

    def fetch_data(self):
        """
        Starts the fetch request
        """
        request = QNetworkRequest(QUrl(self.generate_url(format='xml')))
        self.result = None

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def _reply_progress(self, received, total):
        if total > 0:
            self.progress.emit(float(received) / total * 100)

    def _reply_finished(self, reply):
        self.result = QuakeMlParser.parse(reply.readAll())
        self.finished.emit()

    def _generate_layer_name(self):
        name = self.event_service

        if self.event_min_magnitude is not None and self.event_max_magnitude is not None:
            name += ' ({} ≤ Magnitude ≤ {})'.format(self.event_min_magnitude, self.event_max_magnitude)
        elif self.event_min_magnitude is not None:
            name += ' ({} ≤ Magnitude)'.format(self.event_min_magnitude)
        elif self.event_max_magnitude is not None:
            name += ' (Magnitude ≤ {})'.format(self.event_max_magnitude)

        return name

    def _create_empty_layer(self):
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('Point?crs=EPSG:4326', self._generate_layer_name(), 'memory')

        fields = QgsFields()
        for k, v in fdsn_event_fields.items():
            fields.append(QgsField(k, v))
        vl.dataProvider().addAttributes(fields)
        vl.updateFields()

        return vl

    def events_to_layer(self, events):
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_layer()

        features = []
        for e in events:
            features.extend(e.to_features())

        vl.dataProvider().addFeatures(features)

        return vl

    def create_layer(self):
        return self.events_to_layer(self.result)

