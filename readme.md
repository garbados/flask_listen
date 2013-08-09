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