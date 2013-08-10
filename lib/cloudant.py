import os
import requests


class Cloudant(object):

    def __init__(self, **config):
        if 'root_url' in config:
            self.root_url = config['root_url']
        else:
            self.root_url = "http://localhost:5984/{db}".format(
                **config)
            # self.root_url = "https://{user}:{pass}@{user}.cloudant.com/{db}".format(
            #     **config)

    def get(self, path, **opts):
        view_url = '/'.join([self.root_url, path])
        r = requests.get(view_url, params=opts)
        return r.json()

    def view(self, doc, name, **opts):
        view_opts = {
            "stale": "ok"
        }
        path = '/'.join(['_design', doc, '_view', name])
        opts.update(view_opts)
        return self.get(path, **opts)