import config
import logging

import Arguments
import Commands
import Filters
import LogicOperators

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
        for lang_object in sentence_object.nlp_parts:
            if type(lang_object) == Commands.Command:
                if "command" in context:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Two commands are not supported'}
                context["command"] = lang_object
        context["sentence"] = sentence_object
        return {'type': 'result', 'result': sentence_object.nlp_parts}

    def identify_datasets(self, language_objects, context):

        new_sentence = []

        filter_obj = None
        arg_header = []
        opt_arg_header = []
        arguments = []
        optional_arguments = []


        context["search"] = None
        context["last_type"] = None

        index = 0

        for lang_object in language_objects:

            obj_type = type(lang_object)

            # We found something to search for :D!
            if obj_type == Arguments.SearchQuery:

                # Lets store it for now
                context["search_index"] = index
                context["search"] = lang_object
                continue

            elif issubclass(obj_type, Arguments.Argument):
                if not filter_obj:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Argument before filter'}

                # If there are still arguments left
                if len(arg_header) > 0:

                    # And it is the right type
                    if arg_header[0] == obj_type:

                        #Take it!
                        arg_header.pop(0)
                        arguments.append(lang_object)

                        #If its the last word and there are no arguments left
                        if index == (len(language_objects) - 1) and len(arg_header) == 0:

                            # Its done :)

                            # TODO clean up these 'done' parts
                            new_sentence.append(filter_obj.get_dataset(context, context["search"], arguments, optional_arguments))

                            filter_obj = None
                            arg_header = []
                            opt_arg_header = []
                            arguments = []
                            optional_arguments = []

                    else:
                        # Otherwise its a malformed sentence
                        return {'type':'error', 'error_code': 1, 'error_message': 'Needed arg not found'}

                # Maybe there is an optional argument left?
                elif len(opt_arg_header) > 0:

                    # If it is what we are searching for
                    if opt_arg_header[0] == obj_type:

                        #Store it
                        optional_arguments.pop(0)
                        optional_arguments.append(lang_object)

                        #If its the last word and there are no optional arguments left
                        if index == (len(language_objects) - 1) and len(opt_arg_header) == 0:

                            # Its done :)

                            # TODO clean up these 'done' parts
                            new_sentence.append(filter_obj.get_dataset(context, context["search"], arguments, optional_arguments))

                            filter_obj = None
                            arg_header = []
                            opt_arg_header = []
                            arguments = []
                            optional_arguments = []
                    else:
                        # we are done!
                        # TODO clean up these 'done' parts


                        new_sentence.append(filter_obj.get_dataset(context, context["search"], arguments, optional_arguments))

                        filter_obj = None
                        arg_header = []
                        opt_arg_header = []
                        arguments = []
                        optional_arguments = []

                else:

                    # TODO clean up these 'done' parts

                    new_sentence.append(filter_obj.get_dataset(context, context["search"], arguments, optional_arguments))

                    filter_obj = None
                    arg_header = []
                    opt_arg_header = []
                    arguments = []
                    optional_arguments = []

            # Its a filter!
            elif issubclass(obj_type, Filters.Filter) and obj_type != Filters.ReferenceFilter:

                # Maybe we are still undergoing some argument hunting?
                if filter_obj:
                    # if so, malformed sentence
                    return {'type':'error', 'error_code': 1, 'error_message': 'new filter while old not done'}

                # And if we don't know what to search for, its a malformed sentence too
                if not "search" in context:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Filter without search query'}


                # Lets hunt for these arguments!
                filter_obj = lang_object
                arg_header = lang_object.arguments
                opt_arg_header = lang_object.optional_arguments

            else:
                # The next step needs this information, so lets give it
                new_sentence.append(lang_object)
                
        if filter_obj:
            return {'type':'error', 'error_code': 1, 'error_message': 'Filter not done after sentence'}
        return new_sentence

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

        if location:
            context["location"] = location

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
        print(semi_query)

        # TODO check dataset result

        logical_sentence = self.fn_logical_bindings(semi_query, context)

        # TODO check logical bindings

        sql_results = self.fn_to_sql_and_run(logical_sentence, context)

        # TODO Check SQL results

        geojson = self.fn_convert_to_geojson(sql_results, context)

        # TODO Check geojson result

        return {'type':'result', 'result':None}
