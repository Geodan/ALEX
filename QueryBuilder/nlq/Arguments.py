from .WordGroup import WordGroup
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

english_stopwords = set(stopwords.words('english'))
wnl = WordNetLemmatizer()


class Type:
    Location, Distance, Amount, SearchQuery = range(4)


class Argument(WordGroup):
    """A group of words that serves as an argument to a different word"""

    def __init__(self, word, type):
        """
        Returns the corresponding amount of meters

        :returns: The amount of meters
        :rtype: int
        """
        super().__init__(word)
        self.type = type


class Location(Argument):
    """A group of words that is a location argument"""

    def __init__(self, word):
        super().__init__(word, Type.Location)
        self.text = " ".join(self.words)

    def __str__(self):
        return "Location: " + " ".join(self.words)


class Distance(Argument):
    """A group of words that represents a distance as an argument"""

    def __init__(self, word, unit):
        super().__init__(word, Type.Distance)
        self.value = int(word)
        self.unit = unit

    def get_meters(self):
        """
        Returns the corresponding amount of meters

        :returns: The amount of meters
        :rtype: int
        """
        if self.unit == "kilometre":
            return self.value * 1000
        elif self.unit == "mile":
            return self.value * 1609.344

        return self.value

    def __str__(self):
        res = "Distance: " + " ".join(self.words)
        res = res + " " + self.unit + " or " + str(self.get_meters())
        res = res + " metres"
        return res


class Amount(Argument):
    """A group of words that represents an amount as an argument"""
    def __init__(self, word):
        super().__init__(word, Type.Amount)


class SearchQuery(Argument):
    """A group of words that represents a search query as an argument"""
    def __init__(self, word):
        super().__init__(word, Type.SearchQuery)
        words = []
        for word in word.split(" "):
            words.append(wnl.lemmatize(word, 'n'))

        self.search = " ".join(words)

    def __str__(self):
        return "SearchQuery: " + self.search
