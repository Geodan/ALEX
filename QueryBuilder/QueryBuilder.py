import flask
import logging
import config
import requests
from wit import Wit

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

        if "search_query" not in resp["entities"]:
            return flask.jsonify({'error': 'No search query given'}) #What do I have to search?

        if "filter" not in resp["entities"]:
            return flask.jsonify({'error': 'No filter given'}) #How do I limit the results?

        sentence = json_data["sentence"].lower().strip()

        ordered_sentence = []
        query = []

        top_confidence = 0
        for c in resp["entities"]["command"]:
            if c["confidence"] > top_confidence:
                top_confidence = c["confidence"]
                command = c["value"]

        counter = 0
        tries = 0

        while len(sentence) > 0:
            tries += 1
            for type in resp["entities"]:
                for word_info in resp["entities"][type]:
                    word = str(word_info["value"]).lower()
                    try:
                        if sentence.index(word) == 0:
                            tries = 0
                            sentence = sentence.replace(word, "", 1).strip()

                            ordered_sentence.append((word, type, word_info))

                            counter += 1
                            if type == "distance":
                                sentence = trim_next_word_off_sentence(sentence) #remove unit
                                break
                    except ValueError as e:
                        pass

            if tries == 3:
                counter += 1
                ordered_sentence.append((word, "unknown", {}))
                sentence = trim_next_word_off_sentence(sentence)
                tries = 0

            print("Sentence left: ", sentence)
            print("Tries left", tries)


        flask_response = {
            'nlp_result': ordered_sentence,
            'query': sentence_to_query(ordered_sentence, location)
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
def sentence_to_query(sentence, location=None):

    query = "SELECT * FROM "
    last_type = None
    for word, type, word_info in sentence:
        if type == "search_query":
            query += word
        elif type == "logic_operator":
            if last_type == "search_query":
                query += ","
            else:
                query += " "
                query += word.upper()
                query += " "
        elif type == "filter":
            if last_type == "search_query":
                query += " WHERE "
            distance_within_filter = ["within", "in a radius of"]
            if word in distance_within_filter:
                query += "ST_Distance_Sphere(geom, ST_MakePoint("
                query += str(location[0]) + ","
                query += str(location[1])
                query += ")) < "

        elif type == "distance":
            query += str(convert_distance_units_to_meters(word_info))

        last_type = type

    return query + ";"



if __name__ == "__main__":
    import os

    port = 8085

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run('0.0.0.0', port=port)
