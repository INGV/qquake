# -*- coding: utf-8 -*-
"""
Base class for QuakeML elements
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

from qgis.PyQt.QtCore import (
    QDateTime,
    Qt
)
from qgis.core import NULL


class QuakeMlElement:
    """
    Base class for QuakeML elements
    """

    def to_dict(self) -> Dict[str, object]:
        """
        Converts the element to a python dictionary
        """
        res = {
            'type': self.__class__.__name__
        }

        def convert_value(value):
            """
            Converts a value for storage in a dictionary
            """
            if value is None or value == NULL:
                return None
            if isinstance(value, (str, float, bool, int)):
                return value
            if isinstance(value, QDateTime):
                return value.toString(Qt.ISODate)
            if isinstance(value, QuakeMlElement):
                return value.to_dict()
            if isinstance(value, list):
                return [convert_value(v) for v in value]
            if isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}

            raise NotImplementedError()

        for _attr in dir(self):
            if _attr.startswith('__'):
                continue

            val = getattr(self, _attr)
            if callable(val):
                continue

            try:
                res[_attr] = convert_value(val)
            except NotImplementedError:
                assert False, (_attr, val)

        return res
