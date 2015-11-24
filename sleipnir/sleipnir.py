import json
import os, sys

# -------------------------------------------
# Set up the basic flask stuff...
# -------------------------------------------
from flask import Flask, request, render_template

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.debug = True
app.config.from_pyfile('../config.py')

# -------------------------------------------
# Do the imports of XIGT and INTENT
# -------------------------------------------
sys.path.append(app.config.get('INTENT_LIB'))
sys.path.append(app.config.get('XIGT_LIB'))

from intent.igt.rgxigt import RGCorpus
from xigt.codecs import xigtjson

# -------------------------------------------
# DOCID
# -------------------------------------------

@app.route('/doc/<docid>')
def retrieve_docid(docid):
    return str(docid)

# -------------------------------------------
# LANGID
# -------------------------------------------

@app.route('/iso/<string:langid>')
def retrieve_langid(langid):
    return str(langid)

# -------------------------------------------
# FILENAME
# -------------------------------------------

@app.route('/file/<path:filename>')
def retrieve_filename(filename):
    realpath = os.path.join(app.config['XIGT_DIR'], filename)
    if os.path.exists(realpath):
        xc = RGCorpus.load(realpath)

        # -------------------------------------------
        # Set up the page size...
        page_size = 10

        page = int(request.args.get('page', '0'))

        num_pages = int(len(xc.igts)/page_size)+1
        page_list = range(num_pages)

        xc.igts = xc.igts[page*page_size:(page+1)*page_size]


        # Do the conversion to json...
        xigt_json = json.loads(xigtjson.dumps(xc))

        # -------------------------------------------
        # Build the return params
        params = {'cur_page':page,
                  'filename':filename,
                  'num_pages':num_pages,
                  'page_list':page_list,
                  'xigt':xigt_json}

        return render_template('element.html', **params)
    else:
        return page_not_found(filename)

@app.errorhandler(404)
def page_not_found(e):
    return 'Path "{}" not found.'.format(e)