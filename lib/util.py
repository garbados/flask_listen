import time
import json
import copy
import os
from collections import defaultdict

# with open('static/countries.geo.json', 'r') as f:
#     country_json = json.loads(f.read())

# class Countries(object):
#     def __init__(self, obj):
#         """
#         Accepts {country: features} where features is a dict
#         """

#         def filter_countries(country):
#             return country['properties']['name'] in obj.keys()

#         def map_countries(country):
#             name = country['properties']['name']
#             country['properties'].update(obj[name])
#             return country

#         countries = copy.deepcopy(country_json)
#         countries['features'] = filter(filter_countries, countries['features'])
#         countries['features'] = map(map_countries, countries['features'])
#         self.countries = countries

#     def keys(self):
#         return self.countries.keys()

#     def __getitem__(self, key):
#         return self.countries.get(key)

class Timer(object):
    """
    Stupid simple timer for ghetto profiling.
    """
    def __init__(self):
        self.stops = [time.time()]
    def next(self):
        self.stops.append(time.time())
        return self.stops[-1] - self.stops[-2]
    def sum(self):
        return self.stops[-1] - self.stops[0]

class Data(object):
    """
    Get data from downloaded files. Utility methods for parsing.
    """
    def __init__(self, filename):
        filepath = os.path.normpath(os.path.join(__file__, '..', '..', 'data', filename + '.json'))
        with open(filepath, 'r') as f:
            self.data = json.loads(f.read())
    def all(self):
        results = []
        for row in self.data['rows']:
            results.append(row['value'])
        return ' '.join(results)

class Geo(Data):
    def __init__(self):
        super(Geo, self).__init__('geo')

    def geo(self):
        results = {}
        for row in self.data['rows']:
            if row['key'][0] not in results:
                results[row['key'][0]] = {}
            if row['key'][1] not in results[row['key'][0]]:
                results[row['key'][0]][row['key'][1]] = []
            results[row['key'][0]][row['key'][1]].append(row['value'])
        for key1 in results.keys():
            for key2 in results[key1].keys():
                results[key1][key2] = ' '.join(results[key1][key2])
        return results

class Countries(Data):
    def __init__(self):
        super(Geo, self).__init__('countries')

    def countries(self):
        results = {}
        for row in self.data['rows']:
            if row['key'] not in results:
                results[row['key']] = []
            results[row['key']].append(row['value'])
        for key in results.keys():
            results[key] = ' '.join(results[key])
        return results