import Arguments
from Exceptions import MalformedSentenceException
from WordGroup import WordGroup
import random, string

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Filter(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words):
        super().__init__(words)

class RadiusFilter(Filter):

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "RadiusFilter: " + " ".join(self.words)


class ExistenceFilter(Filter):

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "OtherFilter: " + " ".join(self.words)

# TODO Fix this in the classification stage, this is no filter
class ReferenceFilter(Filter):

    def __init__(self, words):
        super().__init__(words)

    def __str__(self):
        return "ReferenceFilter: " + " ".join(self.words)


class HardCodedFilterClassifier:

    def __init__(self):
        pass

    def classify(self, words, sentence, current_index):

        radius = ["in", "within", "in a radius of"]
        existence = ["where there is", "where"]
        reference = ["of", "from"]


        if words in radius:
            return RadiusFilter(words)
        if words in existence:
            return ExistenceFilter(words)
        if words in reference:
            return ReferenceFilter(words)
