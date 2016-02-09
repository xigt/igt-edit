from intent.consts import CLEAN_STATE, CLEAN_ID, NORM_ID, NORM_STATE, DATA_SRC_ATTR, DATA_PROV
from intent.igt.igt_functions import create_text_tier_from_lines
from intent.igt.metadata import set_meta_attr, set_meta
from intent.igt.references import cleaned_tier, normalized_tier
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