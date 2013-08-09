import flask
import requests
import os
from config import Config

app = flask.Flask(__name__)

@app.route('/count')
def count():
  url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
  r = requests.get(url)
  return flask.jsonify({"count": r.json()['total_rows']})

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
	app.run(port=int(os.environ.get('PORT', 5000)))