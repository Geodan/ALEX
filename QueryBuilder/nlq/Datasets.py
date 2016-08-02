from enum import Enum
from . import Subsets

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

    def __init__(self, db_name, content, table, columns=None):
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

    def get_subset(self, subset):

        subset_type = type(subset)
        sql = ""
        if subset.relative:
            return ""

        if subset_type == Subsets.RadiusSubset:
            sql += """
            WITH %s AS (
                SELECT ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), 3857), %s) geom
            ),
            """ % (
                subset.id + "_radius",
                subset.location[0],
                subset.location[1],
                subset.location[2],
                subset.distance.get_meters()

            )

            sql += """
            %s AS (
                SELECT %s.way FROM %s, %s
                WHERE way IS NOT NULL AND
                    NOT ST_IsEmpty(way) AND
                    ST_Intersects(way, %s.geom)
                    AND %s LIKE '%s'
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

        elif subset_type == Subsets.PolygonSubset:
            sql += """
            WITH %s AS (
                SELECT way FROM planet_osm_polygon
                WHERE way IS NOT NULL AND
                    NOT ST_IsEmpty(way) AND
                    admin_level='10' AND
                    LOWER(name) LIKE '%s'
                    LIMIT 1
            ),
            """ % (
                subset.id + "_geom",
                subset.polygon_name
            )

            sql += """
            %s AS (
                SELECT %s.way FROM %s, %s
                WHERE %s.way IS NOT NULL AND
                    NOT ST_IsEmpty(%s.way) AND
                    ST_Intersects(%s.way, %s.way)
                    AND %s LIKE '%s'
            )
            """ % (
                subset.id,
                self.table,
                self.table,
                subset.id + "_geom",
                self.table,
                self.table,
                self.table,
                subset.id + "_geom",
                self.map_keyword_to_tags(subset.search_query.search)[0],
                self.map_keyword_to_tags(subset.search_query.search)[1]
            )


        return sql

    def map_keyword_to_tags(self, word):
        return (("building", word))

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
        if word in ["road"]:
            return [("highway", "*")]
        if word in ["train_rail", "train_line", "trainrail", "trainline"]:
            return [("railway", "rail")]
        if word in ["railroad", "rail", "railway"]:
            return [("railway", "rail"), ("railway", "subway")]
        if word in ["subway", "subway_rail","subway_line"]:
            return [("railway", "subway")]
