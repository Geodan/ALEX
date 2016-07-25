from WordGroup import WordGroup

class LogicOperator(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "LogicOperator: " + " ".join(self.words)

    def sequelize(self, arguments, context):
        return [(self.words[0], -1)]
