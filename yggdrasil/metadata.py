from intent.igt.metadata import set_meta_attr, find_meta, find_meta_attr
from yggdrasil.consts import USER_META_ATTR, RATING_META_TYPE, QUALITY_META_ATTR, RATINGS, RATINGS_REV, \
    EDITOR_METADATA_TYPE


def set_rating(inst, user, rating):
    set_meta_attr(inst, RATING_META_TYPE, USER_META_ATTR, user, metadata_type=EDITOR_METADATA_TYPE)
    set_meta_attr(inst, RATING_META_TYPE, QUALITY_META_ATTR, RATINGS.get(rating), metadata_type=EDITOR_METADATA_TYPE)

def get_rating(inst):
    r = find_meta_attr(inst, RATING_META_TYPE, QUALITY_META_ATTR, metadata_type=EDITOR_METADATA_TYPE)
    if r is not None:
        return RATINGS_REV.get(r)