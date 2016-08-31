from .SQLQuery import SQLQuery


class BasicSQLGenerator(object):

    @classmethod
    def radius_from_point_sql(cls, name, location, distance, projection):
        """
        Returns the SQL query for a radius selection from a point

        :param name: The name of the selection
        :param location: The location, containing [lon, lat, epsgnumber]
        :param distance: The distance object
        :type name: string
        :type location: list
        :type distance: Arguments.Distance

        :returns: the SQL query object
        :rtype: string
        """
        inf = {
            'lon': location[0],
            'lat': location[1],
            'proj': location[2],
            'to_proj': projection,
            'dist': distance.get_meters()
        }
        geom = SQLQuery(alias=name)
        geom.attributes.append(
            "ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint({lon}, {lat}), {proj}), {to_proj}), {dist}) way"
        )

        sql = geom.to_string(inf)
        return sql

    @classmethod
    def polygon_from_location_sql(cls, sql_name, location_name):
        """
        Returns the SQL query for a polygon selection of a city

        :param sql_name: The name of the selection
        :param location_name: The name of the polygon
        :type name: string
        :type location: string

        :returns: the SQL query object
        :rtype: string
        """
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
