import json
import sys, logging

from flask import Flask, render_template, url_for, request, Request
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
@app.route('/display/<corp_id>', methods=['GET'])
def display(corp_id):

    # -------------------------------------------
    # A) Get the current page.
    # -------------------------------------------
    cur_page = request.args.get('page')
    YGG_LOG.critical(cur_page)
    if not cur_page.strip():
        cur_page = 1
    else:
        cur_page = int(cur_page)

    # -------------------------------------------
    # B) If we have a page, try to request a subset
    #    of the available igt instances.
    # -------------------------------------------

    xc = dbi.get_corpus(corp_id)
    xc.__class__ = RGCorpus
    xc._finish_load()


    # -------------------------------------------
    # B) Get the number of pages.
    # -------------------------------------------
    num_instances = len(xc.igts)
    num_pages = int(num_instances/10)
    page_list = range(1,num_pages+2)

    # -------------------------------------------
    # C) Now, get the subset of igt instances.
    # -------------------------------------------
    xc.igts = xc.igts[(cur_page-1)*10:cur_page*10]


    return render_template('element.html', xigt=xc, page_list=page_list, cur_page=cur_page, corp_id=corp_id)



@app.route('/query')
def query():
    return render_template('query.html')



# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)