import random, string

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Subset:

    def __init__(self):
        self.id = randomword(5)
        self.relative = False
        self.relative_to = None

class RadiusSubset(Subset):

    def __init__(self,
                search_query=None,
                distance=None,
                location=None,
                dataset=None
                ):
        super().__init__()
        self.search_query = search_query
        self.distance = distance
        self.location = location
        self.dataset = dataset


    def is_valid(self):
        return self.search_query and self.distance and self.location and self.dataset

    def __str__(self):
        return "RadiusSubset: %s within %s from %s" % (self.search_query, self.distance, self.location)


class GeomSubset(Subset):

    def __init__(self,
                search_query=None,
                geom=None,
                dataset=None
                ):
        self.search_query = search_query
        self.geom = geom
        self.dataset = dataset


    def is_valid(self):
        return self.search_query and self.geom and self.dataset
