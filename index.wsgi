import json, sys, logging, os

# -------------------------------------------
# Set up the Flask app
# -------------------------------------------
from flask import Flask, render_template, url_for, request, g, make_response

app = Flask(__name__)
application = app

# -------------------------------------------
# Import the configuration.
# -------------------------------------------
sys.path.append(os.path.dirname(__file__))
from yggdrasil import config
from yggdrasil.config import INTENT_LIB, XIGT_LIB, SLEIPNIR_LIB, LINE_TAGS, LINE_ATTRS
from yggdrasil.consts import NORM_STATE, CLEAN_STATE, RAW_STATE, NORMAL_TABLE_TYPE, CLEAN_TABLE_TYPE, EDITOR_DATA_SRC, \
    EDITOR_METADATA_TYPE

sys.path.append(INTENT_LIB)
sys.path.append(XIGT_LIB)
sys.path.append(SLEIPNIR_LIB)

from yggdrasil.metadata import get_rating, set_rating, set_comment
from yggdrasil.users import get_user_corpora, get_state, set_state

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


from intent.igt.metadata import set_meta_attr
from intent.igt.rgxigt import RGIgt, retrieve_normal_line, retrieve_lang_words, retrieve_gloss_words, \
    retrieve_trans_words, find_lang_word, x_contains_y
from intent.igt.creation import get_clean_tier, get_normal_tier, get_raw_tier, replace_lines
from intent.igt.consts import ODIN_LANG_TAG, ODIN_GLOSS_TAG, CLEAN_ID, NORM_ID, DATA_PROV, DATA_SRC
from intent.igt.igtutils import is_strict_columnar_alignment
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
        return render_template('browser.html', corpora=sorted_corpora, user_id=userid)
    else:
        return render_template('login_screen.html', try_again=True)


# -------------------------------------------
# When a user clicks a "corpus", display the
# IGT instances contained by that corpus below.
# -------------------------------------------
@app.route('/populate/<corp_id>')
def populate(corp_id):
    xc = dbi.get_corpus(corp_id)
    ratings = {inst.id: get_rating(inst) for inst in xc}
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
    # Get the state from the user file.
    # -------------------------------------------
    state = get_state(request.args.get('user'), corp_id, igt_id)
    if state is None:
        state = RAW_STATE

    rt = raw_tier(inst)
    ct, nt = None, None
    if state >= CLEAN_STATE:
        ct = cleaned_tier(inst)

    if state == NORM_STATE:
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
    clean_lines = data.get('lines')

    # Retrieve the original IGT from the database
    # and swap out the new clean lines for the old
    # clean lines, then generate a new normalized
    # tier based on that.
    i = dbi.get_igt(corp_id, igt_id)
    replace_lines(i, clean_lines, None)
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

    response = {}

    # Check that the language line and gloss line
    # have the same number of whitespace-delineated tokens.
    response['glw'] = 1 if len(inst.lang) == len(inst.gloss) else 0

    # Check that the language line and gloss line
    # have the same number of morphemes.
    response['glm'] = 1 if len(inst.morphemes) == len(inst.glosses) else 0

    # Check that the normalized tier has only L, G, T for tags.
    norm_tags = set([l.attributes.get('tag') for l in inst.normal_tier()])
    response['tag'] = 1 if set(['L','G','T']) == norm_tags else 0

    # Check that the g/l lines are aligned in strict columns
    lang_line  = retrieve_normal_line(inst, ODIN_LANG_TAG)
    gloss_line = retrieve_normal_line(inst, ODIN_GLOSS_TAG)
    if lang_line is None or gloss_line is None:
        response['col'] = 0
    else:
        response['col'] = 1 if is_strict_columnar_alignment(lang_line.value(), gloss_line.value()) else 0

    # figure out how many columns we're going to need to number.
    col_nums = range(1, max(len(inst.lang), len(inst.gloss), len(inst.trans))+1)


    lws = retrieve_lang_words(inst)
    gws = retrieve_gloss_words(inst)
    tw = retrieve_trans_words(inst)

    lms = inst.morphemes
    gms = inst.glosses

    lang_list = []
    for lw in lws:
        pairs = (lw, [])
        for lm in lms:
            if x_contains_y(inst, lw, lm):
                pairs[1].append(lm)
        lang_list.append(pairs)

    gloss_list = []
    for gw in gws:
        pairs = (gw, [])
        for gm in gms:
            if x_contains_y(inst, gw, gm):
                pairs[1].append(gm)
        gloss_list.append(pairs)


    response['words'] = render_template('group_2.html',
                                        col_nums=col_nums,
                                        lang=lang_list,
                                        gloss=gloss_list,
                                        trans=tw,
                                        aln=inst.heur_align())
    return json.dumps(response)


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
    user_id = data.get('userID')
    comment = data.get('comment', '')

    # Set the rating...
    if norm:
        set_state(user_id, corp_id, igt_id, NORM_STATE)
    elif clean:
        set_state(user_id, corp_id, igt_id, CLEAN_STATE)
    else:
        set_state(user_id, corp_id, igt_id, RAW_STATE)



    # Retrieve the IGT instance, and swap in the
    # new cleaned and normalized tiers.
    igt = dbi.get_igt(corp_id, igt_id)
    igt = replace_lines(igt, clean, norm)
    set_rating(igt, user_id, rating)

    # Only add the comment if it is contentful.
    if comment.strip():
        set_comment(igt, user_id, comment)


    # Add the data provenance to the tier.
    ct = cleaned_tier(igt)
    nt = normalized_tier(igt)
    for t in [ct, nt]:
        if t is not None:
            set_meta_attr(t, DATA_PROV, DATA_SRC, EDITOR_DATA_SRC, metadata_type=EDITOR_METADATA_TYPE)

    # Do the actually saving of the igt instance.
    dbi.set_igt(corp_id, igt_id, igt)

    return make_response()

# -------------------------------------------
# Static files

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)