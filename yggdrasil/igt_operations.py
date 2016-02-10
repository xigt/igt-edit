from intent.consts import CLEAN_STATE, CLEAN_ID, NORM_ID, NORM_STATE, DATA_SRC_ATTR, DATA_PROV, ODIN_TAG_ATTRIBUTE, \
    ODIN_JUDGMENT_ATTRIBUTE, RAW_ID, RAW_STATE, ODIN_TYPE, STATE_ATTRIBUTE
from intent.igt.metadata import set_meta_attr, set_meta
from intent.igt.references import cleaned_tier, normalized_tier, gen_item_id, gen_tier_id
from xigt import Item, Tier
from yggdrasil.consts import EDITOR_DATA_SRC, DUPLICATE_ATTR
from yggdrasil.consts import EDITOR_METADATA_TYPE


def replace_lines(inst, clean_lines, norm_lines):
    """
    Given an instance and a list of clean lines and normal lines,
    add a cleaned tier and normalized if they do not already exist,
    otherwise, replace them.

    :param inst:
    :type inst: xigt.Igt
    :param clean_lines:
    :type clean_lines: list[dict]
    :param norm_lines:
    :type norm_lines: list[dict]
    """

    # -------------------------------------------
    # Remove the old clean/norm lines.
    # -------------------------------------------
    old_clean_tier = cleaned_tier(inst)
    if old_clean_tier is not None:
        inst.remove(old_clean_tier)

    old_norm_tier = normalized_tier(inst)
    if old_norm_tier is not None:
        inst.remove(old_norm_tier)

    # -------------------------------------------
    # Now, add the clean/norm lines, if provided.
    # -------------------------------------------
    if clean_lines:
        new_clean_tier = create_text_tier_from_lines(inst, clean_lines, CLEAN_ID, CLEAN_STATE)
        inst.append(new_clean_tier)

    if norm_lines:
        new_norm_tier = create_text_tier_from_lines(inst, norm_lines, NORM_ID, NORM_STATE)
        inst.append(new_norm_tier)

    return inst

def add_editor_metadata(igt):
    ct = cleaned_tier(igt)
    nt = normalized_tier(igt)
    for tier in [ct, nt]:
        if tier is not None:
            set_meta_attr(tier, DATA_PROV, DATA_SRC_ATTR, EDITOR_DATA_SRC, metadata_type=EDITOR_METADATA_TYPE)

def add_split_metadata(igt, source_id):
    set_meta_attr(igt, DATA_PROV, DUPLICATE_ATTR, source_id, metadata_type=EDITOR_METADATA_TYPE)


def create_text_tier_from_lines(inst, lines, id_base, state):
    """
    Given a list of lines that are dicts with the attributes 'text' and 'tag', create
    a text tier of the specified type with the provided line items.

    :type lines: list[dict]
    """
    # -------------------------------------------
    # 1) Generate the parent tier.
    tier = Tier(id=gen_tier_id(inst, id_base), type=ODIN_TYPE, attributes={STATE_ATTRIBUTE:state})


    # -------------------------------------------
    # 2) Iterate over the list of lines
    for line in lines:

        # Make sure the line is a dict.
        if not hasattr(line, 'get') or 'text' not in line or 'tag' not in line:
            raise Exception("When constructing tier from lines, must be a list of dicts with keys 'text' and 'tag'.")

        # Construct the list of tags.
        alltags = []
        if line.get('tag') is not None:
            alltags.append(line.get('tag'))
        if line.get('labels') is not None and line.get('labels'):
            alltags.append(line.get('labels'))
        tag_str = '+'.join(alltags)


        # Construct the attributes
        line_attributes = {ODIN_TAG_ATTRIBUTE:tag_str}
        if line.get('judgment') is not None:
            line_attributes[ODIN_JUDGMENT_ATTRIBUTE] = line['judgment']

        # Add the linenumber
        if line.get('lineno'):
            line_attributes['line'] = line.get('lineno', '')


        l = Item(id=gen_item_id(tier.id, len(tier)),
                   attributes=line_attributes,
                   text=line.get('text'))
        tier.append(l)
    return tier

def add_text_tier_from_lines(inst, lines, id_base, state):
    tier = create_text_tier_from_lines(inst, lines, id_base, state)
    inst.append(tier)

def add_raw_tier(inst, lines):
    add_text_tier_from_lines(inst, lines, RAW_ID, RAW_STATE)

def add_clean_tier(inst, lines):
    add_text_tier_from_lines(inst, lines, CLEAN_ID, CLEAN_STATE)

def add_normal_tier(inst, lines):
    add_text_tier_from_lines(inst, lines, NORM_ID, NORM_STATE)
