from cloudant import Cloudant
import json

class Downloader(object):
    def __init__(self, **config):
        self._cloudant = Cloudant(**config)
        
    def save(self, filepath, json_data):
        with open(filepath, 'w') as f:
            f.write(json.dumps(json_data))

    def get_and_save(self, filepath, doc, query, **params):
        json_data = self._cloudant.view(doc, query, **params)
        self.save(filepath, json_data)