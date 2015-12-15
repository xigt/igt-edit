import json, sys, logging, os

# -------------------------------------------
# Set up the Flask app
# -------------------------------------------
from flask import Flask, render_template, url_for, request, g

app = Flask(__name__)
application = app

# -------------------------------------------
# Import the configuration.
# -------------------------------------------
sys.path.append(os.path.dirname(__file__))
from yggdrasil import config
from yggdrasil.config import USER_DB, INTENT_LIB, XIGT_LIB, SLEIPNIR_LIB, LINE_TAGS, LINE_ATTRS
from yggdrasil.consts import NORM_STATE, CLEAN_STATE, RAW_STATE, NORMAL_TABLE_TYPE, CLEAN_TABLE_TYPE
from yggdrasil.users import get_rating, set_rating, set_state

sys.path.append(INTENT_LIB)
sys.path.append(XIGT_LIB)
sys.path.append(SLEIPNIR_LIB)

# -------------------------------------------
# Add the configuration to the app config
# -------------------------------------------
app.config.from_object(config)

# -------------------------------------------
# Now that we've imported our dependencies,
# we can register the blueprint.
# -------------------------------------------
from sleipnir import dbi

# -------------------------------------------
# Import other stuff here.
# -------------------------------------------



from intent.igt.rgxigt import RGCorpus, RGIgt, retrieve_normal_line
from intent.igt.xigt_manipulations import get_clean_tier, get_normal_tier, get_raw_tier, replace_lines
from intent.igt.consts import ODIN_LANG_TAG, ODIN_GLOSS_TAG, CLEAN_ID, NORM_ID
from intent.igt.igtutils import is_strict_columnar_alignment, rgencode
from intent.igt.search import raw_tier, cleaned_tier, normalized_tier

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
    return render_template('login_screen.html', try_again=False)

# -------------------------------------------
# Retrieve the specific user.
# -------------------------------------------
@app.route('/user/<userid>')
def get_user(userid):
    user_corpora = get_user_corpora(userid)
    if user_corpora is not None:
        all_corpora  = dbi.list_corpora()

        filtered_corpora = [c for c in all_corpora if c.get('id') in user_corpora]

        sorted_corpora = sorted(filtered_corpora,
                                key=lambda x: x.get('name'))
        return render_template('browser.html', corpora=sorted_corpora)
    else:
        return render_template('login_screen.html', try_again=True)


# -------------------------------------------
# When a user clicks a "corpus", display the
# IGT instances contained by that corpus below.
# -------------------------------------------
@app.route('/populate/<corp_id>')
def populate(corp_id):
    xc = dbi.get_corpus(corp_id)
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

    # -------------------------------------------
    # Start by getting the IGT instance.
    # -------------------------------------------
    inst = dbi.get_igt(corp_id, igt_id)

    # -------------------------------------------
    # Now, get the raw tier, and see if there's a clean tier.
    # -------------------------------------------
    rt = raw_tier(inst)
    ct = cleaned_tier(inst)

    # -------------------------------------------
    # Check to see if we already have a clean tier
    # or normalized tier. If so, display them.
    # -------------------------------------------
    state = RAW_STATE
    if ct is not None:
        state = CLEAN_STATE
    else:
        ct = get_clean_tier(inst, merge=True)

    nt = normalized_tier(inst)
    nt_content = None
    if nt is not None:
        state = NORM_STATE
        nt_content = render_template("tier_table.html", tier=nt, table_type=NORMAL_TABLE_TYPE, id_prefix=NORM_ID, editable=True)

    # -------------------------------------------
    # Render the element template.
    # -------------------------------------------
    content = render_template('element.html', state=state, rt=rt, ct=ct, nt_content=nt_content, igt=inst, igt_id=igt_id, corp_id=corp_id)

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

    i = dbi.get_igt(corp_id, igt_id)
    nt = get_normal_tier(i, force_generate=True)

    content = render_template("tier_table.html", tier=nt, table_type=NORMAL_TABLE_TYPE, id_prefix=NORM_ID, editable=True)

    retdata = {"content":content}

    return json.dumps(retdata)

def tagfunc(tagstr):
    tags = tagstr.split('+')
    maintag = tags[0]
    r = {'maintag':maintag, 'attrs':[]}
    for elt in tags[1:]:
        r['attrs'].append(elt)
    return r

# -------------------------------------------
# Generate a cleaned tier
# -------------------------------------------
@app.route('/clean/<corp_id>/<igt_id>', methods=['GET'])
def clean(corp_id, igt_id):

    inst = dbi.get_igt(corp_id, igt_id)
    return render_template("tier_table.html",
                           table_type=CLEAN_TABLE_TYPE,
                           tier=get_clean_tier(inst, force_generate=True),
                           id_prefix=CLEAN_ID,
                           editable=True,
                           tag_options=LINE_TAGS,
                           label_options=LINE_ATTRS,
                           tagfunc=tagfunc)


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

    # -------------------------------------------
    # Get the lines
    # -------------------------------------------
    clean = data.get('clean')
    norm  = data.get('norm')

    # Set the rating...
    set_rating(1, corp_id, igt_id, rating)

    # Retrieve the IGT instance, and swap in the
    # new cleaned and normalized tiers.
    igt = dbi.get_igt(corp_id, igt_id)
    igt = replace_lines(igt, clean, norm)

    # Do the actually saving of the igt instance.
    dbi.set_igt(corp_id, igt_id, igt)

    return str(get_rating(1, corp_id, igt_id))

# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)