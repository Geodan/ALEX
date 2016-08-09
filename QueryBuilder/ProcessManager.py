import config
import logging
import geojson

from nlq import Arguments, Commands, Filters, Logic, Subsets
from nlq.temply.extractors import WordTypeTemplateExtractor
from nlq.Sentence import Sentence
from wit import Wit


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


class ProcessManager(object):

    def classify(self, sentence, context):
        try:
            resp = client.converse('geobot-session-5', sentence, {})
            print(resp)
        except:
            return {
                'type': 'error',
                'error_code': 1,
                'error_message': 'Wit returned an error'
            }
        original_sentence = sentence.lower().strip()
        sentence_object = Sentence(original_sentence, resp)

        # Best place to find the command and store it in the context
        for index, lang_object in enumerate(sentence_object.nlp_parts):
            if type(lang_object) == Commands.Command:
                if "command" in context:
                    return {
                        'type': 'error',
                        'error_code': 1,
                        'error_message': 'Two commands are not supported'
                    }
                context["command"] = lang_object
                del sentence_object.nlp_parts[index]

        context["sentence"] = sentence_object
        return {'type': 'result', 'result': sentence_object.nlp_parts}

    def identify_datasets(self, language_objects, context):

        datasets, new_sentence = self.extractor.extract_all_templates(
            language_objects, context
        )
        context["datasets"] = datasets
        return {'type': 'result', 'result': (new_sentence, datasets)}

    # TODO better name for semi query
    def logical_bindings(self, semi_query, datasets, context):

        bindings = []
        for index, query_object in enumerate(semi_query):
            obj_type = type(query_object)

            # If it is a binding
            if issubclass(obj_type, Logic.Binding):

                # If its the first or the last, it cant bind
                if index != 0 and index != (len(semi_query) - 1):

                    # The one before is our first set
                    query_object.one = index - 1

                    # Check if it is negated after where there are not etc.
                    if issubclass(type(semi_query[index + 1]), Logic.Inverter):

                        # Its inverted :D
                        query_object.inverted = True

                        # Check two spaces after, if we can
                        if index != (len(semi_query - 2)):

                            # I plus two
                            i_p_t = index + 2

                            # Set the relativity of the second set
                            query_object.two = plus_two

                            semi_query[i_p_t].relative = True
                            semi_query[i_p_t].relative_to = semi_query[i_p_t]
                        else:
                            # TODO ERROR
                            pass
                    else:
                        # I plus one
                        i_p_o = index + 1
                        query_object.two = i_p_o
                        semi_query[i_p_o].relative = True
                        semi_query[i_p_o].relative_to = semi_query[i_p_o]
                    bindings.append(query_object)
            else:
                # TODO ERROR
                pass

        return {'type': 'result', 'result': (datasets, bindings)}

    def to_sql(self, databindings, context):

        # Only test SQLization. The real parts are going to be put
        # in the SQLQuery.py file

        sql = ""
        for subset in databindings[0]:
            if not subset.relative:
                sql += self.databases[0].get_subset(subset)

        sql += "SELECT "
        for subset in databindings[0]:
            sql += "ST_AsGeoJSON(%s.way)" % (subset.id)

        sql += " FROM "

        for subset in databindings[0]:
            sql += "%s" % (subset.id)

        sql += ";"

        return {'type': 'result', 'result': sql}

    def get_geojson(self, sql, context):
        result = self.db.query(sql).getresult()
        geo_objects = []

        for poly in result:
            poly = poly[0]
            geo_objects.append(geojson.Feature(geometry=geojson.loads(poly)))

        crs = {
            "type": "name",
            "properties": {
                "name": "EPSG:" + str(context["crs"])
            }
        }
        collection = geojson.FeatureCollection(geo_objects, crs=crs)

        return {
            'type': 'result',
            'result': geojson.dumps(collection)
        }

    def __init__(self,
                 databases,
                 db,
                 cf=None,
                 dsf=None,
                 lbf=None,
                 sqlf=None,
                 geojf=None
                 ):

        self.databases = databases
        self.db = db
        if not cf:
            self.fn_classify = self.classify
        if not dsf:
            self.fn_identify_dataset = self.identify_datasets
        if not lbf:
            self.fn_logical_bindings = self.logical_bindings
        if not sqlf:
            self.fn_to_sql = self.to_sql
        if not geojf:
            self.fn_get_geojson = self.get_geojson

        self.extractor = WordTypeTemplateExtractor()

        self.extractor.add_template(
            [Arguments.SearchQuery, Filters.RadiusFilter, Arguments.Distance],
            [(0, 'sq'), (2, 'distance')],
            Subsets.RadiusSubset
        )

        self.extractor.add_template(
            [Arguments.SearchQuery, Filters.RadiusFilter, Arguments.Location],
            [(0, 'sq'), (2, 'polygon_name')],
            Subsets.PolygonSubset
        )

    def handle_request(self, sentence, location=None):
        if type(sentence) != str:
            raise ValueError("Sentence is not a string")

        context = {}
        context["crs"] = 3857

        if location:
            context["location"] = location

        language_objects = self.fn_classify(sentence, context)

        print(sentence)

        if "type" not in language_objects:
            logging.error("No type field in classification result")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'Incorrect return type'
            }

        if language_objects["type"] == "error":
            logging.error(language_objects["error_message"])
            return language_objects  # Error to client

        if "result" not in language_objects:
            logging.error("No field result in classification result?")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'No result in result'
            }

        print(language_objects)
        lang_obj_result = language_objects["result"]
        semi_query = self.fn_identify_dataset(lang_obj_result, context)

        if "type" not in semi_query:
            logging.error("No type field in dataset result")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'Incorrect return type'
            }

        if semi_query["type"] == "error":
            logging.error(semi_query["error_message"])
            return semi_query  # Error to client

        if "result" not in semi_query:
            logging.error("No field result in dataset result?")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'No result in result'
            }

        sq_result = semi_query["result"]
        logical_sentence = self.fn_logical_bindings(*sq_result, context)
        print(logical_sentence)
        if "type" not in logical_sentence:
            logging.error("No type field in dataset result")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'Incorrect return type'
            }

        if logical_sentence["type"] == "error":
            logging.error(logical_sentence["error_message"])
            return logical_sentence  # Error to client

        if "result" not in logical_sentence:
            logging.error("No field result in dataset result?")
            return {
                'type': 'error',
                'error_code': 5,
                'error_message': 'No result in result'
            }

        sql = self.fn_to_sql(logical_sentence["result"], context)

        print(sql)

        geojson = self.fn_get_geojson(sql["result"], context)

        # TODO Check geojson result

        return {
            'type': 'result',
            'result': geojson["result"]
        }
