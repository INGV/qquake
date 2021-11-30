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

from qgis.PyQt.QtCore import QDateTime
from qgis.PyQt.QtXml import QDomElement

from ..element import QuakeMlElement
from .time_quantity import TimeQuantity


class CompositeTime(QuakeMlElement):
    """
    CompositeTime
    """

    def __init__(self,
                 year,
                 month,
                 day,
                 hour,
                 minute,
                 second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    @staticmethod
    def from_element(element: QDomElement) -> 'CompositeTime':
        """
        Constructs a CompositeTime from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return CompositeTime(year=parser.int_quantity('year', optional=True),
                             month=parser.int_quantity('month', optional=True),
                             day=parser.int_quantity('day', optional=True),
                             hour=parser.int_quantity('hour', optional=True),
                             minute=parser.int_quantity('minute', optional=True),
                             second=parser.real_quantity('second', optional=True))

    def can_convert_to_datetime(self) -> bool:
        """
        Returns True if the time can be converted to a date time
        """
        return bool(self.year and self.year.value)

    def to_timequantity(self) -> TimeQuantity:
        """
        Converts the composite time to a TimeQuantity
        """
        return TimeQuantity(value=QDateTime(self.year.value,
                                            self.month and self.month.value or 1,
                                            self.day and self.day.value or 1,
                                            self.hour and self.hour.value or 0,
                                            self.minute and self.minute.value or 0,
                                            self.second and self.second.value or 0),
                            uncertainty=None,
                            lowerUncertainty=None,
                            upperUncertainty=None,
                            confidenceLevel=None)
