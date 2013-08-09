import flask
import requests
import os
from listen import listen
from config import Config
from multiprocessing import Process

app = flask.Flask(__name__)

# spawn the listener as a process so it doesn't block our server
p = Process(target=listen)
p.start()

@app.route('/count')
def count():
  url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
  r = requests.get(url)
  return flask.jsonify({"count": r.json()['total_rows']})

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
	app.run(port=os.environ.get('PORT', 5000))