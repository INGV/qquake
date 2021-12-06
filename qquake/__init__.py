# -*- coding: utf-8 -*-
"""
Plugin entry point
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QQuake class from file QQuake.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qquake import QQuake  # pylint: disable=import-outside-toplevel
    return QQuake(iface)
