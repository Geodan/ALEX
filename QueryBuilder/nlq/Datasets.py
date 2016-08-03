from enum import Enum
from . import Subsets
from .sql.SQLQuery import SQLQuery

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

    def get_geometry_table(self):
        raise NotImplementedError

class OSMTable(GeoDataset):

    def __init__(self, content, table, columns):
        super().__init__("OSM", content, table, columns)

    def get_geometry_table(self):
        return "way"

class OSMPolygonTable(OSMTable):

    def __init__(self):
        super().__init__(
            "polygons",
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

            inf = {
                'lon': subset.location[0],
                'lat': subset.location[1],
                'proj': subset.location[2],
                'dist':subset.distance.get_meters()
            }
            geom = SQLQuery(alias=str(subset.id) + "_radius")
            geom.attributes.append(
                "ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({lon}, {lat}), {proj}), 3857), {dist}) geom"
            )

            sql = geom.to_string(inf)
            sql += ', '

            tags = self.map_keyword_to_tags(subset.search_query.search)
            inf = inf = {
                'selection' : self.table + '.way',
                'table': self.table,
                'radius': subset.id + "_radius"
            }
            subset_sql = SQLQuery(alias=subset.id)
            subset_sql.attributes.append("{selection}")
            subset_sql.tables.append("{table}")
            subset_sql.tables.append("{radius}")
            subset_sql.clauses.append("{selection} IS NOT NULL AND ")
            subset_sql.clauses.append("NOT ST_isEmpty({selection}) AND ")
            subset_sql.clauses.append("ST_Intersects({selection}, {radius}.geom)")

            print(tags)
            for i, tag in enumerate(tags):
                print("TAG", tag)
                inf["tag" + str(i)] = str(tag[0])
                inf["keyword" + str(i)] = str(tag[1])
                subset_sql.clauses.append(" AND {tag%d}='{keyword%d}'" % (i,i))

            sql += subset_sql.to_string(inf, with_with=False)

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
        return [("building", word)]

class OSMLinesTable(OSMTable):

    def __init__(self):
        super().__init__(
            "lines",
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
