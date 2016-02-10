import json
import logging
import os
import sys

# -------------------------------------------
# Set up the Flask app
# -------------------------------------------
from flask import Flask, render_template, url_for, request, make_response

app = Flask(__name__)
application = app

# -------------------------------------------
# Import the configuration.
# -------------------------------------------
sys.path.append(os.path.dirname(__file__))
from yggdrasil import config
from yggdrasil.config import INTENT_LIB, XIGT_LIB, SLEIPNIR_LIB, LINE_TAGS, LINE_ATTRS, ODIN_UTILS, XIGTVIZ
from yggdrasil.consts import NORM_STATE, CLEAN_STATE, RAW_STATE, NORMAL_TABLE_TYPE, CLEAN_TABLE_TYPE, EDITOR_DATA_SRC, \
    EDITOR_METADATA_TYPE, HIDDEN

sys.path.append(INTENT_LIB)
sys.path.append(XIGT_LIB)
sys.path.append(SLEIPNIR_LIB)
sys.path.append(ODIN_UTILS)

from yggdrasil.metadata import get_rating, set_rating, set_comment
from yggdrasil.users import get_user_corpora, get_state, set_state
from yggdrasil.igt_operations import replace_lines, add_editor_metadata, add_split_metadata, add_raw_tier, \
    add_clean_tier, add_normal_tier

from odinclean import add_cleaned_tier
from odinnormalize import add_normalized_tier

from xigt import Igt
from xigt.codecs import xigtjson

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

from intent.consts import CLEAN_ID, NORM_ID
from intent.igt.igtutils import is_strict_columnar_alignment
from intent.igt.create_tiers import lang_lines, gloss_line, trans_lines, \
    generate_lang_words, generate_gloss_glosses, generate_trans_words, lang, gloss, morphemes, glosses, trans
from intent.igt.igt_functions import x_contains_y, copy_xigt, delete_tier, heur_align_inst, classify_gloss_pos, \
    tag_trans_pos, project_gloss_pos_to_lang
from intent.igt.references import raw_tier, cleaned_tier, normalized_tier
from intent.igt.exceptions import NoNormLineException, NoGlossLineException, GlossLangAlignException

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

        xigtviz_conf = os.path.join(XIGTVIZ, 'config.json')
        with open(xigtviz_conf) as f:
            xigtviz_settings = json.loads(f.read())


        return render_template('browser.html', corpora=sorted_corpora, user_id=userid, xv_settings=xigtviz_settings)
    else:
        return render_template('login_screen.html', try_again=True)


# -------------------------------------------
# When a user clicks a "corpus", display the
# IGT instances contained by that corpus below.
# -------------------------------------------
@app.route('/populate/<corp_id>', methods=['POST'])
def populate(corp_id):
    xc = dbi.get_corpus(corp_id)
    xc = sorted(xc, key=lambda x: x.id)

    data = json.loads(request.get_data().decode())
    user_id = data.get('userID')

    filtered_list = []

    ratings = {inst.id: get_rating(inst) for inst in xc}
    nexts = {}
    for i, igt in enumerate(xc):

        # Skip this instance if we've hidden it
        # (As we do for duplicates)
        if get_state(user_id, corp_id, igt.id) != HIDDEN:
            filtered_list.append(igt)

        if i < len(xc)-1:
            nexts[igt.id] = xc[i+1].id
        else:
            nexts[igt.id] = None


    filtered_list = sorted(filtered_list, key=lambda x: x.id)


    return render_template('igt_list.html', igts=filtered_list, corp_id=corp_id, ratings=ratings, nexts=nexts)

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
    inst = dbi.get_igt(corp_id, igt_id)
    replace_lines(inst, clean_lines, None)

    # Now, remove any old normalized tier and replace it with
    # one generated by the odin-utils script.
    if normalized_tier(inst) is not None:
        delete_tier(normalized_tier(inst))

    add_normalized_tier(inst, cleaned_tier(inst))
    nt = normalized_tier(inst)

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

    # Remove the previously cleaned tier, and
    # regenerate it with the odin-utils script.
    delete_tier(cleaned_tier(inst))
    add_cleaned_tier(inst, raw_tier(inst))
    ct = cleaned_tier(inst)

    return render_template("tier_table.html",
                           table_type=CLEAN_TABLE_TYPE,
                           tier=ct,
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

    inst = Igt(id=igt_id)
    add_raw_tier(inst, data.get('raw'))
    add_clean_tier(inst, data.get('clean'))
    add_normal_tier(inst, data.get('normal'))

    try:
        ll = lang_lines(inst)[0]
    except NoNormLineException:
        ll = None

    try:
        gl = gloss_line(inst)
    except (NoNormLineException, NoGlossLineException):
        gl = None

    try:
        tl = trans_lines(inst)[0]
    except NoNormLineException:
        tl = None

    # if (ll is None) or (gl is None) or (tl is None):
    #     raise Exception("Missing L, G, or T line")


    response = {}

    # Check that the language line and gloss line
    # have the same number of whitespace-delineated tokens.
    if ll is not None and gl is not None:
        response['glw'] = 1 if len(lang(inst)) == len(gloss(inst)) else 0

        # Check that the language line and gloss line
        # have the same number of morphemes.
        response['glm'] = 1 if len(morphemes(inst)) == len(glosses(inst)) else 0
    else:
        response['glw'] = 0
        response['glm'] = 0

    # Check that the normalized tier has only L, G, T for tags.
    norm_tags = set([l.attributes.get('tag') for l in normalized_tier(inst)])
    response['tag'] = 1 if set(['L','G','T']) == norm_tags else 0

    # Check that the g/l lines are aligned in strict columns
    if ll is None or gl is None:
        response['col'] = 0
    else:
        response['col'] = 1 if is_strict_columnar_alignment(ll.value(), gl.value()) else 0

    # -------------------------------------------
    # DO ENRICHMENT
    # -------------------------------------------
    if tl is not None:
        generate_trans_words(inst)
        tag_trans_pos(inst)

        # If we have translation AND gloss, align them.
        if gl is not None:
            generate_gloss_glosses(inst)
            heur_align_inst(inst)

    if gl is not None and ll is not None:
        generate_lang_words(inst)
        if classify_gloss_pos(inst):
            try:
                project_gloss_pos_to_lang(inst)
            except GlossLangAlignException:
                pass

    inst.sort_tiers()

    # figure out how many columns we're going to need to number.

    # col_nums = range(1, max(len(lang(inst)), len(gloss(inst)), len(trans(inst))+1))
    #
    #
    # lws = generate_lang_words(inst)
    # gws = generate_gloss_glosses(inst)
    # tw = generate_trans_words(inst)
    #
    # lms = morphemes(inst)
    # gms = glosses(inst)
    #
    # lang_list = []
    # for lw in lws:
    #     pairs = (lw, [])
    #     for lm in lms:
    #         if x_contains_y(inst, lw, lm):
    #             pairs[1].append(lm)
    #     lang_list.append(pairs)
    #
    # gloss_list = []
    # for gw in gws:
    #     pairs = (gw, [])
    #     for gm in gms:
    #         if x_contains_y(inst, gw, gm):
    #             pairs[1].append(gm)
    #     gloss_list.append(pairs)


    # response['words'] = render_template('group_2.html',
    #                                     col_nums=col_nums,
    #                                     lang=lang_list,
    #                                     gloss=gloss_list,
    #                                     trans=tw,
    #                                     aln=heur_align_inst(inst),
    #                                     item_index=item_index)

    igtjson = xigtjson.encode_igt(inst)
    response['igt'] = igtjson

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
    add_editor_metadata(igt)

    # Do the actually saving of the igt instance.
    dbi.set_igt(corp_id, igt_id, igt)

    return make_response()

# -------------------------------------------
# Split an instance
# -------------------------------------------
@app.route('/split/<corp_id>/<igt_id>', methods=['POST'])
def split(corp_id, igt_id):
    data = request.get_json()

    user_id = data.get('userID')
    clean   = data.get('clean')
    norm    = data.get('norm')

    # -------------------------------------------
    # Get the original instance that we're going
    # to split, and add some metadata info.
    # -------------------------------------------
    igt = dbi.get_igt(corp_id, igt_id)
    igt = replace_lines(igt, clean, norm)
    add_editor_metadata(igt)
    add_split_metadata(igt, igt.id)

    # -------------------------------------------
    # Make our new copies.
    # -------------------------------------------
    igt_a = copy_xigt(igt)
    igt_b = copy_xigt(igt)

    igt_a.id = igt.id+'_a'
    igt_b.id = igt.id+'_b'

    dbi.add_igt(corp_id, igt_a)
    dbi.add_igt(corp_id, igt_b)

    set_state(user_id, corp_id, igt.id, HIDDEN)
    set_state(user_id, corp_id, igt_a.id, NORM_STATE)
    set_state(user_id, corp_id, igt_b.id, NORM_STATE)

    return json.dumps({'next':igt_a.id})

@app.route('/delete/<corp_id>/<igt_id>', methods=['POST'])
def delete_igt(corp_id, igt_id):

    user = request.get_json().get('userID')

    # TODO: FIXME: A sleipnir update should fix this so that we don't need to hide deleted instances.
    set_state(user, corp_id, igt_id, HIDDEN)
    dbi.del_igt(corp_id, igt_id)

    return make_response()

# -------------------------------------------
# Static files
# -------------------------------------------

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)