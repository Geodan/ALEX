from enum import Enum
from .SQLQuery import SQLQuery
from .utils import BasicSQLGenerator
from .. import Subsets

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
        subset_type = type(subset)
        sql = ""
        if subset.relative:
            return ""

        if subset_type == Subsets.RadiusSubset:

            sql = BasicSQLGenerator.radius_from_point_sql(
                subset.id + "_container",
                subset.location,
                subset.distance
            )
            sql += ', '

        elif subset_type == Subsets.PolygonSubset:

            sql = BasicSQLGenerator.polygon_from_location_sql(
                subset.id + "_container",
                subset.polygon_name
            )
            sql += ', '

        tags = self.map_keyword_to_tags(subset.search_query.search)
        inf = inf = {
            'selection' : self.table + '.way',
            'table': self.table,
            'container': subset.id + "_container"
        }

        subset_sql = SQLQuery(alias=subset.id)
        subset_sql.attributes.append("{selection}")
        subset_sql.tables.append("{table}")
        subset_sql.tables.append("{container}")
        subset_sql.clauses.append("{selection} IS NOT NULL AND ")
        subset_sql.clauses.append("NOT ST_isEmpty({selection}) AND ")
        subset_sql.clauses.append("ST_Intersects({selection}, {container}.way)")

        for i, tag in enumerate(tags):
            inf["tag" + str(i)] = str(tag[0])
            inf["keyword" + str(i)] = str(tag[1])
            subset_sql.clauses.append(" AND {tag%d}='{keyword%d}'" % (i,i))

        sql += subset_sql.to_string(inf, with_with=False)

        return sql

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
