import requests


class Geonames(object):
    root = "http://api.geonames.org"

    def __init__(self, username):
        self.opts = {
            "params": {
                "username": username,
                "type": "json"
            }
        }

    def get(self, route, **opts):
        url = '/'.join([root, route])
        opts.update(self.opts)
        r = requests.get(url, **opts)
        return r.json()
