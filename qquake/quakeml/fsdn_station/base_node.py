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

from qgis.PyQt.QtXml import QDomElement

from ..element import QuakeMlElement


class BaseNodeType(QuakeMlElement):
    """
    A base node type for derivation from: Network, Station and Channel types.
    """

    def __init__(self,
                 Code,
                 StartDate,
                 EndDate,
                 SourceID,
                 RestrictedStatus,
                 AlternateCode,
                 HistoricalCode,
                 Description=None,
                 DataAvailability=None,
                 Comment=None,
                 Identifier=None):
        self.Code = Code
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.SourceID = SourceID
        self.RestrictedStatus = RestrictedStatus
        self.AlternateCode = AlternateCode
        self.HistoricalCode = HistoricalCode
        self.Description = Description
        self.DataAvailability = DataAvailability
        self.Comment = Comment
        self.Identifier = Identifier

    @staticmethod
    def _from_element(obj: 'BaseNodeType', element: QDomElement):
        """
        Populates the base node attributes from a DOM element
        """
        from .element_parser import FDSNStationElementParser  # pylint: disable=import-outside-toplevel
        parser = FDSNStationElementParser(element)
        obj.Code = parser.string('code', optional=False, is_attribute=True)
        obj.StartDate = parser.datetime('startDate', optional=False, is_attribute=True)
        obj.EndDate = parser.datetime('endDate', optional=False, is_attribute=True)
        obj.SourceID = parser.string('sourceID', optional=False, is_attribute=True)
        obj.RestrictedStatus = parser.string('restrictedStatus', is_attribute=True)
        obj.AlternateCode = parser.string('alternateCode', is_attribute=True)
        obj.HistoricalCode = parser.string('historicalCode', is_attribute=True)
        obj.Description = parser.string('Description')
        obj.Identifier = parser.identifier('Identifier', optional=True)
        obj.DataAvailability = parser.data_availability('DataAvailability', optional=True)
        obj.Comment = parser.comment('Comment', optional=True)
