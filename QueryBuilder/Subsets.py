

class RadiusSubset(object):

    def __init__(self,
                search_query=None,
                distance=None,
                location=None,
                dataset=None
                ):
        self.search_query = search_query
        self.distance = distance
        self.location = location
        self.dataset = dataset


    def is_valid(self):
        return self.search_query and self.distance and self.location and self.dataset


class GeomSubset(object):

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
