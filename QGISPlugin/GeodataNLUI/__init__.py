# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeodataNLUI
                                 A QGIS plugin
 This plugin provides a GUI for our NLUI
                             -------------------
        begin                : 2016-07-11
        copyright            : (C) 2016 by Geodan (Alexander Freeman)
        email                : alexander.freeman@geodan.nl
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
    """Load GeodataNLUI class from file GeodataNLUI.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geodata_nlui import GeodataNLUI
    return GeodataNLUI(iface)
