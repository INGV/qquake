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
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    NULL
)

from qquake.qquake_defs import (
    fdsn_events_capabilities,
    fdsn_event_fields,
    getFDSNEvent,
)


class CreationInfo():

    def __init__(self,
                 agencyID,
                 agencyURI,
                 author,
                 authorURI,
                 creationTime,
                 version):
        self.agencyID = agencyID
        self.agencyURI = agencyURI
        self.author = author
        self.authorURI = authorURI
        self.creationTime = creationTime
        self.version = version

    @staticmethod
    def from_element(element):
        agency_id = element.elementsByTagName('agencyID').at(0).toElement().text()
        author = element.elementsByTagName('author').at(0).toElement().text()
        version = element.elementsByTagName('version').at(0).toElement().text()
        author_uri = element.elementsByTagName('authorURI').at(0).toElement().text()
        agency_uri = element.elementsByTagName('agencyURI').at(0).toElement().text()
        creation_time = element.elementsByTagName('creationTime').at(0).toElement().text()

        return CreationInfo(agencyID=agency_id,
                            agencyURI=agency_uri,
                            author=author,
                            authorURI=author_uri,
                            creationTime=creation_time,
                            version=version)


class EventDescription:

    def __init__(self, text, type):
        self.text = text
        self.type = type

    @staticmethod
    def from_element(element):
        type = element.elementsByTagName('type').at(0).toElement().text()
        text = element.elementsByTagName('text').at(0).toElement().text()
        return EventDescription(text=text, type=type)


class Origin:

    def __init__(self,
                 publicID,
                 time,
                 longitude,
                 latitude,
                 depth,
                 depthType,
                 timeFixed,
                 epicenterFixed,
                 referenceSystemID,
                 methodID,
                 earthModeID,
                 compositeTime,
                 quality,
                 type,
                 region,
                 evaluationMode,
                 evaluationStatus,
                 comment,
                 creationInfo):
        self.publicID = publicID
        self.time = time
        self.longitude = longitude
        self.latitude = latitude
        self.depth = depth
        self.depthType = depthType
        self.timeFixed = timeFixed
        self.epicenterFixed = epicenterFixed
        self.referenceSystemID = referenceSystemID
        self.methodID = methodID
        self.earthModeID = earthModeID
        self.compositeTime = compositeTime
        self.quality = quality
        self.type = type
        self.region = region
        self.evaluationMode = evaluationMode
        self.evaluationStatus = evaluationStatus
        self.comment = comment
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        publicId = element.attribute('publicID')
        time = element.elementsByTagName('time').at(0).toElement().elementsByTagName('value').at(0).toElement().text()
        region = element.elementsByTagName('region').at(0).toElement().text()
        latitude = element.elementsByTagName('latitude').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        longitude = element.elementsByTagName('longitude').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        depth = element.elementsByTagName('depth').at(0).toElement().elementsByTagName('value').at(
            0).toElement().text()
        evaluationMode = element.elementsByTagName('evaluationMode').at(0).toElement().text()
        evaluationStatus = element.elementsByTagName('evaluationStatus').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

        return Origin(publicID=publicId,
                      time=time,
                      longitude=longitude,
                      latitude=latitude,
                      depth=depth,
                      depthType=None,
                      timeFixed=None,
                      epicenterFixed=None,
                      referenceSystemID=None,
                      methodID=None,
                      earthModeID=None,
                      compositeTime=None,
                      quality=None,
                      type=None,
                      region=region,
                      evaluationMode=evaluationMode,
                      evaluationStatus=evaluationStatus,
                      comment=None,
                      creationInfo=creation_info)


class RealQuantity:

    def __init__(self,
                 value,
                 uncertainty,
                 lowerUncertainty,
                 upperUncertainty,
                 confidenceLevel):
        self.value = value
        self.uncertainty = uncertainty
        self.lowerUncertainty = lowerUncertainty
        self.upperUncertainty = upperUncertainty
        self.confidenceLevel = confidenceLevel

    @staticmethod
    def from_element(element):
        value = element.elementsByTagName('value').at(0).toElement().text()
        uncertainty = element.elementsByTagName('uncertainty').at(
            0).toElement().text() if not element.elementsByTagName('uncertainty').at(0).toElement().isNull() else None
        lowerUncertainty = element.elementsByTagName('lowerUncertainty').at(
            0).toElement().text() if not element.elementsByTagName('lowerUncertainty').at(
            0).toElement().isNull() else None
        upperUncertainty = element.elementsByTagName('upperUncertainty').at(
            0).toElement().text() if not element.elementsByTagName('upperUncertainty').at(
            0).toElement().isNull() else None
        confidenceLevel = element.elementsByTagName('confidenceLevel').at(
            0).toElement().text() if not element.elementsByTagName('confidenceLevel').at(
            0).toElement().isNull() else None

        return RealQuantity(value=value,
                            uncertainty=uncertainty,
                            lowerUncertainty=lowerUncertainty,
                            upperUncertainty=upperUncertainty,
                            confidenceLevel=confidenceLevel)


class Magnitude:

    def __init__(self,
                 publicID,
                 mag,
                 type,
                 originID,
                 methodID,
                 stationCount,
                 azimuthalGap,
                 evalutionMode,
                 evaluationStatus,
                 comment,
                 creationInfo):
        self.publicID = publicID
        self.mag = mag
        self.originID = originID
        self.methodID = methodID
        self.azimuthalGap = azimuthalGap
        self.stationCount = stationCount
        self.stationCount = stationCount
        self.evalutionMode = evalutionMode
        self.type = type
        self.evaluationStatus = evaluationStatus
        self.comment = comment
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element):
        publicId = element.attribute('publicID')
        type = element.elementsByTagName('type').at(0).toElement().text()
        originID = element.elementsByTagName('originID').at(0).toElement().text()
        mag = Magnitude.from_element(
            element.elementsByTagName('mag').at(0).toElement()) if not element.elementsByTagName('mag').at(
            0).toElement().isNull() else None
        evaluationMode = element.elementsByTagName('evaluationMode').at(0).toElement().text()
        evaluationStatus = element.elementsByTagName('evaluationStatus').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

        return Magnitude(publicID=publicId,
                         mag=mag,
                         type=type,
                         originID=originID,
                         methodID=None,
                         stationCount=None,
                         azimuthalGap=None,
                         evalutionMode=evaluationMode,
                         evaluationStatus=evaluationStatus,
                         comment=None,
                         creationInfo=creation_info)


class Event:

    def __init__(self, publicID,
                 type,
                 typeCertainty,
                 description,
                 preferredOriginID,
                 preferredMagnitudeID,
                 preferredFocalMechanismID,
                 comment,
                 creationInfo,
                 origins,
                 magnitudes):
        self.publicID = publicID
        self.type = type
        self.typeCertainty = typeCertainty
        self.description = description
        self.preferredOriginID = preferredOriginID
        self.preferredMagnitudeID = preferredMagnitudeID
        self.preferredFocalMechanismID = preferredFocalMechanismID
        self.comment = comment
        self.creationInfo = creationInfo
        self.origins = origins
        self.magnitudes = magnitudes

    def to_features(self):
        fields = QgsFields()
        for k, v in fdsn_event_fields.items():
            fields.append(QgsField(k, v))

        features = []
        for o in self.origins:
            f = QgsFeature(fields)
            f['EventID'] = self.publicID
            f['Time'] = o.time
            f['Latitude'] = o.latitude
            f['Longitude'] = o.longitude
            f['DepthKm'] = o.depth
            f['Author'] = o.creationInfo.author if o.creationInfo else NULL
            f['Catalog'] = NULL #?
            f['Contributor'] = NULL #?
            f['ContributorID'] = NULL #?
            f['MagType'] = NULL #?
            f['Magnitude'] = NULL #?
            f['MagAuthor'] = NULL #?
            f['EventLocationName'] = o.region #?

            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(o.longitude), float(o.latitude))))
            features.append(f)

        return features

    @staticmethod
    def from_element(element):
        publicId = element.attribute('publicID')
        type = element.elementsByTagName('type').at(0).toElement().text()
        typeCertainty = element.elementsByTagName('typeCertainty').at(0).toElement().text()
        creation_info = CreationInfo.from_element(element.elementsByTagName('creationInfo').at(0).toElement())

        description_nodes = element.elementsByTagName('description')
        descriptions = []
        for e in range(description_nodes.length()):
            descriptions.append(EventDescription.from_element(description_nodes.at(e).toElement()))

        origin_nodes = element.elementsByTagName('origin')
        origins = []
        for e in range(origin_nodes.length()):
            origins.append(Origin.from_element(origin_nodes.at(e).toElement()))

        magnitude_nodes = element.elementsByTagName('magnitude')
        magnitudes = []
        for e in range(magnitude_nodes.length()):
            magnitudes.append(Magnitude.from_element(magnitude_nodes.at(e).toElement()))

        return Event(publicID=publicId,
                     type=type,
                     typeCertainty=typeCertainty,
                     description=descriptions,
                     preferredOriginID=None,
                     preferredMagnitudeID=None,
                     preferredFocalMechanismID=None,
                     comment=None,
                     creationInfo=creation_info,
                     origins=origins,
                     magnitudes=magnitudes)


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
        self.result = self.parse_reply(reply)
        self.finished.emit()

    @staticmethod
    def parse_reply(reply):
        doc = QDomDocument()
        doc.setContent(reply.readAll())
        event_elements = doc.elementsByTagName('event')

        events = []
        for e in range(event_elements.length()):
            event_element = event_elements.at(e).toElement()
            events.append(Event.from_element(event_element))

        return events

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

