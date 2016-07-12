# GeodataNLUI

This repository is a set of services and bots that allows users to query geographical data using natural language.

At the moment the package consists of:

    - A telegram bot as an (very simple) I/O mechanism
    - A query builder, which builds the queries from a sentence, runs it on a postgis server and then returns corresponding geojson
    - An QGIS plugin, which allows users to send queries and see the results
    in a vector layer.
