from .WordGroup import WordGroup


class LogicOperator(WordGroup):
    """A group of words that provides logic in a sentence"""

    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)

    def __str__(self):
        return "LogicOperator: " + " ".join(self.words)


class Inverter(WordGroup):
    """A group of words that inverts the meaning of other words"""

    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)

    def __str__(self):
        return "Inverter: " + " ".join(self.words)


class Binding(WordGroup):
    """A group of words that semantically binds two datasets together"""

    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)
        self.one = None
        self.two = None
        self.inverted = False


class ExistenceBinding(Binding):
    """A group of words that is a binding of existence between two subsets"""
    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "ExistenceBinding: " + " ".join(self.words)
