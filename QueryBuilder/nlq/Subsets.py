import random
import string


def randomword(leng):
    """
    Generates a random of word of <leng> alphanumberical characters

    :param leng: The length of the string
    :type datasets: int
    :returns: A random alphanumerical string of length <leng>
    """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(leng))


class Subset:
    """A subset of a dataset"""
    def __init__(self):
        self.id = randomword(5)
        self.relative = False
        self.relative_to = None


class RadiusSubset(Subset):
    """A subset of a dataset, containing objects in a radius of a point"""
    def __init__(self,
                 extraction,
                 context
                 ):
        """
        :param extraction: The arguments, extracted from the sentence
        :param context: Known context about the request
        :type extraction: dict
        :type context: dict
        """
        super().__init__()
        self.search_query = extraction["sq"]
        self.distance = extraction["distance"]
        if "location" in extraction:
            self.location = extraction["location"]
        else:
            self.location = context["location"]

    def __str__(self):
        return "RadiusSubset: %s within %s from %s" % (
            self.search_query, self.distance, self.location
        )


class PolygonSubset(Subset):
    """
    A subset of a dataset, containing objects within a polygon, such
    as a city
    """
    def __init__(self,
                 extraction,
                 context
                 ):
        """
        :param extraction: The arguments, extracted from the sentence
        :param context: Known context about the request
        :type extraction: dict
        :type context: dict
        """
        super().__init__()
        self.search_query = extraction["sq"]
        self.polygon_name = extraction["polygon_name"].text
