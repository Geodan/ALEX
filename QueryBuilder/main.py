import flask
import Sequelizer

app = flask.Flask(__name__)
sequelizer = Sequelizer.Sequelizer()

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

        if not "sentence" in json_data:
            return flask.jsonify({"error_code": 0, "error_message": "No sentence given"})

        location = None

        if "location" in json_data:
            location = json_data["location"]

        geojson = sequelizer.handle_request(json_data["sentence"], location)

        flask_response = {
            'result': geojson
        }

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
