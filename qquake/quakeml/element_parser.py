# -*- coding: utf-8 -*-
"""
QuakeML Element parser
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
    QDateTime,
    QDate,
    QTime,
    Qt
)
from qgis.core import NULL


class ElementParser:  # pylint: disable=too-many-public-methods
    """
    QuakeML Element parser
    """

    def __init__(self, element):
        self.element = element

    def text(self) -> Optional[str]:
        """
        Returns the element text
        """
        return self.element.text()

    def string(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[str]:
        """
        Returns an attribute as a string
        """
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = self.element.attribute(attribute)
        else:
            child = self.element.firstChildElement(attribute)
            if optional and child.isNull():
                res = None
            else:
                res = child.text()
        return res

    def resource_reference(self, attribute: str, optional: bool = True) -> Optional[str]:
        """
        Returns a resource reference as a string
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        return child.text()

    def datetime(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[QDateTime]:
        """
        Returns an attribute as a QDateTime
        """

        def to_datetime(val):
            if not val:
                return NULL
            if 'T' in val:
                if '.' not in val:
                    val += '.000'
                if val[-1].upper() == 'Z':
                    val = val[:-1]
                dt = QDateTime.fromString((val + '000')[:23], 'yyyy-MM-ddThh:mm:ss.zzz')
                dt.setTimeSpec(Qt.UTC)
                return dt

            dt = QDateTime(QDate.fromString(val, 'yyyy-MM-dd'), QTime())
            dt.setTimeSpec(Qt.UTC)
            return dt

        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = to_datetime(self.element.attribute(attribute))
        else:
            child = self.element.firstChildElement(attribute)
            if optional and child.isNull():
                res = None
            else:
                res = to_datetime(child.text())
        return res

    def time_quantity(self, attribute: str, optional: bool = True) -> Optional['TimeQuantity']:
        """
        Returns an attribute as a TimeQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .common import TimeQuantity  # pylint: disable=import-outside-toplevel,cyclic-import
        return TimeQuantity.from_element(child)

    def real_quantity(self, attribute: str, optional: bool = True) -> Optional['RealQuantity']:
        """
        Returns an attribute as a RealQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional RealQuantities
        value_child = child.firstChildElement('value')
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

        from .common import RealQuantity  # pylint: disable=import-outside-toplevel,cyclic-import
        return RealQuantity.from_element(child)

    def int_quantity(self, attribute: str, optional: bool = True) -> Optional['IntegerQuantity']:
        """
        Returns an attributes as an IntegerQuantity
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        # some services include "value" element, but empty for optional IntQuantities
        value_child = child.firstChildElement('value')
        if optional and value_child.isNull() or value_child.text() is None or value_child.text() == '':
            return None

        from .common import IntegerQuantity  # pylint: disable=import-outside-toplevel,cyclic-import
        return IntegerQuantity.from_element(child)

    def float(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[float]:
        """
        Returns an attribute as a float value
        """
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = float(self.element.attribute(attribute))
        else:
            child = self.element.firstChildElement(attribute)
            if optional:
                res = float(child.text()) if not child.isNull() else None
            else:
                res = float(child.text())
        return res

    def int(self, attribute: str, optional: bool = True, is_attribute: bool = False) -> Optional[int]:
        """
        Returns an attribute as an integer value
        """
        if is_attribute:
            if optional and not self.element.hasAttribute(attribute):
                res = None
            else:
                res = int(self.element.attribute(attribute))
        else:
            child = self.element.firstChildElement(attribute)
            if optional:
                res = int(child.text()) if not child.isNull() else None
            else:
                res = int(child.text())
        return res

    def boolean(self, attribute: str, optional: bool = True) -> Optional[bool]:
        """
        Returns an attribute as a boolean value
        """
        child = self.element.firstChildElement(attribute)
        if optional:
            return bool(child.text()) if not child.isNull() else None

        return bool(child.text())

    def creation_info(self, attribute: str, optional: bool = True) -> Optional['CreationInfo']:
        """
        Returns an attribute as an CreationInfo
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .common import CreationInfo  # pylint: disable=import-outside-toplevel,cyclic-import
        return CreationInfo.from_element(child)

    def composite_time(self, attribute, optional=True) -> Optional['CompositeTime']:
        """
        Returns an attribute as a CompositeTime
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .common import CompositeTime  # pylint: disable=import-outside-toplevel,cyclic-import
        return CompositeTime.from_element(child)

    def epoch(self, attribute, optional=True) -> Optional['Epoch']:
        """
        Returns an attribute as a Epoch
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .common import Epoch  # pylint: disable=import-outside-toplevel,cyclic-import
        return Epoch.from_element(child)
