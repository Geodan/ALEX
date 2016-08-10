from . import Arguments
from . import Subsets
from .Exceptions import MalformedSentenceException
from .WordGroup import WordGroup
import random
import string


class Filter(WordGroup):
    """A group of words that filters a dataset"""

    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)


class RadiusFilter(Filter):
    """A group of words that filters a dataset in a radius from a location"""
    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)

    def __str__(self):
        return "RadiusFilter: " + " ".join(self.words)


# TODO Fix this in the classification stage, this is no filter
class ReferenceFilter(Filter):
    """A group of words that moves the referencelocation to a location"""
    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)

    def __str__(self):
        return "ReferenceFilter: " + " ".join(self.words)
