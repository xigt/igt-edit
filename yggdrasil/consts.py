EDITOR_METADATA_TYPE = 'editor'

RATING_META_TYPE   = 'rating'
COMMENT_META_TYPE  = 'comment'
JUDGMENT_META_TYPE = 'judgment'

# -------------------------------------------
# Editor Data Provenance
# -------------------------------------------
EDITOR_DATA_SRC = 'annotator'
DUPLICATE_ATTR  = 'duplicate-of'

# -------------------------------------------
# Editor Quality Ratings
# -------------------------------------------
HIDDEN = 4
BAD_QUALITY = 3
OK_QUALITY = 2
GOOD_QUALITY = 1

BAD_QUALITY_STR  = 'bad'
OK_QUALITY_STR   = 'ok'
GOOD_QUALITY_STR = 'good'

RATINGS = {BAD_QUALITY:BAD_QUALITY_STR,
           OK_QUALITY:OK_QUALITY_STR,
           GOOD_QUALITY:GOOD_QUALITY_STR}
RATINGS_REV = {RATINGS[key]:key for key in RATINGS}

QUALITY_META_ATTR = 'quality'
USER_META_ATTR = 'user'
REASON_META_ATTR = 'reason'

# -------------------------------------------

RAW_STATE = 0
CLEAN_STATE = 1
NORM_STATE = 2

# -------------------------------------------
# Types of tables
# -------------------------------------------
NORMAL_TABLE_TYPE = 'normal'
CLEAN_TABLE_TYPE  = 'clean'

# -------------------------------------------
# Tags
# -------------------------------------------
PUNC_TAG = 'PUNC'