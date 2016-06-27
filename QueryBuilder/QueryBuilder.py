import flask
import logging
import config
import requests
from wit import Wit

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
        A JSON array containing the geodata when successful. An empty array
        when not successful.
    """

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


        command = None
        search = []
        logic = []
        conditionals = []
        filter = []
        arguments = []


        top_confidence = 0
        for c in resp["entities"]["command"]:
            if c["confidence"] > top_confidence:
                top_confidence = c["confidence"]
                command = c["value"]

        counter = 0
        while len(sentence) > 0:

            for type in resp["entities"]:
                for word_info in resp["entities"][type]:
                    word = str(word_info["value"]).lower()
                    try:
                        if sentence.index(word) == 0:
                            sentence = sentence.replace(word, "", 1).strip()

                            if type == "search_query":
                                print("Search", word)
                                search.append((counter, word))
                            elif type == "filter":
                                filter.append((counter, word))
                            elif type == "distance":
                                arguments.append((counter, (word, word_info["unit"])))
                            elif type == "logic_operator":
                                logic.append((counter, word))
                            elif type == "location":
                                arguments.append((counter, word))

                            counter += 1
                            if type == "distance":
                                sentence = sentence[sentence.find(' '):].strip()
                                if sentence.find(' ') < 0:
                                    sentence = ''
                                    break

                    except ValueError as e:
                        pass

            print("Sentence left: ", sentence)
        print("Done :)")

        flask_response = {
            'command': command,
            'search': search,
            'logic': logic,
            'filter': filter,
            'conditionals': conditionals,
            'arguments': arguments
        }
        return flask.jsonify(flask_response)

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
