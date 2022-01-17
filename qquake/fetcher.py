# -*- coding: utf-8 -*-
"""
Fetcher for feeds
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

import re
from pathlib import Path
from typing import List, Tuple, Dict
from typing import Union, Optional

from qgis.PyQt.QtCore import (
    Qt,
    QUrl,
    QObject,
    pyqtSignal,
    QDateTime,
    QCoreApplication
)
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import (
    Qgis,
    QgsNetworkAccessManager,
    QgsVectorLayer,
    QgsSettings,
    QgsUnitTypes,
)

from qquake.basic_text import (
    BasicTextParser,
    BasicStationParser
)

from qquake.quakeml import (
    QuakeMlParser,
    MissingOriginException
)
from qquake.quakeml.fdsn_station import (
    FDSNStationXMLParser,
    Station,
    Fdsn
)
from qquake.services import SERVICE_MANAGER
from qquake.style_utils import StyleUtils


class Fetcher(QObject):
    """
    Fetcher for feeds
    """

    BASIC = 'BASIC'
    EXTENDED = 'EXTENDED'

    SPLIT_STRATEGY_YEAR = 'SPLIT_STRATEGY_YEAR'
    SPLIT_STRATEGY_MONTH = 'SPLIT_STRATEGY_MONTH'
    SPLIT_STRATEGY_DAY = 'SPLIT_STRATEGY_DAY'

    STRATEGIES = {
        QCoreApplication.translate('QQuake', 'Split by Years'): SPLIT_STRATEGY_YEAR,
        QCoreApplication.translate('QQuake', 'Split by Months'): SPLIT_STRATEGY_MONTH,
        QCoreApplication.translate('QQuake', 'Split by Days'): SPLIT_STRATEGY_DAY,
    }

    started = pyqtSignal()
    progress = pyqtSignal(float)
    finished = pyqtSignal(bool)
    message = pyqtSignal(str, Qgis.MessageLevel)

    def __init__(self,  # pylint: disable=too-many-locals,too-many-statements
                 service_type,
                 event_service,
                 event_start_date=None,
                 event_end_date=None,
                 event_min_magnitude=None,
                 event_max_magnitude=None,
                 limit_extent_rect=False,
                 min_latitude=None,
                 max_latitude=None,
                 min_longitude=None,
                 max_longitude=None,
                 limit_extent_circle=False,
                 circle_latitude=None,
                 circle_longitude=None,
                 circle_min_radius=None,
                 circle_max_radius=None,
                 circle_radius_unit=QgsUnitTypes.DistanceDegrees,
                 earthquake_number_mdps_greater=None,
                 earthquake_max_intensity_greater=None,
                 event_ids=None,
                 contributor_id=None,
                 network_codes=None,
                 station_codes=None,
                 locations=None,
                 parent=None,
                 output_fields=None,
                 output_type=EXTENDED,
                 convert_negative_depths=False,
                 depth_unit=QgsUnitTypes.DistanceMeters,
                 event_type: Optional[str] = None,
                 updated_after: Optional[QDateTime] = None,
                 split_strategy: Optional[str] = None,
                 styles: Dict[str, str] = None,
                 url=None
                 ):
        super().__init__(parent=parent)

        self.service_type = service_type
        self.service_id = event_service
        self.service_config = SERVICE_MANAGER.service_details(self.service_type, self.service_id)

        self.split_strategy = split_strategy
        self.exceeded_limit = False

        self.event_start_date = event_start_date
        self.event_end_date = event_end_date

        # if we have a split strategy set, we HAVE to have a full date range available
        if self.split_strategy is not None and self.event_start_date is None:
            self.event_start_date = QDateTime.fromString(self.service_config.get('datestart'), Qt.ISODate)
        if self.split_strategy is not None and self.event_end_date is None:
            self.event_end_date = QDateTime.fromString(self.service_config.get('dateend'),
                                                       Qt.ISODate) if self.service_config.get(
                'dateend') else QDateTime.currentDateTime()

        self.event_start_date_limit = self.event_start_date
        self.event_end_date_limit = self.event_end_date

        if self.split_strategy is not None:
            self.ranges = Fetcher.split_range_by_strategy(self.split_strategy, self.event_start_date,
                                                          self.event_end_date)
            self.event_start_date, self.event_end_date = self.ranges[0]
            del self.ranges[0]
        else:
            self.ranges = None

        self.event_min_magnitude = event_min_magnitude
        self.event_max_magnitude = event_max_magnitude
        self.event_type = event_type
        self.limit_extent_rect = limit_extent_rect
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude
        self.limit_extent_circle = limit_extent_circle
        self.circle_latitude = circle_latitude
        self.circle_longitude = circle_longitude
        self.circle_min_radius = circle_min_radius
        self.circle_max_radius = circle_max_radius
        self.circle_radius_unit = circle_radius_unit
        self.earthquake_number_mdps_greater = earthquake_number_mdps_greater
        self.earthquake_max_intensity_greater = earthquake_max_intensity_greater
        self.event_ids = event_ids
        self.contributor_id = contributor_id
        self.network_codes = network_codes
        self.station_codes = station_codes
        self.locations = locations
        self.pending_event_ids = event_ids
        self.macro_pending_event_ids = event_ids
        self.output_type = output_type
        self.convert_negative_depths = convert_negative_depths
        self.depth_unit = depth_unit
        self.updated_after = updated_after
        self.url = url

        s = QgsSettings()
        self.preferred_origins_only = s.value('/plugins/qquake/output_preferred_origins', True, bool) or not \
            self.service_config['settings'].get('queryincludeallorigins', False)
        self.preferred_magnitudes_only = s.value('/plugins/qquake/output_preferred_magnitude', True, bool) or not \
            self.service_config['settings'].get('queryincludeallmagnitudes', False)
        self.preferred_mdp_only = s.value('/plugins/qquake/output_preferred_mdp', True, bool)

        self.output_fields = output_fields[:] if output_fields else []

        if self.output_type == self.EXTENDED:
            if not self.preferred_origins_only and "!IsPrefOrigin" not in self.output_fields:
                self.output_fields.append("!IsPrefOrigin")
            if not self.preferred_magnitudes_only and "!IsPrefMag" not in self.output_fields:
                self.output_fields.append("!IsPrefMag")
            if not self.preferred_mdp_only and "!IsPrefMdpset" not in self.output_fields:
                self.output_fields.append("!IsPrefMdpset")

            self.result = QuakeMlParser(convert_negative_depths=self.convert_negative_depths,
                                        depth_unit=self.depth_unit)
        else:
            self.result = BasicTextParser(convert_negative_depths=self.convert_negative_depths,
                                          depth_unit=self.depth_unit)

        self.missing_origins = set()
        self.is_missing_origin_request = False
        self.require_mdp_basic_text_request = self.output_type == self.BASIC and self.service_type == SERVICE_MANAGER.MACROSEISMIC
        self.is_mdp_basic_text_request = False
        self.is_first_request = True
        self.query_limit = None
        self.styles = styles

    def suggest_split_strategy(self) -> str:
        """
        Suggests a split strategy based on the fetchers' date range
        """
        start_date = self.event_start_date if self.event_start_date is not None else QDateTime.fromString(
            self.service_config.get('datestart'), Qt.ISODate)
        end_date = self.event_end_date if self.event_end_date is not None else (
            QDateTime.fromString(self.service_config.get('dateend'), Qt.ISODate) if self.service_config.get(
                'dateend') else QDateTime.currentDateTime()
        )

        days_between = start_date.daysTo(end_date)

        if days_between > 5 * 365:
            res = Fetcher.SPLIT_STRATEGY_YEAR
        elif days_between > 30:
            res = Fetcher.SPLIT_STRATEGY_MONTH
        else:
            res = Fetcher.SPLIT_STRATEGY_DAY
        return res

    @staticmethod
    def split_range_by_strategy(strategy: str, begin: QDateTime, end: QDateTime) -> List[Tuple[QDateTime, QDateTime]]:
        """
        Splits a date range by the specified strategy
        """
        res = []
        current = begin
        while current < end:

            if strategy == Fetcher.SPLIT_STRATEGY_YEAR:
                part_end = current.addYears(1)
            elif strategy == Fetcher.SPLIT_STRATEGY_MONTH:
                part_end = current.addMonths(1)
            elif strategy == Fetcher.SPLIT_STRATEGY_DAY:
                part_end = current.addDays(1)
            else:
                assert False

            res.append((current, part_end))
            current = part_end.addSecs(1)

        return res

    def generate_url(self):  # pylint: disable=too-many-statements,too-many-branches
        """
        Returns the URL request for the query
        """
        if self.url is not None:
            return self.url

        if self.is_mdp_basic_text_request:
            result_format = 'textmacro'
        else:
            result_format = 'text' if self.output_type == Fetcher.BASIC else 'xml'

        query = []
        # append to the string the parameter of the UI (starttime, endtime, etc)
        if self.event_start_date is not None and self.event_start_date.isValid():
            query.append('starttime={}'.format(self.event_start_date.toString(Qt.ISODate)))

        if self.event_end_date is not None and self.event_end_date.isValid():
            query.append('endtime={}'.format(self.event_end_date.toString(Qt.ISODate)))

        if self.updated_after is not None and self.updated_after.isValid():
            query.append('updatedafter={}'.format(self.updated_after.toString(Qt.ISODate)))

        if self.event_min_magnitude is not None:
            query.append('minmag={}'.format(self.event_min_magnitude))

        if self.event_max_magnitude is not None:
            query.append('maxmag={}'.format(self.event_max_magnitude))

        if self.event_type is not None:
            query.append('eventtype={}'.format(self.event_type))

        if self.limit_extent_rect:
            if self.min_latitude is not None:
                query.append('minlatitude={}'.format(self.min_latitude))
            if self.max_latitude is not None:
                query.append('maxlatitude={}'.format(self.max_latitude))
            if self.min_longitude is not None:
                query.append('minlongitude={}'.format(self.min_longitude))
            if self.max_longitude is not None:
                query.append('maxlongitude={}'.format(self.max_longitude))
        elif self.limit_extent_circle and self.circle_latitude is not None and self.circle_longitude is not None and \
                (self.circle_min_radius is not None or self.circle_max_radius is not None):
            query.append('latitude={}'.format(self.circle_latitude))
            query.append('longitude={}'.format(self.circle_longitude))
            if self.circle_radius_unit == QgsUnitTypes.DistanceDegrees:
                if self.circle_min_radius is not None:
                    query.append('minradius={}'.format(self.circle_min_radius))
                if self.circle_max_radius is not None:
                    query.append('maxradius={}'.format(self.circle_max_radius))
            elif self.circle_radius_unit == QgsUnitTypes.DistanceKilometers:
                if self.circle_min_radius is not None:
                    query.append('minradiuskm={}'.format(self.circle_min_radius))
                if self.circle_max_radius is not None:
                    query.append('maxradiuskm={}'.format(self.circle_max_radius))

        if self.earthquake_number_mdps_greater is not None:
            query.append('minmdps={}'.format(
                self.earthquake_number_mdps_greater))

        if self.earthquake_max_intensity_greater is not None:
            query.append('minintensity={}'.format(
                self.earthquake_max_intensity_greater))

        if not self.event_ids and 'querylimitmaxentries' in self.service_config['settings']:
            self.query_limit = self.service_config['settings']['querylimitmaxentries']
            query.append('limit={}'.format(self.query_limit))

        if self.pending_event_ids:
            query.append('eventid={}'.format(self.pending_event_ids[0]))

        if self.station_codes:
            query.append('station={}'.format(self.station_codes))

        if self.network_codes:
            query.append('network={}'.format(self.network_codes))

        if self.locations:
            query.append('location={}'.format(self.locations))

        if self.contributor_id:
            query.append('contributor={}'.format(self.contributor_id))

        if self.output_type == Fetcher.EXTENDED:
            if not self.preferred_origins_only:
                if self.pending_event_ids or self.service_config['settings'].get('queryincludeallorigins_multiple',
                                                                                 False):
                    query.append('includeallorigins=true')
            if not self.preferred_magnitudes_only:
                if self.pending_event_ids or self.service_config['settings'].get('queryincludeallmagnitudes_multiple',
                                                                                 False):
                    query.append('includeallmagnitudes=true')

        if self.service_type == SERVICE_MANAGER.MACROSEISMIC:
            query.append('includemdps=true')

        query.append('format={}'.format(result_format))

        return self.service_config['endpointurl'] + '&'.join(query)

    def fetch_data(self):
        """
        Starts the fetch request
        """
        if self.is_first_request:
            self.started.emit()
            self.is_first_request = False

        request = QNetworkRequest(QUrl(self.generate_url()))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def fetch_missing(self):
        """
        Fetches missing results
        """
        # pop first missing origin from front of queue and fetch it
        self.message.emit(
            self.tr('Returned XML was incomplete. {} missing origins left to fetch').format(len(self.missing_origins)),
            Qgis.Warning)

        remaining = list(self.missing_origins)
        next_origin = remaining[0]
        self.missing_origins = set(remaining[1:])

        # change smi: prefix to http://
        parts = next_origin.split(":")
        next_origin = 'http://' + ':'.join(parts[1:])

        self.is_missing_origin_request = True

        request = QNetworkRequest(QUrl(next_origin))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)

        reply = QgsNetworkAccessManager.instance().get(request)

        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def fetch_next_event_by_id(self):
        """
        Fetches next event by ID
        """
        # pop first id from front of queue and fetch it
        self.message.emit(self.tr('{} events left to fetch').format(len(self.pending_event_ids)), Qgis.Info)
        self.fetch_data()

    def fetch_basic_mdp(self):
        """
        Fetches basic MDP
        """
        self.require_mdp_basic_text_request = False
        self.is_mdp_basic_text_request = True
        self.message.emit(self.tr('Fetching MDPs'), Qgis.Info)

        self.pending_event_ids = self.macro_pending_event_ids[:1]
        self.macro_pending_event_ids = self.macro_pending_event_ids[1:]
        request = QNetworkRequest(QUrl(self.generate_url()))
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)

        reply = QgsNetworkAccessManager.instance().get(request)
        reply.finished.connect(lambda r=reply: self._reply_finished(r))
        reply.downloadProgress.connect(self._reply_progress)

    def _reply_progress(self, received, total):
        """
        Triggered when reply progress is received
        """
        if total > 0:
            self.progress.emit(float(received) / total * 100)

    def _reply_finished(self, reply: QNetworkReply):  # pylint: disable=too-many-branches,too-many-statements
        """
        Triggered when a reply is finished
        """
        if reply.error() != QNetworkReply.NoError:
            self.message.emit(self.tr('Error: {}').format(reply.errorString()), Qgis.Critical)
            self.finished.emit(False)
            return

        if self.output_type == self.EXTENDED:  # pylint:disable=too-many-nested-blocks
            if self.service_type in (SERVICE_MANAGER.FDSNEVENT, SERVICE_MANAGER.MACROSEISMIC):
                if self.is_missing_origin_request:
                    self.result.parse_missing_origin(reply.readAll())
                    self.is_missing_origin_request = False
                else:
                    had_events_ids = bool(self.pending_event_ids)
                    if self.pending_event_ids:
                        self.pending_event_ids = self.pending_event_ids[1:]

                    prev_event_count = len(self.result.events)

                    if self.result.events:
                        self.result.add_events(reply.readAll())
                    else:
                        self.result.parse_initial(reply.readAll())
                        if self.service_type == SERVICE_MANAGER.MACROSEISMIC and not self.event_ids:
                            # for a macroseismic parameter based search, we have to then go and fetch events
                            # one by one in order to get all the mdp location information required
                            self.pending_event_ids = [e.publicID for e in self.result.events]
                        elif not had_events_ids and ((not self.service_config['settings'].get(
                                'queryincludeallorigins_multiple', False) and not self.preferred_origins_only) or
                                                     (not self.service_config['settings'].get(
                                                         'queryincludeallmagnitudes_multiple',
                                                         False) and not self.preferred_magnitudes_only)):
                            # hmmm....
                            extract_numeric_id_regex = re.compile('^.*=(.*?)$')
                            self.pending_event_ids = []
                            for e in self.result.events:
                                public_id = e.publicID
                                id_match = extract_numeric_id_regex.match(public_id)
                                assert id_match
                                self.pending_event_ids.append(id_match.group(1))

                    if self.query_limit and len(self.result.events) - prev_event_count >= self.query_limit:
                        self.exceeded_limit = True

                    self.missing_origins = self.missing_origins.union(self.result.scan_for_missing_origins())
            elif self.service_type == SERVICE_MANAGER.FDSNSTATION:
                self.result = FDSNStationXMLParser.parse(reply.readAll())
            else:
                assert False

            if self.missing_origins:
                if self.url is not None:
                    self.message.emit(
                        self.tr('QuakeML file is incomplete. {} origins are missing from the data').format(
                            len(self.missing_origins)),
                        Qgis.Warning)
                    self.finished.emit(True)
                else:
                    self.fetch_missing()
            elif self.pending_event_ids:
                self.fetch_next_event_by_id()
            elif self.ranges:
                # fetch next range
                self.event_start_date, self.event_end_date = self.ranges[0]
                del self.ranges[0]
                self.fetch_data()
            else:
                self.finished.emit(True)
        else:
            # basic output types
            if self.service_type == SERVICE_MANAGER.FDSNSTATION:
                self.result = BasicStationParser()
                self.result.parse(reply.readAll())
                self.finished.emit(True)
            else:
                if self.pending_event_ids:
                    self.pending_event_ids = self.pending_event_ids[1:]

                if not self.is_mdp_basic_text_request:
                    prev_event_count = len(self.result.events)
                    if self.result.events:
                        self.result.add_events(reply.readAll())
                    else:
                        self.result.parse(reply.readAll())

                    if self.query_limit and len(self.result.events) - prev_event_count >= self.query_limit:
                        self.exceeded_limit = True

                if self.pending_event_ids:
                    self.fetch_next_event_by_id()
                elif self.require_mdp_basic_text_request:
                    if not self.pending_event_ids:
                        # we don't yet have an explicit list of event ids to fetch -- build that now, then fire
                        # off the one-by-one requests for their details
                        self.macro_pending_event_ids = self.result.all_event_ids()

                    self.fetch_basic_mdp()
                else:
                    if self.is_mdp_basic_text_request:
                        self.result.add_mdp(reply.readAll())

                    if self.is_mdp_basic_text_request and self.macro_pending_event_ids:
                        self.fetch_basic_mdp()
                    elif self.ranges:
                        # fetch next range
                        self.event_start_date, self.event_end_date = self.ranges[0]
                        del self.ranges[0]
                        self.fetch_data()
                    else:
                        self.finished.emit(True)

    def _generate_layer_name(self, layer_type: Optional[str] = None) -> str:
        """
        Generates a good default layer name
        """
        if self.url and QUrl(self.url).isLocalFile():
            return Path(QUrl(self.url).toLocalFile()).stem

        name = self.service_id

        if self.event_min_magnitude is not None and self.event_max_magnitude is not None:
            name += ' ({:.1f} ≤ Magnitude ≤ {:.1f})'.format(self.event_min_magnitude, self.event_max_magnitude)
        elif self.event_min_magnitude is not None:
            name += ' ({:.1f} ≤ Magnitude)'.format(self.event_min_magnitude)
        elif self.event_max_magnitude is not None:
            name += ' (Magnitude ≤ {:.1f})'.format(self.event_max_magnitude)

        if self.event_ids and len(self.event_ids) == 1:
            name += ' [' + self.event_ids[0] + ']'

        if layer_type:
            name += ' - {}'.format(layer_type)

        return name

    def _create_empty_event_layer(self) -> QgsVectorLayer:
        """
        Creates an empty layer for earthquake data
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name(), 'memory')

        vl.dataProvider().addAttributes(self.result.to_event_fields(self.output_fields))
        vl.updateFields()

        try:
            # QGIS 3.14 - setup temporal handling automatically if time field was selected
            if vl.fields().lookupField('time') >= 0:
                temporal_props = vl.temporalProperties()
                temporal_props.setIsActive(True)
                temporal_props.setStartField('time')
                from qgis.core import QgsVectorLayerTemporalProperties  # pylint: disable=import-outside-toplevel
                temporal_props.setMode(QgsVectorLayerTemporalProperties.ModeFeatureDateTimeInstantFromField)

        except AttributeError:
            pass

        return vl

    def _create_empty_mdp_layer(self) -> QgsVectorLayer:
        """
        Creates an empty layer for mdp
        """
        vl = QgsVectorLayer('Point?crs=EPSG:4326', self._generate_layer_name(layer_type='mdp'), 'memory')

        vl.dataProvider().addAttributes(self.result.create_mdp_fields(self.output_fields))
        vl.updateFields()

        return vl

    def _create_empty_stations_layer(self) -> QgsVectorLayer:
        """
        Creates an empty layer for stations
        """
        vl = QgsVectorLayer('PointZ?crs=EPSG:4326', self._generate_layer_name('Stations'), 'memory')

        if self.output_type == Fetcher.BASIC:
            vl.dataProvider().addAttributes(self.result.to_station_fields())
        else:
            vl.dataProvider().addAttributes(Station.to_fields(self.output_fields))
        vl.updateFields()

        return vl

    def events_to_layer(self,  # pylint: disable=too-many-locals,too-many-branches
                        parser: Union[BasicTextParser, QuakeMlParser],
                        preferred_origin_only: bool,
                        preferred_magnitudes_only: bool) -> Optional[QgsVectorLayer]:
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_event_layer()

        features = []
        try:
            for f in parser.create_event_features(self.output_fields, preferred_origin_only, preferred_magnitudes_only):
                features.append(f)
        except MissingOriginException as e:
            self.message.emit(
                str(e),
                Qgis.Critical)
            return None

        ok, _ = vl.dataProvider().addFeatures(features)
        assert ok

        epicenter_style_url = StyleUtils.style_url(
            self.styles[SERVICE_MANAGER.FDSNEVENT]) if SERVICE_MANAGER.FDSNEVENT in self.styles else None

        if self.url:
            default_style_url = epicenter_style_url or StyleUtils.default_style_for_events_url()
            err = StyleUtils.fetch_and_apply_style(vl, default_style_url)
            if err:
                self.message.emit(err, Qgis.Warning)
        elif not self.url and (epicenter_style_url or self.service_config.get('styleurl')):
            err = StyleUtils.fetch_and_apply_style(vl, epicenter_style_url or self.service_config.get('styleurl'))
            if err:
                self.message.emit(err, Qgis.Warning)
        elif not self.url and (
                epicenter_style_url or (isinstance(self.service_config.get('default', {}).get('style', {}), dict) and
                                        self.service_config['default']['style'].get('events'))):

            style_url = None
            if epicenter_style_url:
                style_url = epicenter_style_url
            else:
                style = self.service_config['default']['style']['events']

                style_ref = style.get('style')
                if style_ref:
                    style_url = SERVICE_MANAGER.get_style(style_ref)['url']

            if style_url:
                if isinstance(self.result, BasicTextParser):
                    style_attr = style.get('classified_attribute_text')
                else:
                    style_attr = self.result.remap_attribute_name(SERVICE_MANAGER.FDSNEVENT,
                                                                  style.get('classified_attribute_xml'))
                err = StyleUtils.fetch_and_apply_style(vl, style_url, style_attr)
                if err:
                    self.message.emit(err, Qgis.Warning)

        return vl

    def mdpset_to_layer(self, parser: Union[BasicTextParser, QuakeMlParser]) -> QgsVectorLayer:  # pylint:disable=too-many-branches
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_mdp_layer()

        features = []
        for f in parser.create_mdp_features(self.output_fields, self.preferred_mdp_only):
            features.append(f)

        ok, _ = vl.dataProvider().addFeatures(features)
        assert ok

        mdp_style_url = StyleUtils.style_url(
            self.styles[SERVICE_MANAGER.MACROSEISMIC]) if SERVICE_MANAGER.MACROSEISMIC in self.styles else None

        if self.url:
            default_style_url = mdp_style_url or StyleUtils.default_style_for_macro_url()
            err = StyleUtils.fetch_and_apply_style(vl, default_style_url)
            if err:
                self.message.emit(err, Qgis.Warning)
        elif self.service_config.get('mdpstyleurl'):
            err = StyleUtils.fetch_and_apply_style(vl, mdp_style_url or self.service_config.get('mdpstyleurl'))
            if err:
                self.message.emit(err, Qgis.Warning)
        elif isinstance(self.service_config.get('default', {}).get('style', {}), dict) and \
                self.service_config['default']['style'].get('mdp'):

            style_url = None
            style = self.service_config['default']['style']['mdp']

            if mdp_style_url:
                style_url = mdp_style_url
            else:
                style_ref = style.get('style')
                if style_ref:
                    style_url = SERVICE_MANAGER.get_style(style_ref)['url']

            if style_url:
                if isinstance(self.result, BasicTextParser):
                    style_attr = style.get('classified_attribute_text')
                else:
                    style_attr = self.result.remap_attribute_name(SERVICE_MANAGER.MACROSEISMIC,
                                                                  style.get('classified_attribute_xml'))

                err = StyleUtils.fetch_and_apply_style(vl, style_url, style_attr)
                if err:
                    self.message.emit(err, Qgis.Warning)

        return vl

    def stations_to_layer(self, fdsn: Optional[Fdsn]) -> QgsVectorLayer:  # pylint:disable=too-many-branches
        """
        Returns a new vector layer containing the reply contents
        """
        vl = self._create_empty_stations_layer()

        features = []
        if self.output_type == Fetcher.BASIC:
            for f in self.result.create_station_features():
                features.append(f)
        else:
            features.extend(fdsn.to_station_features(self.output_fields))

        ok, _ = vl.dataProvider().addFeatures(features)
        assert ok

        station_style_url = StyleUtils.style_url(
            self.styles[SERVICE_MANAGER.FDSNSTATION]) if SERVICE_MANAGER.FDSNSTATION in self.styles else None

        if station_style_url or self.service_config.get('styleurl'):
            err = StyleUtils.fetch_and_apply_style(vl, station_style_url or self.service_config.get('styleurl'))
            if err:
                self.message.emit(err, Qgis.Warning)

        elif isinstance(self.service_config.get('default', {}).get('style', {}), dict) and \
                self.service_config['default']['style'].get('stations'):
            style = self.service_config['default']['style']['stations']

            style_url = None
            if station_style_url:
                style_url = station_style_url
            else:
                style_ref = style.get('style')
                if style_ref:
                    style_url = SERVICE_MANAGER.get_style(style_ref)['url']

            if style_url:
                if isinstance(self.result, BasicTextParser):
                    style_attr = style.get('classified_attribute_text')
                else:
                    style_attr = FDSNStationXMLParser.remap_attribute_name(style.get('classified_attribute_xml'))

                err = StyleUtils.fetch_and_apply_style(vl, style_url, style_attr)
                if err:
                    self.message.emit(err, Qgis.Warning)

        return vl

    def create_event_layer(self) -> Optional[QgsVectorLayer]:
        """
        Creates an event layer from the results
        """
        return self.events_to_layer(self.result, self.preferred_origins_only, self.preferred_magnitudes_only)

    def create_mdp_layer(self) -> QgsVectorLayer:
        """
        Creates an MDP layer from the results
        """
        if not hasattr(self.result, 'create_mdp_features'):
            return None

        return self.mdpset_to_layer(self.result)

    def create_stations_layer(self) -> QgsVectorLayer:
        """
        Creates a stations layer from the results
        """
        return self.stations_to_layer(self.result)
