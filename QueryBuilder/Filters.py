import Arguments
import Subsets
from Exceptions import MalformedSentenceException
from WordGroup import WordGroup
import random, string

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Filter(WordGroup):

    """
    For now an empty class that serves as a type indentifier
    """

    def __init__(self, words, args, optional_args):
        super().__init__(words)
        self.arguments = args
        self.optional_arguments = optional_args

class RadiusFilter(Filter):

    def __init__(self, words):
        super().__init__(words, [Arguments.Distance], [Arguments.Location])

    def __str__(self):
        return "RadiusFilter: " + " ".join(self.words)

    def get_dataset(self, context, sq, args, opt_args):
        if len(opt_args) == 0:
            opt_args.append(context["location"])

        return Subsets.RadiusSubset(sq, args[0], opt_args[0])


# TODO Fix this in the classification stage, this is no filter
class ReferenceFilter(Filter):

    def __init__(self, words):
        super().__init__(words, [], [])

    def __str__(self):
        return "ReferenceFilter: " + " ".join(self.words)
