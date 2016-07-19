import config
import logging

from wit import Wit

#TODO document these methods


# Needed for the wit.ai client for now :c
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

db = DB(dbname='gis', host='localhost', port=5432)

client = Wit(config.wit_token, actions)

class Sequelizer(object):


    def classify(self, sentence):
        try:
            resp = client.converse('geobot-session-5', sentence, {})
        except:
            return {'type': 'error', 'error_code': 1, 'error_message':'Wit returned an error'}
        original_sentence = sentence.lower().strip()
        sentence_object = Sentence(original_sentence, resp)

        return {'type': 'result', 'result': Sentence.ordered_sentence}



    def identify_datasets(self, language_objects):
        pass

    #TODO better name for semi query
    def logical_bindings(self, semi_query):
        pass

    def to_sql_and_run(self, logical_sentence):
        pass

    def convert_to_geojson(self, results):
        pass

    def __init__(self,
                cf=self.classify,
                dsf=self.identify_datasets,
                lbf=self.logical_bindings,
                sqlf=self.to_sql_and_run,
                geojf=self.convert_to_geojson
                ):
        self.fn_classify = cf
        self.fn_identify_dataset = dsf
        self.fn_logical_bindings = lbf
        self.fn_to_sql_and_run = sqlf
        self.fn_convert_to_geojson = geojf

    def handle_request(self, sentence, location):
        if type(sentence) != str:
            raise ValueError("Sentence is not a string")

        language_objects = self.fn_classify(sentence)
        print(language_objects)

        if not "type" in language_objects:
            logging.error("No type field in classification result")
            return {'type':'error', 'error_code': 5, 'error_message':'Incorrect return type'}

        if language_objects["type"] == "error":
            return language_objects # Error to client

        if not "result" in language_objects:
            logging.error("No field result in classification result while it is a result type?")
            return {'type':'error', 'error_code': 5, 'error_message':'No result in result'}

        semi_query = self.fn_identify_dataset(language_objects["result"])

        # TODO check dataset result

        logical_sentence = self.fn_logical_bindings(semi_query)

        # TODO check logical bindings

        sql_results = self.fn_to_sql_and_run(logical_sentence)

        # TODO Check SQL results

        geojson = self.fn_convert_to_geojson(sql_results):

        # TODO Check geojson result

        return geojson
