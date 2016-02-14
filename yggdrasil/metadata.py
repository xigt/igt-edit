from intent.igt.metadata import set_meta_attr, find_meta, find_meta_attr, set_meta_text
from yggdrasil.consts import USER_META_ATTR, RATING_META_TYPE, QUALITY_META_ATTR, RATINGS, RATINGS_REV, \
    EDITOR_METADATA_TYPE, COMMENT_META_TYPE, REASON_META_ATTR


def set_rating(inst, user, rating, reason):
    set_meta_attr(inst, RATING_META_TYPE, USER_META_ATTR, user, metadata_type=EDITOR_METADATA_TYPE)
    set_meta_attr(inst, RATING_META_TYPE, QUALITY_META_ATTR, RATINGS.get(rating), metadata_type=EDITOR_METADATA_TYPE)
    set_meta_attr(inst, RATING_META_TYPE, REASON_META_ATTR, reason, metadata_type=EDITOR_METADATA_TYPE)

def get_rating(inst):
    r = find_meta_attr(inst, RATING_META_TYPE, QUALITY_META_ATTR, metadata_type=EDITOR_METADATA_TYPE)
    if r is not None:
        return RATINGS_REV.get(r)

def get_reason(inst):
    r = find_meta_attr(inst, RATING_META_TYPE, REASON_META_ATTR, metadata_type=EDITOR_METADATA_TYPE)
    return r

def set_comment(inst, user, comment):
    set_meta_text(inst, COMMENT_META_TYPE, comment, metadata_type=EDITOR_METADATA_TYPE)
    set_meta_attr(inst, COMMENT_META_TYPE, USER_META_ATTR, user, metadata_type=EDITOR_METADATA_TYPE)

def get_comment(inst):
    m = find_meta(inst, COMMENT_META_TYPE, metadata_type=EDITOR_METADATA_TYPE)
    if m is not None:
        return m.text
    else:
        return None

