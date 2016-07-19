
#TODO document these methods

class Sequelizer(object):


    def classify(self, sentence):
        pass

    def identify_datasets(self, language_objects):
        pass

    #TODO better name for semi query
    def logical_bindings(self, semi_query):
        pass

    def to_sql_and_run(self, logical_sentence):
        pass

    def convert_to_geojson(self, results):
        pass

    def __init__(self,
                cf=self.classify,
                dsf=self.identify_datasets,
                lbf=self.logical_bindings,
                sqlf=self.to_sql_and_run,
                geojf=self.convert_to_geojson
                ):
        self.cf = cf # Classification Function
        self.dsf = dsf # Dataset Identification Function
        self.lbf = lbf # Logical Bindings Function
        self.sqlf = sqlf # SQL Function
        self.geojf = geojf # GeoJSON unction

    def handle_request(self, sentence):
        pass
