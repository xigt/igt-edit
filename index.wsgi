import json
import sys, logging

from flask import Flask, render_template, url_for, request

from xigt.codecs import xigtjson

import sleipnir



app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(sleipnir.blueprint)

application = app

sys.path.append(app.config.get('INTENT_LIB'))
sys.path.append(app.config.get('XIGT_LIB'))

# -------------------------------------------
# Import intent stuff here.
from intent.igt.rgxigt import RGCorpus, RGIgt, GlossLangAlignException
from intent.igt.igtutils import clean_lang_string, clean_gloss_string, clean_trans_string, \
    strip_leading_whitespace, rgencode

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
    corpora = sorted(corpora_json.get('corpora'), key=lambda x: x.get('name'))

    return render_template('browser.html', corpora=corpora)

# -------------------------------------------
# For populating the IGT list
# -------------------------------------------
@app.route('/populate/<corp_id>')
def populate(corp_id):
    xc = dbi.get_corpus(corp_id)
    return render_template('igt_list.html', igts=xc, corp_id=corp_id)

# -------------------------------------------
# For displaying the corpus...
@app.route('/display/<corp_id>/<igt_id>', methods=['GET'])
def display(corp_id, igt_id):

    xc = dbi.get_igts(corp_id, igt_ids=[igt_id])
    xc.__class__ = RGCorpus
    xc._finish_load()

    return render_template('element.html', xigt=xc, corp_id=corp_id)


# -------------------------------------------
# For returning the normalized tier...
@app.route('/normalize/<corp_id>/<igt_id>', methods=['POST'])
def normalize(corp_id, igt_id):

    # Get the data...
    lines = json.loads(request.data.decode('utf-8'))



    for i, line in enumerate(lines):
        if 'L' in line.get('tag'):
            lines[i]['text'] = clean_lang_string(lines[i]['text'])
        elif 'G' in line.get('tag'):
            lines[i]['text'] = clean_gloss_string(lines[i]['text'])
        elif 'T' in line.get('tag'):
            lines[i]['text'] = clean_trans_string(lines[i]['text'])

        lines[i]['num'] = i+1

    textlines = strip_leading_whitespace([l.get('text') for l in lines])

    for i, line in enumerate(lines):
        lines[i]['text'] = textlines[i]


    return render_template('normalized_tier.html', lines=lines)

# -------------------------------------------
# For returning the INTENT-generated additional tiers...
@app.route('/intentify/<corp_id>/<igt_id>', methods=['POST'])
def intentify(corp_id, igt_id):

    data = json.loads(request.data.decode('utf-8'))

    inst = RGIgt(id=igt_id)
    inst.add_raw_tier(data.get('raw'))
    inst.add_clean_tier(data.get('clean'))
    inst.add_normal_tier(data.get('normal'))

    try:
        inst.basic_processing()
    except GlossLangAlignException as glae:
        return 'Gloss and language lines do not align 1-to-1'
    else:
        inst.classify_gloss_pos()
        xc = RGCorpus(id='xc1')
        xc.append(inst)
        return xigtjson.dumps(xc)

# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)