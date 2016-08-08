import flask
import ProcessManager
from nlq.sql import Datasets
from pg import DB

app = flask.Flask(__name__)

db = DB(dbname='gis', host='localhost', port=5432)
# nit__(self, content, table):
osm_buildings = Datasets.OSMPolygonTable()
# osm_roads = Datasets.OSMLinesTable()
process_manager = ProcessManager.ProcessManager([osm_buildings], db)


@app.route("/")
def index():
    """
    When you request the root path, you'll get the index.html template.

    """
    return flask.render_template("index.html")


@app.route("/parse_and_run_query", methods=['GET', 'POST'])
def query():
    """
    Parses the given sentence and returns the corresponding geodata

    :returns data:
        A JSON array containing the geodata when successful. An empty array
        when not successful.
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

        flask_response = result

        return flask.jsonify(flask_response)

    else:
        return flask.render_template("index.html")


if __name__ == "__main__":
    import os

    port = 8085

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run('0.0.0.0', port=port)
