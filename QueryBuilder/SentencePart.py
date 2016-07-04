from .Area import Area

class SentencePart:

    def __init__(self, type, parts = None):

        # default argument scope can be annoying
        if parts is None:
            self.parts = []
        else:
            self.parts = []
        self.column_mapping = {
            "road": ""
        }

    def get_argument_stack(self):
        result = []
        for part in self.parts:
            if type(part) is Argument:
                result.append(part)
        return result

    def sequelize(self):
        """
        Returns an SQL query generated from the parts in the SentencePart

        :returns data:
            A string containing the SQL query.
        """
