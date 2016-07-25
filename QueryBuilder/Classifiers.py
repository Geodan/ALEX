import Filters

class HardCodedFilterClassifier:

    def __init__(self):
        pass

    def classify(self, words, sentence, current_index, context=None):

        radius = ["in", "within", "in a radius of"]
        reference = ["of", "from"]

        if words in radius:
            return Filters.RadiusFilter(words)
        if words in reference:
            return Filters.ReferenceFilter(words)
