import flask
import requests
import os
from config import Config

app = flask.Flask(__name__)

@app.route('/view/<name>')
def view(name):
    url = Config.db_url + '/_design/nltk/_view/' + name
    r = requests.get(url, params=flask.request.values)
    return flask.jsonify(r.json())

@app.route('/count')
def count():
  url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
  r = requests.get(url)
  return flask.jsonify({"count": r.json()['total_rows']})

@app.route('/')
def index():
    url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
    r = requests.get(url)
    count = r.json()['total_rows']
    return flask.render_template('index.html', count=count)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(port=port)