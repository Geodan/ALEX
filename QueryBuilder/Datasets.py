from enum import Enum
import Subsets

# Maybe useful later on
class ConnectionTypes(Enum):
    SQL = 1
    HTTP = 2

class DatasetCombiner(object):

    def __init__(self, datasets):
        pass


def StatisticalModel(object):

    def __init__(self, dataset):
        self.dataset = dataset

class GeoDataset(object):

    def __init__(self, db_name, conn, content, table, columns=None):
        self.conn = conn
        self.db_name = db_name.lower()
        self.content = content
        self.table = table

        if not columns:
            # TODO Get the columns
            self.columns = []
        else:
            self.columns = columns

    def get_subset(self, subset):
        raise NotImplementedError

    def map_keyword_to_tags(self, word):
        raise NotImplementedError

    def get_location_sql(self):
        raise NotImplementedError



class OSMTable(GeoDataset):

    def __init__(self, conn, content, table, columns):
        super().__init__("OSM", conn, content, table, columns)

    def get_subset(self, subset):
        subset_type = type(subset)
        sql = ""
        if subset.relative:
            return ""
        if subset_type == Subsets.RadiusSubset:
            sql += """
            WITH %s AS (
                SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), 3857), %s) geom
            )
            """ % (
                subset.id + "_radius",
                subset.location[0],
                subset.location[1],
                subset.location[2],
                subset.distance.value
            )

            sql += """
            WITH %s AS (
                SELECT %s.way, %s, %s
                WHERE way IS NOT NULL AND
                    NOT ST_IsEmpty(way) AND
                    ST_Intersects(way, %s.geom)
                    AND %s LIKE '%s';
            )
            """ % (
                subset.id,
                self.table,
                self.table,
                subset.id + "_radius",
                subset.id + "_radius",
                self.map_keyword_to_tags(subset.search_query.search)[0],
                self.map_keyword_to_tags(subset.search_query.search)[1]
            )

        return sql

    def get_location_sql(self):
        return "ST_Centroid(way)"


class OSMPolygonTable(OSMTable):

    def __init__(self, conn):
        super().__init__(
            "lines",
            conn,
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
        return (("building", word))

class OSMLinesTable(OSMTable):

    def __init__(self, conn):
        super().__init__(
            "areas",
            conn,
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
        if word in ["road"]:
            return [("highway", "*")]
        if word in ["train_rail", "train_line", "trainrail", "trainline"]:
            return [("railway", "rail")]
        if word in ["railroad", "rail", "railway"]:
            return [("railway", "rail"), ("railway", "subway")]
        if word in ["subway", "subway_rail","subway_line"]:
            return [("railway", "subway")]
