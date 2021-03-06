from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import requests
import os
import time
from config import Config
from urllib import urlencode

class CloudantListener(StreamListener):
    """ 
    A listener handles tweets are the received from the stream.
    Pipes tweets to Cloudant using Requests
    """
    def on_data(self, data):
        tweet = json.loads(data)
        if not 'delete' in tweet:
            # truncate tweet to keep db manageable
            try:
                tweet_data = {
                    "_id": str(tweet['id']),
                    "created_at": tweet['created_at'],
                    "text": tweet['text'],
                    "lang": tweet['lang'],
                    "geo": tweet['geo'],
                    "coordinates": tweet['coordinates']
                    }
            except:
                print tweet
                raise
            # normalize geodata using geonames
            if tweet_data.get('geo'):
                query = urlencode({
                    "username": Config.geo_user,
                    "lat": tweet_data['geo']['coordinates'][0],
                    "lng": tweet_data['geo']['coordinates'][1],
                    })
            elif tweet_data.get('coordinates'):
                query = urlencode({
                    "username": Config.geo_user,
                    "lat": tweet_data['coordinates']['coordinates'][1],
                    "lng": tweet_data['coordinates']['coordinates'][0],
                    })
            if tweet_data.get('geo') or tweet_data.get('coordinates'):
                url = '?'.join([Config.geo_url, query])
                r = requests.get(url)
                tweet_data.update(r.json())
            # insert to database
            r = requests.post(Config.db_url, data=json.dumps(tweet_data), headers={"Content-Type":"application/json"})
            if r.status_code == 409:
                # if revision conflict, update _rev
                # this will happen: https://dev.twitter.com/docs/streaming-apis/processing#Duplicate_messages
                r = requests.get('/'.join([Config.db_url, str(tweet_data['_id'])]))
                tweet_data['_rev'] = r.json()['_rev']
                r = requests.post(Config.db_url, data=json.dumps(tweet_data), headers={"Content-Type":"application/json"})
            if r.status_code not in [200, 201, 202]:
                # if we failed, even after catching 409, say so
                print r.status_code, r.json()
        return True

    def on_error(self, status):
        print status

def listen():
    l = CloudantListener()
    auth = OAuthHandler(Config.consumer_key, Config.consumer_secret)
    auth.set_access_token(Config.access_token, Config.access_token_secret)

    stream = Stream(auth, l, timeout=36000000)
    def attempt_connect(wait=1):
        try:
            stream.sample()
        except Exception as e:
            print e
            time.sleep(wait)
            attempt_connect(wait * 2)
    attempt_connect()

if __name__ == '__main__':
    listen()