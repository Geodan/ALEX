import config
import logging
import Arguments
import Commands
import Filters

from Sentence import Sentence
from wit import Wit
from pg import DB

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


    def classify(self, sentence, context):
        try:
            resp = client.converse('geobot-session-5', sentence, {})
        except:
            return {'type': 'error', 'error_code': 1, 'error_message':'Wit returned an error'}
        original_sentence = sentence.lower().strip()
        sentence_object = Sentence(original_sentence, resp)

        # Best place to find the command and store it in the context
        for lang_object in sentence.nlp_parts:
            if type(lang_object) == Commands.Command:
                if context["command"]:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Two commands are not supported'}
                context["command"] = lang_object

        return {'type': 'result', 'result': sentence_object.nlp_parts}

    def identify_datasets(self, language_objects, context):

        argument_stack = []
        context = {}

        busy_on_filter = False
        arg_header = []
        opt_arg_header = []
        arguments = []
        optional_arguments = []

        for lang_object in language_objects:
            if issubclass(type(lang_object), Arguments.Argument):
                argument_stack.append(lang_object)

        for lang_object in language_objects:

            obj_type = type(lang_object)

            if issubclass(obj_type, Arguments.Argument):

                if busy_on_filter:
                    if len(arg_header) > 0:
                        if obj_type == arg_header[0]:
                            arguments.append(lang_object)
                            arg_header.pop(0)
                        else:
                            return {'type':'error', 'error_code': 1, 'error_message': 'Missing arguments to filter'}
                    else:
                        if obj_type == opt_arg_header[0]:
                            optional_arguments.append(lang_object)
                            opt_arg_header.pop(0)

                argument_stack.pop(0)

            if issubclass(obj_type, Filters.Filter) && obj_type != Filters.ReferenceFilter:
                busy_on_filter = True
                arg_header = lang_object.arguments
                opt_arg_header = lang_object.optional_arguments



        return

    #TODO better name for semi query
    def logical_bindings(self, semi_query, context):
        pass

    def to_sql_and_run(self, logical_sentence, context):
        pass

    def convert_to_geojson(self, results, context):
        pass

    def __init__(self,
                databases,
                cf=None,
                dsf=None,
                lbf=None,
                sqlf=None,
                geojf=None
                ):

        self.databases = databases
        if not cf:
            self.fn_classify = self.classify
        if not dsf:
            self.fn_identify_dataset = self.identify_datasets
        if not lbf:
            self.fn_logical_bindings = self.logical_bindings
        if not sqlf:
            self.fn_to_sql_and_run = self.to_sql_and_run
        if not geojf:
            self.fn_convert_to_geojson = self.convert_to_geojson

    def handle_request(self, sentence, location=None):
        if type(sentence) != str:
            raise ValueError("Sentence is not a string")

        context = {}

        language_objects = self.fn_classify(sentence, context)

        if not "type" in language_objects:
            logging.error("No type field in classification result")
            return {'type':'error', 'error_code': 5, 'error_message':'Incorrect return type'}

        if language_objects["type"] == "error":
            logging.error(language_objects["error_message"])
            return language_objects # Error to client

        if not "result" in language_objects:
            logging.error("No field result in classification result while it is a result type?")
            return {'type':'error', 'error_code': 5, 'error_message':'No result in result'}

        semi_query = self.fn_identify_dataset(language_objects["result"], context)

        # TODO check dataset result

        logical_sentence = self.fn_logical_bindings(semi_query, context)

        # TODO check logical bindings

        sql_results = self.fn_to_sql_and_run(logical_sentence, context)

        # TODO Check SQL results

        geojson = self.fn_convert_to_geojson(sql_results, context)

        # TODO Check geojson result

        return {'type':'result', 'result':None}
