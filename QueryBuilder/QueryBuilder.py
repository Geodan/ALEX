import flask
from wit import Wit
import logging

import .config

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    return context

def error(session_id, context, e):
    print(str(e))

actions = {
    'say': say,
    'merge': merge,
    'error': error,
}

app = flask.Flask(__name__)
client = Wit(config.wit_token, actions)

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
        A JSON array containing the geodata when successfull. An empty array
        when not successful.
    """

    if flask.request.method == 'POST':
        json_data = flask.request.get_json(force=True)
        print(json_data)
        if not json_data["sentence"]:
            return flask.jsonify({})
        return flask.jsonify({'result': "Success"})


    else:
        return flask.render_template("query.html")


if __name__ == "__main__":
    import os

    port = 8085

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run('0.0.0.0', port=port)
