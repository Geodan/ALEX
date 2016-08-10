from . import Arguments
from .WordGroup import WordGroup


class Command(WordGroup):
    """A group of words that tells what to do with the data"""
    def __init__(self, words):
        """
        :param words: The words
        :type string
        """
        super().__init__(words)
