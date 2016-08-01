from .WordGroup import WordGroup
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

english_stopwords = set(stopwords.words('english'))
wnl = WordNetLemmatizer()

# WITH buf AS (
#     SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(4.9127781,52.3426354), 4326), 3857), 5000) geom
# )
# SELECT name FROM planet_osm_polygon, buf
# WHERE way IS NOT NULL AND
#     NOT ST_IsEmpty(way) AND
#     ST_Intersects(way, buf.geom);

class Type:
    Location, Distance, Amount, SearchQuery = range(4)
#
class Argument(WordGroup):

    def __init__(self, word, type):
        super().__init__(word)
        self.type = type

class Location(Argument):

    def __init__(self, word):
        super().__init__(word, Type.Location)

    def __str__(self):
        return "Location: " + " ".join(self.words)


class Distance(Argument):

    def __init__(self, word, unit):
        super().__init__(word, Type.Distance)
        self.value = int(word)
        self.unit = unit

    def get_meters(self):
        if self.unit == "kilometre":
            return self.value * 1000
        elif self.unit == "mile":
            return self.value * 1609.344

        return self.value

    def __str__(self):
        return "Distance: " + " ".join(self.words) + " " + self.unit + " or " + str(self.get_meters()) + " metres"


class Amount(Argument):

    def __init__(self, word):
        super().__init__(word, Type.Amount)

class SearchQuery(Argument):

    def __init__(self, word):
        super().__init__(word, Type.SearchQuery)
        words = []
        for word in word.split(" "):
            words.append(wnl.lemmatize(word, 'n'))

        self.search = " ".join(words)

    def get_database(self):
        if self.search == "road":
            database = "planet_osm_lines"
        else:
            database = "planet_osm_polygon"

        return database

    def __str__(self):
        return "SearchQuery: " + self.search
