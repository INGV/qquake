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

from typing import Optional

from ..element_parser import ElementParser


class FDSNStationElementParser(ElementParser):
    """
    FDSN Station element parser
    """

    def comment(self, attribute, optional=True) -> Optional['Comment']:
        """
        Returns an attribute as a Comment
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .comment import Comment  # pylint: disable=import-outside-toplevel,cyclic-import
        return Comment.from_element(child)

    def data_availability_extent(self, attribute, optional=True) -> Optional['DataAvailabilityExtent']:
        """
        Returns an attribute as a DataAvailabilityExtent
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .data_availability_extent import \
            DataAvailabilityExtent  # pylint: disable=import-outside-toplevel,cyclic-import
        return DataAvailabilityExtent.from_element(child)

    def data_availability_span(self, attribute, optional=True) -> Optional['DataAvailabilitySpan']:
        """
        Returns an attribute as a DataAvailabilitySpan
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .data_availability_span import \
            DataAvailabilitySpan  # pylint: disable=import-outside-toplevel,cyclic-import
        return DataAvailabilitySpan.from_element(child)

    def data_availability(self, attribute, optional=True) -> Optional['DataAvailability']:
        """
        Returns an attribute as a DataAvailability
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .data_availability import DataAvailability  # pylint: disable=import-outside-toplevel,cyclic-import
        return DataAvailability.from_element(child)

    def phone_number(self, attribute, optional=True) -> Optional['PhoneNumber']:
        """
        Returns an attribute as a PhoneNumber
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .phone_number import PhoneNumber  # pylint: disable=import-outside-toplevel,cyclic-import
        return PhoneNumber.from_element(child)

    def person(self, attribute, optional=True) -> Optional['Person']:
        """
        Returns an attribute as a PhoneNumber
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .person import Person  # pylint: disable=import-outside-toplevel,cyclic-import
        return Person.from_element(child)

    def identifier(self, attribute, optional=True) -> Optional['Identifier']:
        """
        Returns an attribute as a Identifier
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .identifier import Identifier  # pylint: disable=import-outside-toplevel,cyclic-import
        return Identifier.from_element(child)

    def operator(self, attribute, optional=True) -> Optional['Operator']:
        """
        Returns an attribute as a Operator
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .operator import Operator  # pylint: disable=import-outside-toplevel,cyclic-import
        return Operator.from_element(child)

    def equipment(self, attribute, optional=True) -> Optional['Equipment']:
        """
        Returns an attribute as a Equipment
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .equipment import Equipment  # pylint: disable=import-outside-toplevel,cyclic-import
        return Equipment.from_element(child)

    def external_reference(self, attribute, optional=True) -> Optional['ExternalReference']:
        """
        Returns an attribute as a ExternalReference
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .external_reference import ExternalReference  # pylint: disable=import-outside-toplevel,cyclic-import
        return ExternalReference.from_element(child)

    def site(self, attribute, optional=True) -> Optional['Site']:
        """
        Returns an attribute as a Site
        """
        child = self.element.firstChildElement(attribute)
        if optional and child.isNull():
            return None

        from .site import Site  # pylint: disable=import-outside-toplevel,cyclic-import
        return Site.from_element(child)
