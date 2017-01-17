import json
import logging
import os
import sys

# -------------------------------------------
# Set up the Flask app
# -------------------------------------------
import re
from flask import Flask, render_template, url_for, request, make_response, Response, abort

app = Flask(__name__)
application = app

# -------------------------------------------
# Import the configuration.
# -------------------------------------------
sys.path.append(os.path.dirname(__file__))
from yggdrasil import config

# -------------------------------------------
# Add the configuration to the app config
# -------------------------------------------
app.config.from_object(config)

# -------------------------------------------
# Get the other constants, config vars
# -------------------------------------------
from yggdrasil.config import PYTHONPATH, LINE_TAGS, LINE_ATTRS, XIGTVIZ, PDF_DIR
from yggdrasil.consts import NORM_STATE, CLEAN_STATE, RAW_STATE, NORMAL_TABLE_TYPE, CLEAN_TABLE_TYPE, HIDDEN
from yggdrasil.utils import aln_to_json


# -------------------------------------------
# Add the additional path items.
# -------------------------------------------
for path_item in PYTHONPATH.split(':'):
    sys.path.append(path_item)

from yggdrasil.metadata import get_rating, set_rating, set_comment, get_comment, get_reason
from yggdrasil.users import get_user_corpora, get_state, set_state, list_users
from yggdrasil.igt_operations import replace_lines, add_editor_metadata, add_split_metadata, add_raw_tier, \
    add_clean_tier, add_normal_tier, columnar_align_l_g

# -------------------------------------------
# ODIN_UTILS IMPORTS
# -------------------------------------------
import odinclean, odinnormalize

# -------------------------------------------
# XIGT Imports
# -------------------------------------------
from xigt import Igt, Item
from xigt.codecs import xigtjson, xigtxml
import xigt.xigtpath



# -------------------------------------------
# Now that we've imported our dependencies,
# we can register the blueprint.
# -------------------------------------------
from sleipnir import dbi

# -------------------------------------------
# Import other stuff here.
# -------------------------------------------

from intent.consts import CLEAN_ID, NORM_ID, all_punc_re_mult
from intent.igt.igtutils import is_strict_columnar_alignment, rgp
from intent.igt.create_tiers import lang_lines, gloss_line, trans_lines, \
    generate_lang_words, generate_gloss_words, generate_trans_words, lang, gloss, morphemes, glosses, trans, \
    pos_tag_tier
from intent.igt.igt_functions import copy_xigt, delete_tier, heur_align_inst, classify_gloss_pos, \
    tag_trans_pos, project_gloss_pos_to_lang, add_gloss_lang_alignments, get_bilingual_alignment, \
    get_trans_lang_alignment, get_trans_gloss_alignment
from intent.igt.references import raw_tier, cleaned_tier, normalized_tier, item_index
from intent.igt.exceptions import NoNormLineException, NoGlossLineException, GlossLangAlignException, \
    NoLangLineException, NoTransLineException
from intent.utils.listutils import flatten_list

app.debug = True

# -------------------------------------------
# Set up logging.
# -------------------------------------------
YGG_LOG = logging.getLogger('YGG')

# -------------------------------------------
# Set up XigtViz settings
# -------------------------------------------
xv_conf = os.path.join(XIGTVIZ, 'config.json')
with open(xv_conf) as f:
    xv_settings = json.loads(f.read())
    app.config['xvs'] = xv_settings

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
    YGG_LOG.critical(list_users())
    YGG_LOG.critical(userid)
    YGG_LOG.critical(user_corpora)
    YGG_LOG.critical(dbi.list_corpora())
    if user_corpora is not None:
        all_corpora  = dbi.list_corpora()

        filtered_corpora = [c for c in all_corpora if c.get('id') in user_corpora]

        sorted_corpora = sorted(filtered_corpora,
                                key=lambda x: x.get('name'))


        return render_template('browser.html', corpora=sorted_corpora, user_id=userid)
    else:
        return render_template('login_screen.html', try_again=True)

# -------------------------------------------
# Download the corpus in xml.
# -------------------------------------------
@app.route('/download/<corp_id>')
def download_corp(corp_id):
    xc = dbi.get_corpus(corp_id)
    xc.sort(key=igt_id_sort)
    r = Response(xigtxml.dumps(xc), mimetype='text/xml', )
    r.headers['Content-Disposition'] = "attachment; filename={}.xml".format(dbi._get_name(corp_id))
    return r


def igt_id_sort(igt):
    id_str = igt.id
    igt_re = re.search('([0-9]+)-([0-9]+)', id_str)
    if igt_re:
        igt_id, inst_id = igt_re.groups()
        return (int(igt_id), int(inst_id))
    else:
        igt_re=re.search('([0-9]+)', id_str)
        if igt_re:
            return int(igt_re.group(1))
        else:
            return id_str

# -------------------------------------------
# When a user clicks a "corpus", display the
# IGT instances contained by that corpus below.
# -------------------------------------------
@app.route('/populate/<corp_id>', methods=['POST'])
def populate(corp_id):
    xc = dbi.get_corpus(corp_id)
    xc.sort(key=igt_id_sort)

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


    # filtered_list = sorted(filtered_list, key=igt_id_sort)


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
    assert isinstance(inst, Igt)

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

    docid = inst.attributes.get('doc-id')
    pdflink = None
    if pdfpath(docid):
        pdflink='/pdf/'+docid

    # -------------------------------------------
    # Render the element template.
    # -------------------------------------------
    content = render_template('element.html', state=state, rt=rt, ct=ct, nt_content=nt_content,
                              igt=inst, igt_id=igt_id, corp_id=corp_id,
                              comment=get_comment(inst), rating=get_rating(inst), reason=get_reason(inst),
                              pdflink=pdflink, lang=xigt.xigtpath.find(inst, './/dc:subject').text)

    return json.dumps({"content":content})

def pdfpath(docid):
    path = os.path.join(PDF_DIR, '{}.pdf'.format(docid))
    if docid and os.path.exists(path):
        return path
    else:
        return None

@app.route('/pdf/<docid>', methods=['GET'])
def get_pdf(docid):
    pdfpath = os.path.join(PDF_DIR, '{}.pdf'.format(docid))
    if os.path.exists(pdfpath):
        with open(pdfpath, 'rb') as f:
            r = Response(f.read(), mimetype='application/pdf')
            r.headers['Content-Disposition'] = "attachment; filename={}.pdf".format(docid)
            return r
    else:
        abort(404)

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

    odinnormalize.add_normalized_tier(inst, cleaned_tier(inst))
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
    if cleaned_tier(inst):
        delete_tier(cleaned_tier(inst))

    odinclean.add_cleaned_tier(inst, raw_tier(inst))
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

    response = {}

    # Check that the tiers are of equal length...
    def equal_lengths(tier_a, tier_b):
        tier_a_items = [i for i in tier_a if not re.match('^{}$'.format(all_punc_re_mult), i)]
        tier_b_items = [i for i in tier_b if not re.match('^{}$'.format(all_punc_re_mult), i)]
        return len(tier_a_items) == len(tier_b_items)


    # Check that the language line and gloss line
    # have the same number of whitespace-delineated tokens.
    if ll is not None and gl is not None:
        response['glw'] = 1 if equal_lengths([l.value() for l in lang(inst)], [g.value() for g in gloss(inst)]) else 0

        # Check that the language line and gloss line
        # have the same number of morphemes.
        morph_list = flatten_list([re.split('[\-=]', w.value()) for w in lang(inst)])
        gloss_list = flatten_list([re.split('[\-=]', g.value()) for g in gloss(inst)])
        response['glm'] = 1 if equal_lengths(morph_list, gloss_list) else 0
    else:
        response['glw'] = 0
        response['glm'] = 0

    # Check that the normalized tier has only L, G, T for tags.
    norm_tags = set([l.attributes.get('tag') for l in normalized_tier(inst)])
    response['tag'] = 1 if set(['L','G','T']).issubset(norm_tags) else 0

    # Check that the g/l lines are aligned in strict columns
    if ll is None or gl is None:
        response['col'] = 0
    else:
        response['col'] = 1 if is_strict_columnar_alignment(ll.value(), gl.value()) else 0

    # If the number of gloss words on the lang line and gloss
    # line do not match, abort further enrichment and provide
    # a warning.
    if response['glw'] == 0:
        response['group2'] = render_template('group2/group_2_invalid.html')
        return json.dumps(response)

    # -------------------------------------------
    # DO ENRICHMENT
    # -------------------------------------------

    # Start by creating words:
    if tl is not None: generate_trans_words(inst)
    if ll is not None: generate_lang_words(inst)
    if gl is not None:
        generate_gloss_words(inst)
        glosses(inst)


    # Add POS tags as necessary
    if tl is not None: tag_trans_pos(inst)

    # Add alignment
    if gl is not None and tl is not None:
        heur_align_inst(inst)

        # Try POS tagging the language line...
        try:
            add_gloss_lang_alignments(inst)
        except GlossLangAlignException:
            pass

        if classify_gloss_pos(inst):
            try:
                project_gloss_pos_to_lang(inst)
            except GlossLangAlignException:
                pass

    inst.sort_tiers()

    response['group2'] = display_group_2(inst)

    return json.dumps(response)

def display_group_2(inst):
    """
    This function is responsible for compiling all the elements of the "group 2"
    items for editing; e.g. POS tags and word alignment.

    :type inst: Igt
    """
    return_html = ''


    # --1) For the POS tag view, we're going to create a table that is 4 rows,
    #      with as many columns as there are words.

    try:
        lang_w = lang(inst)
    except NoLangLineException as nlle:
        lang_w = None
    try:
        gloss_w = gloss(inst)
    except NoGlossLineException as ngle:
        gloss_w = None

    try:
        trans_w = trans(inst)
        trans_pos = pos_tag_tier(inst, trans_w.id)
    except NoTransLineException as ntle:
        trans_w = None
        trans_pos = []

    def make_gloss_pos(): return [Item(id='gw-pos{}'.format(item_index(l))) for l in lang_w]

    if gloss_w is not None:
        gloss_pos = pos_tag_tier(inst, gloss_w.id)
        if gloss_pos is None:
            gloss_pos = make_gloss_pos()
    elif gloss_w is None and lang_w is not None:
        gloss_pos = make_gloss_pos()

    if gloss_w is not None and trans_w is not None:
        aln = get_trans_gloss_alignment(inst)
    else:
        aln = []



    return_html += render_template('group2/group_2.html',
                                   lang_w=lang_w,
                                   gloss_w=gloss_w,
                                   trans_w=trans_w,
                                   gloss_pos=gloss_pos,
                                   trans_pos=trans_pos,
                                   aln=[[x, y] for x, y in aln]
                                   )

    return return_html

# -------------------------------------------
# Save a file after changes
# -------------------------------------------
@app.route('/save/<corp_id>/<igt_id>', methods=['PUT'])
def save(corp_id, igt_id):
    data = request.get_json()

    # -------------------------------------------
    # Get the lines
    # -------------------------------------------
    clean = data.get('clean')
    norm  = data.get('norm')
    user_id = data.get('userID')

    # Get the other data
    rating = data.get('rating')
    reason = data.get('reason')
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
    set_rating(igt, user_id, rating, reason)

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

    set_state(user, corp_id, igt_id, HIDDEN)
    dbi.del_igt(corp_id, igt_id)

    return make_response()

# -------------------------------------------
# Static files
# -------------------------------------------

@app.route('/static/<path:path>', methods=['GET'])
def default(path):
    return url_for('static', filename=path)