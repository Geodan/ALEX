import Arguments
from WordGroup import WordGroup

class Command(WordGroup):

    def __init__(self, words):
        super().__init__(words)

    def sequelize(self, arguments, context):
        if type(arguments[0]) != Arguments.SearchQuery:
            raise MalformedSentenceException("No SearchQuery to find")

        if not "databases" in context:
            context["databases"] = []

        sql_statements = []
        while type(arguments[0]) == Arguments.SearchQuery:
            arg = arguments.pop(0)
            context["databases"].append(arg.get_database())
            sql_statements.append(("AND building LIKE '" + arg.search + "'", 1000))

        sql_statements.append(("SELECT ST_AsGeoJSON(way) FROM {databases} WHERE ", 0))
        return sql_statements

    def __str__(self):
        return "Command: " + " ".join(self.words)
