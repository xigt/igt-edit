import os

from flask import Flask, json

app = Flask(__name__)
app.debug = True
app.config.from_pyfile('../config.py')

@app.route('/')
def lister():
    return 'test'

@app.route('/langs')
def langs():
    return json.dumps(['bul', 'deu'])

@app.route('/files')
def files():
    return json.dumps(os.listdir(app.config.get('XIGT_DIR')))