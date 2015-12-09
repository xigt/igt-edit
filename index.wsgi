import json, sys, logging, os

# -------------------------------------------
# Set up the Flask app
# -------------------------------------------
import sqlite3
from flask import Flask, render_template, url_for, request, g



app = Flask(__name__)
application = app

# -------------------------------------------
# Import the configuration.
# -------------------------------------------
sys.path.append(os.path.dirname(__file__))
from yggdrasil.config import USER_DB, INTENT_LIB, XIGT_LIB, SLEIPNIR_LIB
from yggdrasil.users import get_rating, set_rating


sys.path.append(INTENT_LIB)
sys.path.append(XIGT_LIB)
sys.path.append(SLEIPNIR_LIB)

# -------------------------------------------
# Now that we've imported our dependencies,
# we can register the blueprint.
# -------------------------------------------
import sleipnir
app.register_blueprint(sleipnir.blueprint)

# -------------------------------------------
# Import other stuff here.
# -------------------------------------------



from xigt.codecs import xigtjson
from intent.igt.rgxigt import RGCorpus, RGIgt, GlossLangAlignException, retrieve_normal_line
from intent.igt.consts import ODIN_LANG_TAG, ODIN_GLOSS_TAG
from intent.igt.igtutils import clean_lang_string, clean_gloss_string, clean_trans_string, \
    strip_leading_whitespace, is_strict_columnar_alignment

app.debug = True

# -------------------------------------------
# Set up logging.
# -------------------------------------------
YGG_LOG = logging.getLogger('YGG')


# -------------------------------------------
# The default route. Display the browser window
# to the user.
# -------------------------------------------
@app.route('/')
def main():
    corpora_json = json.loads(sleipnir.dbi.corpora().data.decode('utf-8'))
    corpora = sorted(corpora_json.get('corpora'), key=lambda x: x.get('name'))

    return render_template('browser.html', corpora=corpora)

# -------------------------------------------
# When a user clicks a "corpus", display the
# IGT instances contained by that corpus below.
# -------------------------------------------
@app.route('/populate/<corp_id>')
def populate(corp_id):
    xc = sleipnir.dbi.get_corpus(corp_id)
    ratings = {igt_id: get_rating(1, corp_id, igt_id) for igt_id in [inst.id for inst in xc]}
    nexts = {}
    for i, igt in enumerate(xc):
        if i < len(xc)-1:
            nexts[igt.id] = xc[i+1].id
        else:
            nexts[igt.id] = None

    return render_template('igt_list.html', igts=xc, corp_id=corp_id, ratings=ratings, nexts=nexts)

# -------------------------------------------
# When a user clicks an IGT instance, display
# the instances and the editor portions in the
# main display panel.
# -------------------------------------------
@app.route('/display/<corp_id>/<igt_id>', methods=['GET'])
def display(corp_id, igt_id):

    xc = sleipnir.dbi.get_igts(corp_id, igt_ids=[igt_id])
    xc.__class__ = RGCorpus
    xc._finish_load()

    # Type hinting
    inst = xc[0]
    assert isinstance(inst, RGIgt)

    content = render_template('element.html', xigt=xc, igt_id=igt_id, corp_id=corp_id);

    return json.dumps({"content":content})


# -------------------------------------------
# After the user has corrected the clean tier
# as necessary, auto-generate the normalized
# tier.
# -------------------------------------------
@app.route('/normalize/<corp_id>/<igt_id>', methods=['POST'])
def normalize(corp_id, igt_id):

    # Get the data...
    data = request.get_json()
    lines = data.get('lines')

    for i, line in enumerate(lines):
        if 'L' in line.get('tag'):
            lines[i]['text'] = clean_lang_string(lines[i]['text'])
        elif 'G' in line.get('tag'):
            lines[i]['text'] = clean_gloss_string(lines[i]['text'])
        elif 'T' in line.get('tag'):
            lines[i]['text'] = clean_trans_string(lines[i]['text'])

        lines[i]['num'] = i+1

    # After the cleaning, proceed through the instances and smartly
    # remove whitespace (i.e. the smallest amount of leading whitespace
    # shared by all lines)
    textlines = strip_leading_whitespace([l.get('text') for l in lines])

    for i, line in enumerate(lines):
        lines[i]['text'] = textlines[i]

    set_state(1, corp_id, igt_id, NORM_STATE)

    retdata = {"content":render_template('normalized_tier.html', lines=lines)}

    return json.dumps(retdata)


# -------------------------------------------
# After the user has corrected the normalized tiers,
# analyze them and provide feedback.
# -------------------------------------------
@app.route('/intentify/<corp_id>/<igt_id>', methods=['POST'])
def intentify(corp_id, igt_id):

    data = request.get_json()

    inst = RGIgt(id=igt_id)
    inst.add_raw_tier(data.get('raw'))
    inst.add_clean_tier(data.get('clean'))
    inst.add_normal_tier(data.get('normal'))

    feedback = {}

    # Check that the language line and gloss line
    # have the same number of whitespace-delineated tokens.
    feedback['glw'] = 1 if len(inst.lang) == len(inst.gloss) else 0

    # Check that the language line and gloss line
    # have the same number of morphemes.
    feedback['glm'] = 1 if len(inst.morphemes) == len(inst.glosses) else 0

    # Check that the normalized tier has only L, G, T for tags.
    norm_tags = set([l.attributes.get('tag') for l in inst.normal_tier()])
    feedback['tag'] = 1 if set(['L','G','T']) == norm_tags else 0

    # Check that the g/l lines are aligned in strict columns
    lang_line  = retrieve_normal_line(inst, ODIN_LANG_TAG)
    gloss_line = retrieve_normal_line(inst, ODIN_GLOSS_TAG)
    if lang_line is None or gloss_line is None:
        feedback['col'] = 0
    else:
        feedback['col'] = 1 if is_strict_columnar_alignment(lang_line.value(), gloss_line.value()) else 0

    return json.dumps(feedback)


# -------------------------------------------
# Save a file after changes
# -------------------------------------------
@app.route('/save/<corp_id>/<igt_id>', methods=['PUT'])
def save(corp_id, igt_id):
    data = request.get_json()
    rating = data.get('rating')

    set_rating(1, corp_id, igt_id, rating)
    return str(get_rating(1, corp_id, igt_id))



# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)