# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuake, a QGIS Plugin for Loading Seismological Data From Web Services

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        copyright            : Istituto Nazionale di Geofisica e Vulcanologia (INGV)
        email                : mario.locati@ingv.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QQuake class from file QQuake.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qquake import QQuake  # pylint: disable=import-outside-toplevel
    return QQuake(iface)
