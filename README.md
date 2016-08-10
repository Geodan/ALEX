# GeodataNLUI

This repository is a set of services and bots that allows users to query geographical data using natural language.

At the moment the package consists of:

    - A telegram bot as an (very simple) I/O mechanism
    - A query builder, which builds the queries from a sentence, runs it on a postgis server and then returns corresponding geojson
    - An QGIS plugin, which allows users to send queries and see the results
    in a vector layer.

At the moment, all of our code is written in Python. We plan of releasing the structure of the messages between components, so new appliances can be written in multiple languages.

## Some words of warning

This project is very much in alpha state. While it is in a working condition at the moment, it is subject to big changes while in development. It is also still very buggy and the codebase needs to be restructured down the road.

## But with this in mind

We would really appreciate any attention to this project! If you have any suggestions, ideas or help you can give, feel free to do so!


# Installation

### Python Requirements

Our components have requirements in the form of python modules. They can be found in the requirements.txt file.

### Postgis
Some of our components require a PostGIS installation with the OSM (open street map) data loaded in. You can  use the osm2pgsql package to achieve this. For more information, you can check their [repository](https://github.com/openstreetmap/osm2pgsql).

### QueryBuilder

The default port for a PostgreSQL server is 8085. If you change the port, you have to change it in the querybuilder as well. At the moment there is no config file yet, but the port can be changed in the QueryBuilder.py file.

To build a query, we first have to classify the intents of the words we were given. We use a service called [wit.ai](wit.ai) for this. We trained our bot with a few intents.

    - filters, which limit the amount of data given
    - logic operators, which combine multiple filters
    - local search queries, which are wat we search for
    - arguments, such as distance and locations, which filters use to fill in blanks

To use our bot, yours has to be trained like ours. Information on this will be added later. For now you can experiment by adding your wit.ai token in ```QueryBuilder/config.py```

### Telegram bot

Our telegram bot is a fairly straightforward bot. First create a bot using the Botfather. Then get your token and put that in token.txt.
After that, run the bot: ```python geo_query_bot.py```

If you don't want to host it yourself: click on [this link](https://telegram.me/geo_query_bot), which will add the bot on your telegram client.


### QGIS plugin

To install the QGIS plugin, you (obviously) have to have QGIS installed. If that is the case, copy the QGISPlugin/GeodataNLUI to ~/.qgis2/python/plugins (if you are using linux). If you are using windows, you will have to find that out yourself for now :)

## WebUI

Just host the files on a webserver and make sure the ip address in ui.js is correct!
