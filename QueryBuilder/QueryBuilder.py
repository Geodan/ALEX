import geojson
import flask
import logging
import config
import requests
import json


from Sentence import Sentence
from wit import Wit
from pg import DB
from nltk.corpus import stopwords

db = DB(dbname='gis', host='localhost', port=5432)

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    print("Session id", session_id)
    print("Context", context)
    print("entities", entities)
    print("msg",  msg)

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
        A JSON array containing the geodata when successful. An empty array
        when not successful.
    """
    location = (52.3426354, 4.9127781)
    if flask.request.method == 'POST':
        json_data = flask.request.get_json(force=True)
        if not json_data["sentence"]:
            return flask.jsonify({})
        try:
            resp = client.converse('geobot-session-3', json_data["sentence"], {})
        except:
            return flask.jsonify({'error':'Wit returned an error'})


        if "command" not in resp["entities"]:
            return flask.jsonify({'error': 'No command given'}) #What do I have to do with the the result?

        if "local_search_query" not in resp["entities"]:
            return flask.jsonify({'error': 'No search query given'}) #What do I have to search?

        if "filter" not in resp["entities"]:
            return flask.jsonify({'error': 'No filter given'}) #How do I limit the results?

        original_sentence = json_data["sentence"].lower().strip()
        sentence_object = Sentence(original_sentence, resp)
        sql = sentence_object.sequelize()
        result = db.query(sql).getresult()
        geo_objects = []
        for polygon in result:
            polygon = polygon[0]
            geo_objects.append(geojson.Feature(geometry=geojson.loads(polygon)))


        flask_response = {
            'nlp': [str(t) for t in sentence_object.nlp_parts],
            'arguments': [str(t) for t in sentence_object.get_argument_stack()],
            'sql': sql,
            'result': geojson.dumps(geojson.FeatureCollection(geo_objects))
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
