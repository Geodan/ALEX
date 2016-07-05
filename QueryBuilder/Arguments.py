from WordGroup import WordGroup

class Type:
    Location, Distance, Amount, SearchQuery = range(4)
#
class Argument(WordGroup):

    def __init__(self, nlp, type):
        super().__init__(nlp["value"])
        self.type = type

class Location(Argument):
    def __init__(self, nlp):
        super().__init__(nlp["value"], Type.Location)

class Distance(Argument):
    def __init__(self, nlp):
        super().__init__(nlp["value"], Type.Distance)
        self.unit = words

    def get_meters(self):
            if dist_obj["unit"] == "kilometre":
                return dist_obj["value"] * 1000

            return int(dist_obj["value"])


class Amount(Argument):
    def __init__(self, nlp):
        super().__init__(nlp["value"], Type.Amount)

class SearchQuery(Argument):
    def __init__(self, nlp):
        super().__init__(nlp["value"], Type.SearchQuery)


def determine_type_of_argument(words):

    return Location(words)
