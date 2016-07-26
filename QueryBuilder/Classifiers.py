import Filters

import Logic

class HardCodedLogicClassifier:

    def classify(self, words, sentence, current_index, context=None):

        invert = ["no"]
        reference = ["of", "from"]

        if words in radius:
            return Filters.RadiusFilter(words)
        if words in reference:
            return Filters.ReferenceFilter(words)


class HardCodedFilterClassifier:

    def classify(self, words, sentence, current_index, context=None):

        radius = ["in", "within", "in a radius of"]
        reference = ["of", "from"]

        if words in radius:
            return Filters.RadiusFilter(words)
        if words in reference:
            return Filters.ReferenceFilter(words)

class HardCodedBindingClassifier:

    def classify(self, words, sentence, current_index, context=None):

        existence = ["where there is", "where there are"]
        combine = ["and"]

        if words in existence:
            return Logic.ExistenceBinding(words)
        if words in combine:
            return None #Must be combinding :')
