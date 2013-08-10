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

Indeed, I found three things:

* Different parts of speech evolve together, proportionally or inversely.
* Different parts of speech react to different events, such as war or shared cultural events like the televised Apollo 11 mission, which 93% of homes witnessed.
* Language style was evolving more slowly over time until 2008, when the Great Recession hits and various parts of speech went wonky.

I got lucky with that research, since Google updated the dataset in 2012 with data about parts of speech and other grammatical structures.