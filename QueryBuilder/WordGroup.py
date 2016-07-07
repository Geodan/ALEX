class WordGroup:

    def __init__(self, sentence):
        self.words = self.split_words(sentence.lower())
        self.sentence = sentence.lower()

    # Copied from http://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
    # Modified to work with my own codebase
    def find_in_word_group(self, wg):
        sl = self.words
        l = wg.words

        sll=len(sl)
        for ind in (i for i,e in enumerate(l) if e==sl[0]):
            if l[ind:ind+sll]==sl:
                return ind,ind+sll-1
        return (-1, -1)

    def remove_n_words_from_front(self, n):
        if len(self.words) > n:
            self.words = self.words[n:]
            self.sentence = "".join(self.words)
        else:
            self.words = []
            self.sentence = "".join(self.words)


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

    def sequelize(self, arguments, context):
        """
        Returns a list of tuples containing SQL queries and an int
        representing the place where the subquery
        must be placed in the the total query. For instance: a 1 (one)
        will be placed as the 2nd subquery (zero indexed).
        These indexes may collide: these conflicts must be solved
        by the sequelizer.
        If the int is < 0, it must be placed relative to the wordgroups
        index in the sentence.

        Parameters:
            self - The current WordGroup
            arguments - The stack of arguments in the complete sentence
        """

        raise NotImplementedError

if __name__ == "__main__":
    wg = WordGroup("This class creates a word group from a string")
    print(wg.words)
    wg = WordGroup("It  works  with  double  spaces")
    print(wg.words)
    wg = WordGroup("and     tabs ")
    print(wg.words)
