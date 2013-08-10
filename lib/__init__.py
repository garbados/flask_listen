import os
from cloudant import Cloudant
from geonames import Geonames
from downloader import Downloader
from util import Data, Timer
import maps

import itertools
import collections

from nltk import pos_tag, batch_pos_tag
from nltk.tokenize import TreebankWordTokenizer
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import punkt

clou = Cloudant(**{
    "user": os.environ['CLOUDANT_USER'],
    "pass": os.environ['CLOUDANT_PASS'],
    "db": os.environ['CLOUDANT_DB']
})

# test runs
n = 1000
t = Timer()
r = clou.view('nltk', 'language', stale="ok", reduce="false", key='"en"', limit=n)
print "Got data in", t.next(), "seconds"
tweets = [row['value'] for row in r['rows']]

def tokenize(tweets):
    tokenizers = {
        "word_tokenize": word_tokenize,
        "wordpunct_tokenize": wordpunct_tokenize,
        "punkt_tokenize": punkt.PunktWordTokenizer().tokenize,
        "treebank_tokenize": TreebankWordTokenizer().tokenize,
        "regexp_tokenize": RegexpTokenizer("\w+|[=]|\S+").tokenize
    }
    times = []
    print "Tokenizing", n, "tweets"
    for name, tokenizer in tokenizers.iteritems():
        tokens = map(tokenizer, tweets)
        time = t.next()
        print name, tokens[2]
        # print name, "\n\t", time, "seconds"
        times.append([name, time])
    best_time = min(times, key=lambda x : x[1])
    print "Best time:", best_time[0], best_time[1]

def tag(tweets):
    tokens = map(RegexpTokenizer("\w+|[=]|\S+").tokenize, tweets)
    t.next()
    tags = batch_pos_tag(tokens)
    print "Tagged", n, "tweets in", t.next(), "seconds"
    print tags[0]

def untag(tweets, n=10):
    tokens = map(RegexpTokenizer("\w+|[=]|\S+").tokenize, tweets)
    all_tokens = reduce(lambda x, y: x + y, tokens)
    untags = collections.Counter(all_tokens)
    print untags.most_common(n)

if __name__ == '__main__':
    tokenize(tweets)
    # untag(tweets)