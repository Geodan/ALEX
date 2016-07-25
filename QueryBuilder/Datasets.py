from enum import Enum

# Maybe useful later on
class ConnectionTypes(Enum):
    SQL = 1
    HTTP = 2

def StatisticalModel(object):

    def __init__(self, dataset):
        self.dataset = dataset

class GeoDataset(object):

    def __init__(self, db_name, content, table, columns=None):
        self.db_name = db_name.lower()
        self.content = content
        self.table = table

        if columns == None:
            # TODO Get the columns
            self.columns = []
        else:
            self.columns = columns

    def map_keyword_to_tags(self, word):
        raise NotImplementedError

    def get_location_sql(self):
        raise NotImplementedError



class OSMTable(GeoDataset):

    def __init__(self, content, table, columns):
        super().__init__("OSM", content, table, columns)

    def get_location_sql(self):
        return "ST_Centroid(way)"


class OSMPolygonTable(OSMTable):

    def __init__(self):
        super().__init__(
            "lines",
            "planet_osm_polygon",
            [
                "building",
                "amenity",
                "leisure",
                "highway",
                "name",
                "way"
            ]
        )

    def map_keyword_to_tags(self, word):
        return ()

class OSMLinesTable(OSMTable):

    def __init__(self):
        super().__init__(
            "areas",
            "planet_osm_line",
            [
                "railway",
                "amenity",
                "public_transport",
                "highway",
                "name",
                "way"
            ]
        )

    def map_keyword_to_tags(self, word):
        if word in ["train_rail", "train_line", "trainrail", "trainline"]:
            return [("railway", "rail")]
        if word in ["railroads", "rail", "railway"]:
            return [("railway", "rail"), ("railway", "subway")]
        if word in ["subway", "subway_rail","subway_line"]:
            return [("railway", "subway")]
