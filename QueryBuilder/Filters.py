import Arguments
from Exceptions import MalformedSentenceException
from WordGroup import WordGroup


class Filter(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)
