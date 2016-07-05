import flask
import logging
import config
import requests
from Sentence import Sentence
from wit import Wit
from pg import DB
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

english_stopwords = set(stopwords.words('english'))

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
            resp = client.converse('geobot-session-1', json_data["sentence"], {})
        except:
            return flask.jsonify({'error':'Wit returned an error'})

        print(resp)

        if "command" not in resp["entities"]:
            return flask.jsonify({'error': 'No command given'}) #What do I have to do with the the result?

        if "local_search_query" not in resp["entities"]:
            return flask.jsonify({'error': 'No search query given'}) #What do I have to search?

        if "filter" not in resp["entities"]:
            return flask.jsonify({'error': 'No filter given'}) #How do I limit the results?

        # query = nlp_result_to_query(ordered_sentence, location)
        # result = str(db.query(query).getresult())
        # result = (result[:75] + '..') if len(result) > 75 else result

        original_sentence = json_data["sentence"].lower().strip()

        flask_response = {
            'sentence': Sentence(original_sentence, resp).ordered_sentence
        }
        return flask.jsonify(flask_response)


    else:
        return flask.render_template("index.html")

def trim_next_word_off_sentence(sentence):

    """
    Removes the next word from the given string.

    :returns data:
        A string with the next word removed. Empty string when there is only
        one word.
    """


    sentence = sentence[sentence.strip().find(' '):].strip()
    if sentence.find(' ') < 0:
        sentence = ''
    return sentence

def convert_distance_units_to_meters(dist_obj):
    if dist_obj["unit"] == "kilometre":
        return dist_obj["value"] * 1000


    return dist_obj["value"]

# Very basic mapping atm
def nlp_result_to_query(sentence, location=None):

    wnl = WordNetLemmatizer()

    started_with_filter = False
    attributes_to_get = None #attribute: name, toll, etc
    type_to_get = []
    database = None

    query = "SELECT * FROM "
    last_type = None
    for word, type, word_info in sentence:

        if type == "attribute":
            word = list(filter(lambda w: not w in english_stopwords, word.split()))[0]
            print(word)
            if not attributes_to_get:
                attributes_to_get = word
            else:
                attributes_to_get += word
        elif type == "search_query":
            lemma = wnl.lemmatize(word, 'n')
            if lemma == "road":
                database = "planet_osm_lines"
            else:
                database = "planet_osm_polygon"
            type_to_get.append(word)
        elif type == "logic_operator":
            if last_type == "attribute":
                query += ","
            else:
                if started_with_filter:
                    query += " "
                    query += word.upper()
                    query += " "
        elif type == "filter":
            if last_type == "search_query":
                if not started_with_filter:
                    query += database
                    query += " WHERE "
                else:
                    query += " AND "
            distance_within_filter = ["within", "in a radius of"]
            if word in distance_within_filter:
                query += "ST_Distance_Sphere(st_transform(way, 4326), ST_MakePoint("
                query += str(location[0]) + ","
                query += str(location[1])
                query += ")) < "
            started_with_filter = True

        elif type == "distance":
            query += str(convert_distance_units_to_meters(word_info))

        last_type = type

    # """
    # WITH buf AS (
    #     SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(4.9127781,52.3426354), 4326), 3857), 5000) geom
    # )
    # SELECT name FROM planet_osm_polygon, buf
    # WHERE way IS NOT NULL AND
    #     NOT ST_IsEmpty(way) AND
    #     ST_Intersects(way, buf.geom)
    #     AND amenity LIKE '%hospital%';
    # """

    if started_with_filter:
        query += " and ("
    first = True
    for search in type_to_get:
        if not first:
            query += " or "
        query += " amenity LIKE '%" + wnl.lemmatize(search, 'n') + "%'"
        first = False

    return query + ") and name is not null limit 10;"



if __name__ == "__main__":
    import os

    port = 8085

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run('0.0.0.0', port=port)
