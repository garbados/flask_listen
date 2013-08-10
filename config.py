import os

class Config(object):
  # Go to http://dev.twitter.com and create an app.
  # The consumer key and secret will be generated for you after
  consumer_key = os.environ['TWITTER_CONSUMER_KEY']
  consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']

  # After the step above, you will be redirected to your app's page.
  # Create an access token under the the "Your access token" section
  access_token = os.environ['TWITTER_ACCESS_KEY']
  access_token_secret = os.environ['TWITTER_ACCESS_SECRET']

  # Database credentials
  db_url = "https://{user}:{pass}@{user}.cloudant.com/{db}".format(**{
    "user": os.environ['CLOUDANT_USER'],
    "pass": os.environ['CLOUDANT_PASS'],
    "db": os.environ['CLOUDANT_DB']
    })

  geo_url = "http://api.geonames.org/countrySubdivisionJSON"
  geo_user = "garbados"