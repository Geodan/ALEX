class WordGroup:

    def __init__(self, sentence):
        self.words = self.split_words(sentence.lower())
        self.sentence = sentence.lower()

    # Copied from http://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
    # Modified to work with my own codebase
    def find_in_word_group(self, wg):
        sl = self.words
        l = wg.words

        sll = len(sl)
        for ind in (i for i, e in enumerate(l) if e == sl[0]):
            if l[ind:ind+sll] == sl:
                return ind, ind+sll-1
        return (-1, -1)

    def remove_n_words_from_front(self, n):
        """Removes n words from the front of the word group.

        :param n: The amount of words to remove
        :type n: int
        :returns: None
        :rtype: dict
        """
        if len(self.words) > n:
            self.words = self.words[n:]
            self.sentence = "".join(self.words)
        else:
            self.words = []
            self.sentence = "".join(self.words)

    def trim_next_word_off_sentence(self, string):
        """Removes n words from a given string and return the string

        :param string: The string to remove the next word from
        :type string: string
        :returns: The string that had the word removed
        :rtype: string
        """
        if string.find(' ') < 0:
            string = ''
            return ''
        string = string[string.strip().find(' '):].strip()
        return string

    def get_next_word(self, string):
        """Returns the next word in the given string

        :param string: The string to return the next word from
        :type string: string
        :returns: The next word in the string
        :rtype: string
        """
        if string.find(' ') < 0:
            return string

        word = string[:string.strip().find(' ')]
        return word

    def split_words(self, string):
        """Splits a string into individual words

        :param string: The string to split
        :type string: string
        :returns: The individual words in a list
        :rtype: list
        """
        result = []
        while string != '':
            next_word = self.get_next_word(string)
            if next_word != '':
                result.append(next_word)
            string = self.trim_next_word_off_sentence(string)
        return result


if __name__ == "__main__":
    wg = WordGroup("This class creates a word group from a string")
    print(wg.words)
    wg = WordGroup("It  works  with  double  spaces")
    print(wg.words)
    wg = WordGroup("and     tabs ")
    print(wg.words)
