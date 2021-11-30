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


class Comment(QuakeMlElement):
    """
    Comment
    """

    def __init__(self,
                 text,
                 comment_id,
                 creationInfo):
        self.text = text
        self.id = comment_id
        self.creationInfo = creationInfo

    @staticmethod
    def from_element(element: QDomElement) -> 'Comment':
        """
        Constructs a Comment from a DOM element
        """
        from ..element_parser import ElementParser  # pylint: disable=import-outside-toplevel
        parser = ElementParser(element)
        return Comment(text=parser.string('text', optional=False),
                       comment_id=parser.resource_reference('id'),
                       creationInfo=parser.creation_info('creationInfo'))
