from . import Filters
from . import Logic


class HardCodedFilterClassifier:

    def classify(self, words, sentence, current_index, context=None):
        """Classifies a filter to a more specific word type

        :param words: The words to classify
        :param sentence: The Sentence object
        :param current_index: The index of the word in the sentence
        :param context: Known context about the request

        :type string: string
        :type string: Sentence
        :type current_index: int
        :type context: dict

        :returns: A more specific subclass of the Filter class
        :rtype: Filters.Filter subclass
        """

        radius = ["in", "within", "in a radius of"]
        reference = ["of", "from"]

        if words in radius:
            return Filters.RadiusFilter(words)
        if words in reference:
            return Filters.ReferenceFilter(words)


class HardCodedBindingClassifier:

    def classify(self, words, sentence, current_index, context=None):
        """Classifies a Binding to a more specific word type

        :param words: The words to classify
        :param sentence: The Sentence object
        :param current_index: The index of the word in the sentence
        :param context: Known context about the request

        :type string: string
        :type string: Sentence
        :type current_index: int
        :type context: dict

        :returns: A more specific subclass of the Binding class
        :rtype: Bindings.Binding subclass
        """

        existence = ["where there is", "where there are"]
        combine = ["and"]

        if words in existence:
            return Logic.ExistenceBinding(words)
