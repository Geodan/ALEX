class WordGroup:

    def __init__(self, sentence):
        self.words = self.split_words(sentence)
        self.part = sentence

    def trim_next_word_off_sentence(self, pos):

        """
        Removes the next word from the given string.

        :returns data:
            A string with the next word removed. Empty string when there is only
            one word.
        """
        if pos.find(' ') < 0:
            pos = ''
            return ''
        pos = pos[pos.strip().find(' '):].strip()
        return pos

    def get_next_word(self, pos):

        """
        Returns the next word in the string

        :returns data:
            The next word in the sentence
        """
        if pos.find(' ') < 0:
            return pos

        word = pos[:pos.strip().find(' ')]
        return word

    def split_words(self, words):
        """
        Splits the sentence into an array of words

        :returns data:
            A string with the next word removed. Empty string when there is only
            one word.
        """
        result = []
        while words != '':
            next_word = self.get_next_word(words)
            if next_word != '':
                result.append(next_word)
            words = self.trim_next_word_off_sentence(words)
        return result

if __name__ == "__main__":
    wg = WordGroup("This class creates a word group from a string")
    print(wg.words)
    wg = WordGroup("It  works  with  double  spaces")
    print(wg.words)
    wg = WordGroup("and     tabs ")
    print(wg.words)
