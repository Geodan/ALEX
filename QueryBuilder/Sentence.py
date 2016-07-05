import copy
from WordGroup import WordGroup
import Arguments
import Commands
import Filters

class MalformedSentenceException(Exception):
    pass

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

                    print("Current word", current_word.words)
                    print("Current sentence", sentence.words)

                    if current_word.find_in_word_group(sentence)[0] == 0:
                        work_done = True
                        word_info["type"] = type
                        ordered_sentence.append(word_info)
                        sentence.remove_n_words_from_front(len(current_word.words))
                    print("tries", tries)


            if not work_done:
                tries += 1
                if tries == 2: #Maybe its stuck on a unit
                    for type in self.nlp_result["entities"]:
                        for word_info in self.nlp_result["entities"][type]:
                            if len(sentence.words) == 0:
                                break
                            current_word = WordGroup(str(word_info["value"]))
                            print("Sentence", sentence.words)
                            first_of_sentence = sentence.words[0]
                            first_of_current_word = current_word.words[0]
                            try:
                                if first_of_sentence.index(first_of_current_word) == 0:
                                    # It was there :D

                                    sentence.remove_n_words_from_front(1)
                                    current_word.remove_n_words_from_front(1)

                                    word_info["type"] = type

                                    ordered_sentence.append(word_info)
                                    tries = 0
                                    continue
                            except ValueError as e:
                                pass

                elif tries == 3: #The fallback hasnt worked :c
                    sentence.remove_n_words_from_front(1)
                    tries = 0


            print("Ordered sentence", ordered_sentence)

        self.ordered_sentence = ordered_sentence



    def get_argument_stack(self):
        # result = []
        # for part in self.parts:
        #     if type(part) is Argument:
        #         result.append(part)
        # return result
        pass

    def add_part(self, part):
        self.parts.append(part)
        # self.arguments = self.get_argument_stack()

    def sequelize(self):
        """
        Returns an SQL query generated from the parts in the SentencePart

        :returns data:
            A string containing the SQL query.
        """

        result = ""
        try:
            for part in self.parts:
                result += part.sequelize(self.arguments)
        except MalformedSentenceException as e:
            print(e)
