from .WordGroup import WordGroup


class LogicOperator(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "LogicOperator: " + " ".join(self.words)


class Inverter(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "Inverter: " + " ".join(self.words)


class Binding(WordGroup):

    """
    A group of words that semantically binds two datasets together.
    """

    def __init__(self, words):
        super().__init__(words)
        self.one = None
        self.two = None
        self.inverted = False

    def bind(self, ds1, ds2):
        raise NotImplemented


class ExistenceBinding(Binding):

    def __init__(self, words):
        super().__init__(words)

    def bind(self, ds1, ds2):
        pass

    def __str__(self):
        return "ExistenceBinding: " + " ".join(self.words)
