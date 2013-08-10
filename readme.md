# NLTK Listen

Flask app for streaming the Twitter public stream into a Cloudant database, using tweepy, gunicorn, and Heroku.

Like [twit_listen](https://github.com/garbados/twit_listen) but in Python.

## Install

First, get the project:

    git clone git@github.com:garbados/flask_listen.git
    cd flask_listen
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Then, configuration. Per Heroku's [configuration recommendations](https://devcenter.heroku.com/articles/config-vars), create a .env file that contains the following:

### Cloudant credentials

Get these by creating an account on [Cloudant](https://cloudant.com/):

* CLOUDANT_USER: your Cloudant username
* CLOUDANT_PASS: your Cloudant password
* CLOUDANT_DB: the database to dump tweets into

### Twitter credentials

Get these by registering an app with [Twitter](https://dev.twitter.com/):

* TWITTER_CONSUMER_KEY
* TWITTER_CONSUMER_SECRET
* TWITTER_ACCESS_KEY
* TWITTER_ACCESS_SECRET

Lastly, let's push this mess to Heroku:

    heroku create
    heroku config:push
    git push heroku master

That should yield a URL where your app lives. To start the listener, do this:

    heroku ps:scale worker=1

You're done! One dyno is serving your app to the world, while the other streams tweets into Cloudant.

## NLTK vs Twitter: A Voyage into Linguistic Frontiers

Language is complicated. A few months ago, I used Google's Ngram dataset to examine how languages have evolved in their use of parts of speech, whether that evolution is accelerating with time, and whether it responds to historical events. You can check it out [here](http://lsm-research.herokuapp.com/).

I found three things:

* Different parts of speech evolve together, proportionally or inversely. In European languages, prepositions, postpositions, determiners, and articles all move together, while pronouns and numerals move in opposition to each other.
* Different parts of speech react to different events, such as war or shared cultural events like the televised Apollo 11 mission, which 93% of homes witnessed.
* Language style was evolving more slowly over time until 2008, when the Great Recession hit and various parts of speech went wonky.

I thought, hey, that's pretty cool, but Google's Ngram dataset is limited to books. Do these findings hold true for other mediums?

### Why Twitter?

As of May 7, 2013, Twitter users generate 9,100 tweets every second. 115 million users tweet every month. That's a tremendous amount of linguistic data, from a tremendous cross-section of the global populace.

Plus, the public stream endpoint on Twitter's API lets you grab about 30% of new tweets as they're created, or about 17.4 million tweets a day, plus metadata like geo-coordinates. As a result of that endpoint, collecting tweets en masse is about as hard as falling on your face.

(Stats from [statisticbrain.com](http://www.statisticbrain.com/twitter-statistics/))

### Flask Listen

For Pycon Canada, I wrote [Flask Listen](https://github.com/garbados/flask_listen), a two-process web app that streams tweets into a Cloudant database, and uses Geonames to flesh out geo-coordinates into country names, etc. I used a modified version of Flask Listen for this talk, which is available under the PyCon branch.

Here's how it works:

**Tools**

* [Tweepy](https://github.com/tweepy/tweepy): A Twitter library for Python.
* [Requests](http://docs.python-requests.org/en/latest/): The best HTTP library for Python.
* [Flask](http://flask.pocoo.org/): A puny web framework ideal for minimal apps like this.
* [Cloudant](https://cloudant.com/): A CouchDB-like NoSQL database built to scale.
* [Geonames](http://www.geonames.org/): Web service for manipulating geographic data.

**Worker Process**

* Tweepy listens to the public Twitter stream.
* If a tweet has geo-coordinates, get details (country, etc) from Geonames.
* If we've already inserted this tweet (Twitter will sometimes send duplicates), update the document rather than insert a new one. Else, insert into Cloudant.

    # Tweepy code sample from `listen.py`
    def listen():
        # custom listener for getting geonames data and inserting into cloudant
        l = CloudantListener()
        # oauth!
        auth = OAuthHandler(Config.consumer_key, Config.consumer_secret)
        auth.set_access_token(Config.access_token, Config.access_token_secret)
        # give twitter plenty of time before we timeout
        stream = Stream(auth, l, timeout=36000000)
        # begin listening!
        stream.sample()

    if __name__ == '__main__':
        listen()

**App Process**

* Requests gets the number of tweets from Cloudant.
* JavaScript on the homepage displays that number, updating it every few seconds.

    # contents of `app.py`
    import flask
    import requests
    import os
    from config import Config # custom settings

    app = flask.Flask(__name__)

    def get_count():
      # get the current number of tweets in the database
      url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
      r = requests.get(url)
      return r.json()['total_rows']

    @app.route('/count')
    def count():
      return flask.jsonify({"count": get_count()})

    @app.route('/')
    def index():
        return flask.render_template('index.html', count=get_count())

    if __name__ == '__main__':
      port = int(os.environ.get('PORT', 5000))
      app.run(port=port)

### Enter the NLTK

I got lucky with the Google Ngrams research, since Google updated the dataset in 2012 with parts of speech and other grammatical data, so I didn't have to determine any of it myself. Turns out, doing semantic and grammatical analysis is super complicated. Enter the NLTK.

If you're not familiar, the NLTK, or Natural Language Tool Kit, is a Python library for working with human language data. It contains a tremendous number of tools for parsing, tokenizing, classifying, and analyzing language, along with numerous algorithms for autonomously learning language.

Now that we've got our listener up, let's see what the NLTK can do for us. Given a tweet like this...

> meaning while I'm just here like waiting for this stuff to come off http://t.co/HRout5G3Uo

What can we do? Let's start by tokenizing the tweet into words.

    import cloudant # helper for interacting with Cloudant
    from nltk import word_tokenize # word tokenizer

    r = cloudant.view('nltk', 'language', stale="ok", reduce="false", key='"en"', limit=1)
    tweets = map(word_tokenize, [row['value'] for row in r['rows']])
    print tweets[0]
    >>> [u'meaning', u'while', u'I', u"'m", u'just', u'here', u'like', u'waiting', u'for', u'this', u'stuff', u'to', u'come', u'off', u'http', u':', u'//t.co/HRout5G3Uo']

Cool! Well, mostly. The tokenizer intelligently splits words like "I'm" and separates punctuation from adjacent words, but it mangles the URL this person shared into the protocol, a colon, and the rest of the link. Splitting out the protocol isn't bad, since we can use that to tell how many links are being shared and where, but that colon is going to skew any analysis of punctuation. 

Before we fix it, what happens if we just, y'know, do nothing? Let's try tagging the tweet's parts of speech:

    # continuing from the last sample...
    from nltk import pos_tag
    tagged_tweets = map(pos_tag, tweets)
    print tagged_tweets[0]
    >>> [(u'meaning', 'VBG'), (u'while', 'IN'), (u'I', 'PRP'), (u"'m", 'VBP'), (u'just', 'RB'), (u'here', 'RB'), (u'like', 'IN'), (u'waiting', 'VBG'), (u'for', 'IN'), (u'this', 'DT'), (u'stuff', 'NN'), (u'to', 'TO'), (u'come', 'VB'), (u'off', 'RP'), (u'http', 'NN'), (u':', ':'), (u'//t.co/HRout5G3Uo', 'JJ')]

All those `VBG` and `IN` markers are code for parts of speech. What these tags mean will depend on which tagger you use. The default `pos_tag` uses the [Penn Treebank tagset](http://www.monlp.com/2011/11/08/part-of-speech-tags/).

Back to our link concerns: "http" is considered a noun, while the non-protocol part of the URL is, um, an adjective?

This gets even wackier with hashtags. Given this tweet...

> Most Extreme Elimination Challenge=Best show ever #rightyouareken

We tokenize into this:

    >>> [u'Most', u'Extreme', u'Elimination', u'Challenge=Best', u'show', u'ever', u'#', u'rightyouareken']

The default tokenizer doesn't split on "=", and it separates the pound sign from the rest of the hashtag, which leads to tagging hilarity:

    >>> [(u'Most', 'JJS'), (u'Extreme', 'NNP'), (u'Elimination', 'NNP'), (u'Challenge=Best', 'NNP'), (u'show', 'NN'), (u'ever', 'RB'), (u'#', '#'), (u'rightyouareken', 'VBN')]

"rightyourareken"'s `VBN` tag means our tagger thinks it's a... past participle? In the abstract for this talk, I said we'd answer what part of speech hashtags are. Well, there you have it. They're past participles. Thanks, NLTK.

Joking aside, we need to fix this.

### Tokenizers

The NLTK comes with a ton of tokenizers. Here's a few of them, and how they work:

#### word_tokenize

The one we've been using so far. It's actually just an alias to TreebankWordTokenizer, which uses the Penn Treebank to intelligently transform contractions, punctuation, etc.

#### wordpunct_tokenize

Uses a regular expression to split on any punctuation. This results in hilarity when confronted with URLs:

    [u'meaning', u'while', u'I', u"'", u'm', u'just', u'here', u'like', u'waiting', u'for', u'this', u'shit', u'to', u'come', u'off', u'http', u'://', u't', u'.', u'co', u'/', u'HRout5G3Uo']

One link becomes 7 tokens. Ouch.

#### Punkt

Punkt usually refers to an unsupervised (self-training) algorithm to learn how to split sentences. Its word tokenizer uses a regular expression that differs mildly from the Penn Treebank method.

    [u'meaning', u'while', u'I', u"'m", u'just', u'here', u'like', u'waiting', u'for', u'this', u'shit', u'to', u'come', u'off', u'http', u':', u'//t.co/HRout5G3Uo']

Equivalent to `word_tokenize`, so not good enough.

#### RegexpTokenizer

Splits the string using a regular expression. Straightforward, and ridiculously fast. Check it out:

    # regex: "\w+|[=]|\S+"
    Tokenizing 10000 tweets
    word_tokenize 
      3.00718903542 seconds
    wordpunct_tokenize 
      0.11208987236 seconds
    regexp_tokenize 
      0.0827131271362 seconds
    punkt_tokenize 
      0.237197875977 seconds
    Best time: regexp_tokenize

For Twitter parsing, I use RegexpTokenizer. Here's what that pattern does to our sample:

    [u'meaning', u'while', u'I', u"'m", u'just', u'here', u'like', u'waiting', u'for', u'this', u'shit', u'to', u'come', u'off', u'http', u'://t.co/HRout5G3Uo']

"I'm" becomes "I" and "'m", while the link becomes "http" followed by the rest of the URL, helping us count links while 
isolating the unique parts of the URL.

The trouble with regex is edge cases. Keep an eye out for wonky or unexpected tokens, and update your pattern accordingly. For our purposes, this pattern is good enough.

### Back to Tagging -- Or not

Part of speech tagging is cool for semantic and grammatical analysis, but for large datasets, it gets to be a huge pain. Here's why:

    Tagged 10,000 tweets in 199.993138075 seconds

For a dataset that grows by hundreds of thousands of rows every hour, more than three minutes per ten thousand is prohibitively slow.

So, what can we do instead? My previous research required parts of speech, so how can I possibly go without?

Language style analysis looks at function words, parts of speech like articles and pronouns, which indicate the relationship between content words (nouns, verbs) without themselves being content. What is and isn't a function word, like most things in linguistics, depends on who you ask.

But function words, as a group, are more common in language than content words. For example, you probably say "it" more than "chair". 

We can get a rough proxy of function words by taking the N most common tokens from a dataset. For that, we won't use the NLTK at all. Instead, we'll use `collections`:

    import collections

    # given 1000 tweets...
    tokens = map(RegexpTokenizer("\w+|[=]|\S+").tokenize, tweets)
    all_tokens = reduce(lambda x, y: x + y, tokens)
    untags = collections.Counter(all_tokens)
    print untags.most_common(10)
    >>> [(u'.', 3540), (u'I', 3384), (u'RT', 2875), (u'to', 2084), (u'the', 1995), (u'you', 1977), (u',', 1885), (u'http', 1778), (u'a', 1631), (u'!', 1402)]

With the exception of the punctuation, "RT", and "http", those are all function words: pronouns, articles, etc. Arguably, within the context of Twitter, RT and http *are* function words. For a larger sample size, both of tweets and for `Collection.most_common`, we can compare linguistic tendencies far more cheaply than using a part of speech tagger.

### Graphing and d3.js

[d3.js](http://d3js.org/) is a JavaScript library for making super-awesome graphs and visualizations, like Highcharts but more freeform. I'll walk you through making a simple visualization to display the size of our dataset by region. Who tweets more, Brazil or Indonesia?

#### HTML

In our HTML, we'll just create a div that our d3.js code will insert its wizardry into.

    <div id="map"></div>

We'll also want to, in some fashion, require these JavaScript dependencies:

* d3.v3.min.js : The library itself
* queue.v1.min.js : helper for retrieving resources the map will need, like place names.
* topojson.js : library for using TopoJSONs, an extension of GeoJSON

#### JavaScript

First, let's set up our projection of the world.

  // our world map and its dimensions / scale
  var projection = d3.geo.mercator()
                  .translate([480, 300])
                  .scale(970);

  // object for handling series of coordinates
  var path = d3.geo.path()
      .projection(projection);

Now, let's add an SVG, which will contain our map and our tooltips, to the DOM.

  // mapping our map to the #map DOM element
  var svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height);

  // set up our tooltips
  var tooltip = d3.select("#map").append("div")
      .attr("class", "tooltip");

#### Queue

Queue delays rendering the map until everything you need is present. By specifying a resource type and a URL for the resource, you can grab both static and dynamic assets. Here, I grab the TopoJSON for our world, a TSV of country names, and the results of a query to Cloudant. d3.js handles it all the same way.

  // load our resources in order
  queue()
      // topojson of the world
      .defer(d3.json, "static/maps/world-110m.json")
      // TSV of nation names and their IDs
      .defer(d3.tsv, "static/maps/world-country-names.tsv")
      // as long as it's json, you can grab dynamic content too :O
      .defer(d3.json, "view/geo?group_level=1&stale=ok")
      .await(ready);

#### Ready

Once everything's ready, it calls `ready`, which is where most of the work happens:

    function ready(error, world, names, counts_rows) {
        ...
    }

Ready receives the results of `queue` in the order they were entered, though any error comes first.

#### Data

d3.js calls itself "data-driven documents." Much of the presentation logic is precisely this: taking an array of objects, and styling the SVG or parts of it accordingly. For example:

    var country = svg.selectAll(".country").data(countries);

    country
      .enter()
      .insert("path")
      .attr("class", "country")    
      .attr("title", function(d,i) { return d.name; })
      .attr("d", path)
      .style("fill", function(d, i) { 
        return color(d.count); 
      })

The data that goes into all that? It comes from the `countries` object we attach using the `data` method. In order to get more data into the our documents, well, just attach it to `countries` -- which we do.

    // attach counts to their respective countries
    countries.forEach(function(d) { 
      var filtered_names = names.filter(function(n) { return d.id == n.id; });
      if(filtered_names.length) d.name = filtered_names[0].name;

      if(counts[d.name]) {
        d.count = counts[d.name];
      }
    });

#### Color Scales

Color gradients in d3.js arrive from the concept of a scale. For example, here's the color scale for our map:

    var color = d3.scale.log().domain([1, most]).range(['black', 'blue']);

It's a logarithmic scale that maps values between 1 and whatever the highest number of tweets in a single country is to a color between black and blue. Values like `undefined` become gray by default, visually separating them from countries with tweets.

#### Final result

Turns out, Indonesia tweets more. I don't know why, but we have the tools to investigate.

### Wrapping up

This was my first ever conference talk. Thanks for coming, guys. I hope it was sufferable. Here's what we talked about:

* Language is complicated.
* Gathering data from Twitter is painless.
* ... but NLTK performance becomes an issue quickly.
* d3.js makes pretty graphs easy.

### Questions?

If y'all have questions, I'm available for another [x] minutes, or feel free to hit me up afterwards, in person or on the interwebs. Here's my contact info: []

Thanks again!