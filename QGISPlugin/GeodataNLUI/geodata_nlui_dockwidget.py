# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeodataNLUIDockWidget
                                 A QGIS plugin
 This plugin provides a GUI for our NLUI
                             -------------------
        begin                : 2016-07-11
        copyright            : (C) 2016 by Geodan (Alexander Freeman)
        email                : alexander.freeman@geodan.nl
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

    def __init__(self, url, sentence, location):
        QtCore.QObject.__init__(self)
        # if isinstance(layer, QgsVectorLayer) is False:
        #     raise TypeError('Worker expected a QgsVectorLayer, got a {} instead'.format(type(layer)))
        self.killed = False
        self.url = url
        self.payload = json.dumps({'sentence':  sentence, 'location': location})
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
            if "error_message" in result:
                self.iface.messageBar().pushCritical(u'GeodataNLUI: ', u'Invalid sentence: ['
                    + str(result["error_code"]) + "] " + result["error_message"])
            else:
                self.iface.messageBar().pushCritical(u'GeodataNLUI: ', u'Invalid sentence')
            return

        self.nlquery.setText(str(result))

        #Write to a random named file, so I can open it later as a layer.

        filename = randomword(5) + '.geojson'
        with open(filename, 'w') as f:
            f.write(str(result["result"]))

        layer = self.iface.addVectorLayer(filename, randomword(5), "ogr")
        if not layer:
            print "Layer failed to load!"
        myLayer = self.iface.activeLayer()
        myLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))



    def on_error(self, e, exception_string):
        QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string),
                                    level=QgsMessageLog.CRITICAL)
        self.iface.messageBar().pushCritical(u'Error in GeodataNLUI: ', exception_string)
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.parserunbutton.setEnabled(True)

    def parse_and_run(self):

        self.parserunbutton.setEnabled(False)

        canvas_coords = iface.mapCanvas().extent()

        location_x = ((canvas_coords.xMaximum() - canvas_coords.xMinimum()) /2) + canvas_coords.xMinimum()

        location_y = ((canvas_coords.yMaximum() - canvas_coords.yMinimum()) /2) + canvas_coords.yMinimum()

        worker = GeoJSONRetriever('http://localhost:8085/parse_and_run_query',
                self.nlquery.toPlainText(), [location_x, location_y, int(self.canvas.mapRenderer().destinationCrs().authid().split(":")[1])])
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

        # Save reference to the QGIS interface
        self.iface = iface
        # reference to map canvas
        self.canvas = self.iface.mapCanvas()
        # our click tool will emit a QgsPoint on every click
        # self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # # create our GUI dialog
        # self.dlg = vector_selectbypointDialog()


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
