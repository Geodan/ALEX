import Arguments
from Exceptions import MalformedSentenceException
from WordGroup import WordGroup
import random, string

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Filter(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)

class RadiusFilter(Filter):

    def __init__(self, words):
        super().__init__(words)

    # WITH buf AS (
    #     SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(4.9127781,52.3426354), 4326), 3857), 5000) geom
    # )
    # SELECT name FROM planet_osm_polygon, buf
    # WHERE way IS NOT NULL ANDz
    #     NOT ST_IsEmpty(way) AND
    #     ST_Intersects(way, buf.geom);

    def sequelize(self, arguments, context):
        print("TYPE CHECK", type(arguments[0]))
        if type(arguments[0]) != Arguments.Distance:
            raise MalformedSentenceException("No distance as argument to filter")

        distance = arguments.pop(0)

        if len(arguments) > 1 and type(arguments[0]) == Arguments.Location:
            location = arguments.pop(0)
        else:
            location = (4.9127781, 52.3426354)

        result = []
        geom_id = randomword(5)
        if not "databases" in context:
            context["databases"] = []
        context["databases"].append(geom_id)
        print("DEBUG", distance)
        print(str(distance.get_meters()))
        f_sql = (
                    "WITH " +
                    geom_id +
                    " AS (" +
                    "SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(" +
                    str(location[0]) + "," + str(location[1]) +
                    "), 4326), 3857)," +
                    str(distance.get_meters()) +
                    ") geom)"
                )
        s_sql = "ST_Intersects(way, " + geom_id + ".geom)"
        result.append((f_sql, 0))
        result.append((s_sql, -1))
        print(result)
        return result

    def __str__(self):
        return "RadiusFilter: " + " ".join(self.words)


class ExistenceFilter(Filter):

    def __init__(self, words):
        super().__init__(words)

    def sequelize(self, arguments, context):
        if type(arguments[0]) != Arguments.SearchQuery:
            raise MalformedSentenceException("No Searchquery as argument to filter")
        sq = arguments.pop(0)

        return [("PART OF QUERY: " + str(sq), -1)]

    def __str__(self):
        return "OtherFilter: " + " ".join(self.words)


class HardCodedFilterClassifier:

    def __init__(self):
        pass

    def classify(self, words, sentence, current_index):

        radius = ["in", "within", "in a radius of"]
        other = ["where there is", "where"]

        if words in radius:
            return RadiusFilter(words)
        else:
            return ExistenceFilter(words)
