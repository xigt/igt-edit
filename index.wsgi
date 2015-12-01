import json
import sys, logging

from flask import Flask, render_template, url_for
import sleipnir



app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(sleipnir.blueprint)

application = app

sys.path.append(app.config.get('INTENT_LIB'))
sys.path.append(app.config.get('XIGT_LIB'))

# -------------------------------------------
# Import intent stuff here.
from intent.igt.rgxigt import RGCorpus
from intent.igt.igtutils import rgp, rgencode

app.debug = True

# -------------------------------------------
# Set up logging.
YGG_LOG = logging.getLogger('YGG')

# -------------------------------------------
# 1) Import the version of the sleipnir dbi we wish to use, so
#    that we can call it directly.
from sleipnir.interfaces import filesystem as dbi

# -------------------------------------------
# The default route.
@app.route('/')
def main():
    corpora_json = json.loads(dbi.corpora().data.decode('utf-8'))
    # YGG_LOG.critical(corpora_json)
    corpora = sorted(corpora_json.get('corpora'), key=lambda x: x.get('name'))
    return render_template('browser.html', corpora=corpora)

# -------------------------------------------
# For displaying the corpus...
@app.route('/display/<corp_id>')
def display(corp_id):
    xc = dbi.get_corpus(corp_id)
    xc.__class__ = RGCorpus
    xc._finish_load()

    return render_template('element.html', xigt=xc)



@app.route('/query')
def query():
    return render_template('query.html')



# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)