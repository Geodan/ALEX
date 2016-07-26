import config
import logging

import Arguments
import Commands
import Filters
import Logic

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
        for index, lang_object in enumerate(sentence_object.nlp_parts):
            if type(lang_object) == Commands.Command:
                if "command" in context:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Two commands are not supported'}
                context["command"] = lang_object
                del sentence_object.nlp_parts[index]

        context["sentence"] = sentence_object
        return {'type': 'result', 'result': sentence_object.nlp_parts}

    def identify_datasets(self, language_objects, context):

        new_sentence = []

        # Current filter object
        filter_obj = None

        # The argument types the filter takes
        arg_header = []

        # The argument types the filter can optionally take extra
        opt_arg_header = []

        # Current argument stack
        arguments = []

        # Current optional argument stack
        optional_arguments = []

        # Do we have to clean up?
        cleanup = False

        context["search"] = None
        context["last_type"] = None
        context["datasets"] = []

        index = 0

        # Check all language_objects
        for lang_object in language_objects:

            obj_type = type(lang_object)

            if cleanup:
                new_dataset = filter_obj.get_dataset(context, context["search"], arguments, optional_arguments)
                new_sentence.append(new_dataset)
                context["datasets"].append(new_dataset)
                data
                filter_obj = None
                arg_header = []
                opt_arg_header = []
                arguments = []
                optional_arguments = []
                cleanup = False


            # We found something to search for :D!
            if obj_type == Arguments.SearchQuery:

                # Lets store it for now
                context["search_index"] = index
                context["search"] = lang_object

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
                            cleanup = True

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
                            cleanup = True
                    else:
                        # Its done :)
                        cleanup = True

                else:
                    cleanup = True


            # Its a filter!
            elif issubclass(obj_type, Filters.Filter) and obj_type != Filters.ReferenceFilter:

                # Maybe we are still undergoing some argument hunting?
                if filter_obj:

                    # If old filter can't be done
                    if len(arg_header) != 0:

                        # if so, malformed sentence
                        return {'type':'error', 'error_code': 1, 'error_message': 'new filter while old not done'}
                    else:
                        new_dataset = filter_obj.get_dataset(context, context["search"], arguments, optional_arguments)
                        new_sentence.append(new_dataset)
                        context["datasets"].append(new_dataset)

                        filter_obj = None
                        arg_header = []
                        opt_arg_header = []
                        arguments = []
                        optional_arguments = []


                # And if we don't know what to search for, its a malformed sentence too
                if not "search" in context:
                    return {'type':'error', 'error_code': 1, 'error_message': 'Filter without search query'}


                # Lets hunt for these arguments!
                filter_obj = lang_object
                arg_header = lang_object.arguments
                opt_arg_header = lang_object.optional_arguments


            else:
                # If old filter can't be done
                if len(arg_header) != 0:

                    # if so, malformed sentence
                    return {'type':'error', 'error_code': 1, 'error_message': 'new filter while old not done'}
                else:
                    if filter_obj:
                        new_dataset = filter_obj.get_dataset(context, context["search"], arguments, optional_arguments)
                        new_sentence.append(new_dataset)
                        context["datasets"].append(new_dataset)

                        filter_obj = None
                        arg_header = []
                        opt_arg_header = []
                        arguments = []
                        optional_arguments = []
                # The next step needs this information, so lets give it
                new_sentence.append(lang_object)

            index += 1

        # One last cleanup ey? :)
        if cleanup:
            new_dataset = filter_obj.get_dataset(context, context["search"], arguments, optional_arguments)
            new_sentence.append(new_dataset)
            context["datasets"].append(new_dataset)

            filter_obj = None
            arg_header = []
            opt_arg_header = []
            arguments = []
            optional_arguments = []

        if filter_obj:
            print(filter_obj)
            return {'type':'error', 'error_code': 1, 'error_message': 'Filter not done after sentence'}
        return {'type': 'result', 'result': (new_sentence, context["datasets"])}

    #TODO better name for semi query
    def logical_bindings(self, semi_query, context):

        bindings = []
        for index, query_object in enumerate(semi_query):
            obj_type = type(query_object)
            if issubclass(obj_type, Logic.Binding):
                if index != 0 and index != (len(semi_query) - 1):
                    query_object.one = index - 1
                    if issubclass(type(semi_query[index + 1]), Logic.Inverter):
                        query_object.inverted = True
                        if index != (len(semi_query - 2)):
                            query_object.two = index + 2
                        else:
                            #TODO ERROR
                            pass
                    else:
                        query_object.two = index + 1
                    bindings.append(query_object)
            else:
                #TODO ERROR
                pass

        return((context["datasets"], bindings))

    def to_sql_and_run(self, databindings, context):
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

        print(sentence)

        if not "type" in language_objects:
            logging.error("No type field in classification result")
            return {'type':'error', 'error_code': 5, 'error_message':'Incorrect return type'}

        if language_objects["type"] == "error":
            logging.error(language_objects["error_message"])
            return language_objects # Error to client

        if not "result" in language_objects:
            logging.error("No field result in classification result while it is a result type?")
            return {'type':'error', 'error_code': 5, 'error_message':'No result in result'}

        print(language_objects["result"])

        semi_query = self.fn_identify_dataset(language_objects["result"], context)

        if not "type" in semi_query:
            logging.error("No type field in dataset result")
            return {'type':'error', 'error_code': 5, 'error_message':'Incorrect return type'}

        if semi_query["type"] == "error":
            logging.error(semi_query["error_message"])
            return semi_query # Error to client

        if not "result" in semi_query:
            logging.error("No field result in dataset result while it is a result type?")
            return {'type':'error', 'error_code': 5, 'error_message':'No result in result'}


        logical_sentence = self.fn_logical_bindings(semi_query["result"][0], semi_query["result"][0], context)
        print(logical_sentence)

        # TODO check logical bindings

        sql_results = self.fn_to_sql_and_run(logical_sentence, context)

        # TODO Check SQL results

        geojson = self.fn_convert_to_geojson(sql_results, context)

        # TODO Check geojson result

        return {'type':'result', 'result':None}
