from .SQLQuery import SQLQuery

class BasicSQLGenerator(object):

    @classmethod
    def radius_from_point_sql(cls, name, location, distance):
        inf = {
            'lon': location[0],
            'lat': location[1],
            'proj': location[2],
            'dist': distance.get_meters()
        }
        geom = SQLQuery(alias=name)
        geom.attributes.append(
            "ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({lon}, {lat}), {proj}), 3857), {dist}) way"
        )

        sql = geom.to_string(inf)
        return sql

    @classmethod
    def polygon_from_location_sql(cls, sql_name, location_name):
        inf = {
            'name': location_name,
        }
        poly = SQLQuery(alias=sql_name)
        poly.attributes.append("way")
        poly.tables.append("planet_osm_polygon")
        poly.clauses.append("way is not null AND ")
        poly.clauses.append("NOT ST_IsEmpty(way) AND ")
        poly.clauses.append("admin_level='10'AND ")
        poly.clauses.append("LOWER(name) LIKE '{name}'")
        poly.clauses.append("LIMIT 1")

        sql = poly.to_string(inf)
        return sql
