import os
from cloudant import Cloudant
from geonames import Geonames
from downloader import Downloader
from util import Data, Timer
import maps

from nltk import pos_tag, word_tokenize
from collections import Counter

clou = Cloudant(**{
    "user": os.environ['CLOUDANT_USER'],
    "pass": os.environ['CLOUDANT_PASS'],
    "db": os.environ['CLOUDANT_DB']
})

# test runs
t = Timer()
r = clou.view('nltk', 'language', stale="ok", reduce="false", key='"en"')
print "Got data in", t.next(), "seconds"
tweets = map(word_tokenize, [row['value'] for row in r['rows']])
print "Tokenized in", t.next(), "seconds"
print tweets[0]
print t.sum()