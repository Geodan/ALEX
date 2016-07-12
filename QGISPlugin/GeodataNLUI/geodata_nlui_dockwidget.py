# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeodataNLUIDockWidget
                                 A QGIS plugin
 This plugin provides a GUI for our NLUI
                             -------------------
        begin                : 2016-07-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Geodan (Alexander Freeman)
        email                : alexander.freeman@geodan.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import requests
import json

from PyQt4 import QtGui, uic
from qgis.utils import iface
from PyQt4.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geodata_nlui_dockwidget_base.ui'))


class GeodataNLUIDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def parse_and_run(self):
        iface.messageBar().pushInfo(u'NLUI', u'button clicked')

        url = 'http://localhost:8085/parse_and_run_query'
        payload = json.dumps({'sentence':  self.nlquery.toPlainText()})
        headers = {'content-type': 'application/json'}
        self.parserunbutton.setEnabled(False)
        response = requests.post(url, data=payload, headers=headers).content.decode("utf-8")
        self.nlquery.setText(response)
        self.parserunbutton.setEnabled(True)


    def __init__(self, parent=None):
        """Constructor."""
        super(GeodataNLUIDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.parserunbutton.clicked.connect(self.parse_and_run)


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
