import config
import flask
import ProcessManager
import crossorigin
import sqlite3
import json

from nlq.sql import Datasets
from pg import DB

app = flask.Flask(__name__)

db = DB(
    dbname=config.db_name,
    host=config.db_host_name,
    port=config.db_port,
    user=config.user,
    passwd=config.password
)
# nit__(self, content, table):
osm_buildings = Datasets.OSMPolygonTable(3857)
# osm_roads = Datasets.OSMLinesTable()
process_manager = ProcessManager.ProcessManager([osm_buildings], db, config.projection)

debug_db = sqlite3.connect('log.db')
cursor = debug_db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS log (
                    id INTEGER PRIMARY KEY,
                    sentence TEXT,
                    geojson_output TEXT
                );""")


@app.route("/")
def index():
    """
    When you request the root path, you'll get the index.html template.
    """
    return flask.render_template("index.html")


@app.route("/parse_and_run_query", methods=['GET', 'POST', 'OPTIONS'])
@crossorigin.crossdomain(origin="*", headers="Content-Type")
def query():
    """
    Parses the given sentence and returns the corresponding geodata.
    Takes a JSON object with the required key 'sentence', containing the
    sentence and an optional 'location', containing an array with
    [lon, lat, espgnumber].

    :returns: JSON object as a string with the following structure:
        Successful: {
            type: "result",
            result: <geojson>
        }
        Error: {
            type: "error",
            error_code: int
            error_message: string containing the error message
        }
    """

    if flask.request.method == 'POST':
        json_data = flask.request.get_json(force=True)

        if "sentence" not in json_data:
            return flask.jsonify({
                "error_code": 0,
                "error_message": "No sentence given"
            })

        loc = None

        if "location" in json_data:
            loc = json_data["location"]

        result = process_manager.handle_request(json_data["sentence"], loc)

        log = (json_data["sentence"], json.dumps(result))
        cursor.execute("INSERT INTO log (sentence, geojson_output) VALUES (?, ?)", log)
        debug_db.commit()

        flask_response = result

        return flask.jsonify(flask_response)

    else:
        return flask.render_template("index.html")


if __name__ == "__main__":
    import os

    port = config.dev_server_port

    # Set up the development server on port 8000.
    app.debug = False
    app.run('0.0.0.0', port=port)
