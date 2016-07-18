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
import traceback
import time
import random

from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.utils import iface

#Find class of UI form
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geodata_nlui_dockwidget_base.ui'))

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class GeoJSONRetriever(QtCore.QObject):
    '''Worker for retrieving the GeoJSON from the GeodataNLUI and putting
    it in a QgsVectorLayer'''

    def __init__(self, url, sentence):
        QtCore.QObject.__init__(self)
        # if isinstance(layer, QgsVectorLayer) is False:
        #     raise TypeError('Worker expected a QgsVectorLayer, got a {} instead'.format(type(layer)))
        self.killed = False
        self.url = url
        self.payload = json.dumps({'sentence':  sentence, 'location': [52.3426354, 4.9127781]})
        self.headers = {'content-type': 'application/json'}

    def run(self):
        ret = None
        try:
            response = json.loads(requests.post(self.url, data=self.payload, headers=self.headers).content.decode("utf-8"))
        except Exception, e:
            self.error.emit(e, traceback.format_exc())
            return
        self.finished.emit(response)

    def kill(self):
        self.killed = True
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, basestring)


class GeodataNLUIDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = QtCore.pyqtSignal()

    def worker_finished(self, result):
        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.parserunbutton.setEnabled(True)

        if not "result" in result:
            if "error" in result:
                iface.messageBar().pushCritical(u'GeodataNLUI: ', u'Invalid sentence: ' + result["error"])
            else:
                iface.messageBar().pushCritical(u'GeodataNLUI: ', u'Invalid sentence')
            return

        self.nlquery.setText(str(result))

        #Write to a random named file, so I can open it later as a layer.

        filename = randomword(5) + '.geojson'
        with open(filename, 'w') as f:
            f.write(str(result["result"]))

        layer = iface.addVectorLayer(filename, randomword(5), "ogr")
        if not layer:
            print "Layer failed to load!"
        myLayer = iface.activeLayer()
        myLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))



    def on_error(self, e, exception_string):
        QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string),
                                    level=QgsMessageLog.CRITICAL)
        iface.messageBar().pushCritical(u'Error in GeodataNLUI: ', exception_string)
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.parserunbutton.setEnabled(True)

    def parse_and_run(self):

        self.parserunbutton.setEnabled(False)

        worker = GeoJSONRetriever('http://localhost:8085/parse_and_run_query', self.nlquery.toPlainText())
        thread = QtCore.QThread(self)
        worker.moveToThread(thread)

        worker.finished.connect(self.worker_finished)
        worker.error.connect(self.on_error)
        thread.started.connect(worker.run)
        thread.start()

        self.thread = thread
        self.worker = worker


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
