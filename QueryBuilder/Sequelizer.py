import config

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

client = Wit(config.wit_token, actions)

class Sequelizer(object):


    def classify(self, sentence):
        pass

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

    def handle_request(self, sentence):
        if type(sentence) != str:
            raise ValueError("Sentence is not a string")

        language_objects = self.fn_classify(sentence)

        # TODO check nlp result

        semi_query = self.fn_identify_dataset(language_objects)

        # TODO check dataset result

        logical_sentence = self.fn_logical_bindings(semi_query)

        # TODO check logical bindings

        sql_results = self.fn_to_sql_and_run(logical_sentence)

        # TODO Check SQL results

        geojson = self.fn_convert_to_geojson(sql_results):

        # TODO Check geojson result

        return geojson
