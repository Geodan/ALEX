import copy
from . import Arguments
from .import Commands
from .import Filters
from .import Logic
from .import Classifiers

from .WordGroup import WordGroup
from .Exceptions import MalformedSentenceException


class Sentence:

    def __init__(self, sentence, nlp_result):

        # default argument scope can be annoying
        self.nlp_result = nlp_result
        self.original = sentence
        self._construct_parts_from_nlp()
        self.arguments = self.get_argument_stack()

    def _construct_parts_from_nlp(self):

        ordered_sentence = []
        sentence = WordGroup(copy.copy(self.original))

        top_confidence = 0
        for c in self.nlp_result["entities"]["command"]:
            if c["confidence"] > top_confidence:
                top_confidence = c["confidence"]
                command = c["value"]

        tries = 0
        fallback = False

        while len(sentence.words) > 0:
            work_done = False
            for type in self.nlp_result["entities"]:
                for word_info in self.nlp_result["entities"][type]:
                    current_word = WordGroup(str(word_info["value"]))

                    if current_word.find_in_word_group(sentence)[0] == 0:
                        work_done = True
                        word_info["type"] = type
                        ordered_sentence.append(word_info)
                        cur_words_len = len(current_word.words)
                        sentence.remove_n_words_from_front(cur_words_len)

            if not work_done:
                tries += 1

                if tries == 2:  # Maybe it's stuck on a unit ("10km" != "10")
                    for type in self.nlp_result["entities"]:
                        for word_info in self.nlp_result["entities"][type]:

                            if len(sentence.words) == 0:
                                break

                            current_word = WordGroup(str(word_info["value"]))
                            first_of_sentence = sentence.words[0]
                            first_of_word = current_word.words[0]

                            try:
                                if first_of_sentence.index(first_of_word) == 0:
                                    # It was there :D

                                    sentence.remove_n_words_from_front(1)
                                    current_word.remove_n_words_from_front(1)

                                    word_info["type"] = type

                                    ordered_sentence.append(word_info)
                                    tries = 0
                                    continue
                            except ValueError as e:
                                pass

                elif tries == 3:  # The fallback hasnt worked :c
                    sentence.remove_n_words_from_front(1)
                    tries = 0

        nlp_parts = []

        # ----------------------
        # Must be made it's own function or class
        # ----------------------
        counter = 0
        for word in ordered_sentence:
            word_val = word["value"]
            if word["type"] == "filter":
                classifier = Classifiers.HardCodedFilterClassifier()
                nlp_parts.append(classifier.classify(word_val, self, counter))
            elif word["type"] == "local_search_query":
                nlp_parts.append(Arguments.SearchQuery(word_val))
            elif word["type"] == "distance":
                unit = word["unit"]
                nlp_parts.append(Arguments.Distance(str(word_val), unit))
            elif word["type"] == "command":
                nlp_parts.append(Commands.Command(word_val))
            elif word["type"] == "reference" or word["type"] == "location":
                nlp_parts.append(Arguments.Location(word_val))
            elif word["type"] == "logic_operator":
                nlp_parts.append(Logic.LogicOperator(word_val))
            elif word["type"] == "binding":
                classifier = Classifiers.HardCodedBindingClassifier()
                nlp_parts.append(classifier.classify(word_val, self, counter))
            counter += 1

        self.nlp_parts = nlp_parts

    def get_argument_stack(self):
        result = []
        for part in self.nlp_parts:
            if issubclass(type(part), Arguments.Argument):
                result.append(part)
        return result

    def add_part(self, part):
        self.nlp_parts.append(part)
