#!/usr/bin/env python3.4

import sys, os
import logging
import urllib
from io import StringIO
from tempfile import NamedTemporaryFile
from flask import Flask, render_template, url_for, request, Response



sys.path.insert(0, os.path.dirname(__file__))
from config import *

# -------------------------------------------
# Import INTENT and XIGT
# -------------------------------------------
sys.path.insert(0, INTENT_DIR)
sys.path.insert(0, XIGT_DIR)

from intent.igt.igtutils import rgencode
from intent.utils.argpasser import ArgPasser
from intent.commands.enrich import enrich
from intent.igt.parsing import raw_txt_to_xc
from intent.consts import *

app = Flask(__name__, template_folder='templates', static_folder='static')

application = app

@app.route('/')
def hello():
    return render_template('index.html')


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
        kwargs[ALN_VAR].append(ARG_ALN_GIZA)
    if 'align_heur' in request.form.keys():
        kwargs[ALN_VAR].append(ARG_ALN_HEUR)
    if 'pos_proj' in request.form.keys():
        kwargs[POS_VAR].append(ARG_POS_PROJ)
    if 'pos_class' in request.form.keys():
        kwargs[POS_VAR].append(ARG_POS_CLASS)
    if 'parse_proj' in request.form.keys():
        kwargs[PARSE_VAR].append(ARG_PARSE_PROJ)
    if 'parse_trans' in request.form.keys():
        kwargs[PARSE_VAR].append(ARG_PARSE_TRANS)

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
        xc = raw_txt_to_xc(request.form['text'])
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
