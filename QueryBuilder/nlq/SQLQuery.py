

class SQLQuery(object):

    def __init__(self, sq, tables, clauses):
        self.sq = sq
        self.tables = tables
        self.clauses = clauses

    def construct_SQL(self):

        clause_length = len(self.clauses)
        sql = "SELECT %s from %s" % (self.sq.search, ",".join(self.tables))


    def append_sql_query(self, sqlq):
        
