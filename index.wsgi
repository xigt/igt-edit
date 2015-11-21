#!/usr/bin/env python3.4


# -------------------------------------------
# Set up flask basics...
# -------------------------------------------
from flask import Flask, render_template, url_for, request, Response
app = Flask(__name__, template_folder='templates', static_folder='static')
application = app

# -------------------------------------------
# Read in the config file...
# -------------------------------------------
app.config.from_pyfile('config.py')

if app.config.get('DEBUG'):
    app.debug = True

# -------------------------------------------

import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/')
sys.path.append('/Users/rgeorgi/Documents/code/dissertation')
sys.path.append('/Users/rgeorgi/Documents/code/xigt')

# -------------------------------------------

import logging
import os
import urllib
from io import StringIO
from tempfile import NamedTemporaryFile


from werkzeug.utils import secure_filename

from intent.igt.igtutils import rgp, rgencode
from intent.igt.rgxigt import RGCorpus
from intent.scripts.conversion.text_to_xigt import text_to_xigtxml
from intent.subcommands import enrich
from intent.utils.arg_consts import ALN_VAR, ALN_GIZA, ALN_HEUR, POS_VAR, POS_LANG_PROJ, POS_LANG_CLASS, PARSE_VAR, \
    PARSE_LANG_PROJ, PARSE_TRANS
from intent.utils.argpasser import ArgPasser



@app.route('/')
def hello():
    return render_template('browser.html', filelist=os.listdir(app.config.get('XIGT_DIR')))

# -------------------------------------------
# Browse to the
@app.route('/browse/<path:filename>')
def browse(filename):
    path = os.path.join(app.config['XIGT_DIR'], filename)
    xc = RGCorpus.load(path)
    return render_template('element.html', igts=xc.igts)

@app.route('/enrich', methods=['POST'])
def process_file():

    kwargs = ArgPasser()

    # -------------------------------------------
    # 1) Grab the uploaded file.
    f = request.files['infile']
    content = f.read().decode('utf-8')

    # -------------------------------------------
    # Add logging to a string to put in the header.
    root = logging.getLogger()
    s = StringIO()
    root.addHandler(logging.StreamHandler(s))

    # -------------------------------------------
    # Build the arguments...
    kwargs[ALN_VAR] = []
    kwargs[POS_VAR] = []
    kwargs[PARSE_VAR] = []

    if 'align_giza' in request.form.keys():
        kwargs[ALN_VAR].append(ALN_GIZA)
    if 'align_heur' in request.form.keys():
        kwargs[ALN_VAR].append(ALN_HEUR)
    if 'pos_proj' in request.form.keys():
        kwargs[POS_VAR].append(POS_LANG_PROJ)
    if 'pos_class' in request.form.keys():
        kwargs[POS_VAR].append(POS_LANG_CLASS)
    if 'parse_proj' in request.form.keys():
        kwargs[PARSE_VAR].extend([PARSE_TRANS, PARSE_LANG_PROJ])
    if 'parse_trans' in request.form.keys():
        kwargs[PARSE_VAR].append(PARSE_TRANS)

    if 'verbose' in request.form.keys():
        root.setLevel(logging.DEBUG)



    # -------------------------------------------
    # 1) Re-save it to a secure, temporary file.
    in_temp = NamedTemporaryFile(mode='w', encoding='utf-8')
    in_temp.write(content)
    in_temp.flush()


    out_temp = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    out_temp.close()
    # -------------------------------------------
    # 2) Now, load it and do the requested processing.

    r = Response()

    try:
        enrich(IN_FILE=in_temp.name, OUT_FILE=out_temp.name, **kwargs)
    except Exception as e:
        r.headers['Exit-Code'] = 1
        root.error(e)
    else:
        r.headers['Exit-Code'] = 0
        f = open(out_temp.name, 'r', encoding='utf-8')
        r.data = f.read()

    r.headers['Stdout'] = urllib.parse.quote(s.getvalue())

    return r


# -------------------------------------------
# Convert the raw text
@app.route('/text', methods=['POST'])
def convert_text():
    # -------------------------------------------
    # Add logging to a string to put in the header.
    root = logging.getLogger()
    s = StringIO()
    root.addHandler(logging.StreamHandler(s))

    r = Response()
    # root.log(1000, "This is a test")
    try:
        xc = RGCorpus.from_raw_txt(request.form['text'])
    except Exception as e:
        r.headers['Exit-Code'] = 1
        root.error(e)
    else:
        r.headers['Exit-Code'] = 0
        r.data = rgencode(xc)

    r.headers['Stdout'] = urllib.parse.quote(s.getvalue())

    return r


# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
