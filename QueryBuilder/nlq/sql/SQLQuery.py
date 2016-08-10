class SQLQuery(object):

    def __init__(self, alias=None, attributes=None, tables=None, clauses=None):
        """
        :param alias: The alias of the selection
        :param attributes: The table attributes to select (e.g. %s.way)
        :param tables: The table names
        :param clauses: The where clauses
        :type alias: string
        :type attributes: list of strings
        :type tables: list of strings
        :type clauses: list of strings
        """

        if not attributes:
            attributes = []
        if not tables:
            tables = []
        if not clauses:
            clauses = []

        self.alias = str(alias)
        self.attributes = attributes
        self.tables = tables
        self.clauses = clauses

    def to_string(self, information, with_with=True):
        """
        Returns the SQL query as a string

        :param information: The information to fill in the SQL
        :param with_with: Should it include the WITH header
        :type alias: dict
        :type attributes: boolean

        :returns: the SQL query
        :rtype: string
        """

        if self.alias:
            if with_with:
                sql = "WITH " + self.alias + " as ("
            else:
                sql = self.alias + " as ("
        else:
            sql = ""

        sql += "SELECT "
        for i, attr in enumerate(self.attributes):
            if i > 0:
                sql += ", "
            sql += attr

        if self.tables and len(self.tables) > 0:
            sql += " FROM "

            for i, table in enumerate(self.tables):
                if i > 0:
                    sql += ", "
                sql += table

        if self.clauses and len(self.clauses) > 0:
            sql += " WHERE "

            for i, clause in enumerate(self.clauses):
                sql += clause

        if self.alias:
            sql += ")"
        else:
            sql += ""
        sql = sql.format(**information)
        return sql

    def concat(self, sqlq):
        return MultipartSQLQuery([self, sqlq])

    def __radd__(self, other):
        return MultipartSQLQuery([self, other])

    def __add__(self, other):
        return MultipartSQLQuery([self, other])

if __name__ == "__main__":
    a = SQLQuery(alias="geom")

    a.attributes.append("way")
    a.attributes.append("name")
    a.tables.append("planet_osm_polygon")
    a.clauses.append("NOT ST_EMPTY({dep1})")

    b = SQLQuery()

    b.attributes.append("way")
    b.tables.append("planet_osm_polygon")
    b.clauses.append("blablabla")

    print(a.to_string({'dep1': 'way'}))
    print(b.to_string({}))
