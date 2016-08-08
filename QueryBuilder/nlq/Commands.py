from . import Arguments
from .WordGroup import WordGroup


class Command(WordGroup):
    """
    For now an empty class that serves as a type identifier
    """
    def __init__(self, words):
        super().__init__(words)
