from .config import USER_DB
import json
import logging
DB_LOG = logging.getLogger('DB')

KEY_RATING = 'rating'
KEY_PROGRESS = 'progress'
KEY_STATE = 'state'

def get_user_corpora(user_id):
    """
    Get the corpora that are owned by this user.
    """
    with open(USER_DB) as f:
        json_obj = json.load(f)
        user_corpora = json_obj['users'].get(user_id)

        if user_corpora is None:
            return None
        else:
            return user_corpora.get('corpora')



def get(user_id, corp_id, igt_id, key):
    # Open the JSON file
    with open(USER_DB) as f:
        d = json.load(f)
        c = d.get(corp_id)
        if c is not None:
            i = c.get(igt_id)
            if i is not None:
                pair = i.get(str(user_id))
                if pair is not None:
                    return pair.get(key)


def get_rating(user_id, corp_id, igt_id):
    return get(user_id, corp_id, igt_id, KEY_RATING)

def get_progress(user_id, corp_id, igt_id):
    return get(user_id, corp_id, igt_id, KEY_PROGRESS)

def set_rating(user_id, corp_id, igt_id, rating):
    set(user_id, corp_id, igt_id, KEY_RATING, rating)

def get_state(user_id, corp_id, igt_id):
    return get(user_id, corp_id, igt_id, KEY_STATE)

def set_state(user_id, corp_id, igt_id, state):
    set(user_id, corp_id, igt_id, KEY_STATE, state)

def set(user_id, corp_id, igt_id, key, val):

    # Load the existing JSON file
    f = open(USER_DB, 'r')
    d = json.load(f)
    f.close()

    # Get the corpus
    c = d.get(corp_id)

    # If the entry doesn't exist, add it.
    if c is None:
        d[corp_id] = {igt_id:{user_id:{key:val}}}

    # Otherwise, get the IGT entry.
    else:
        i = c.get(igt_id)

        # If the igt entry doesn't exist, create it.
        if i is None:
            c[igt_id] = {str(user_id):{key:val}}

        # If it does, set the rating.
        else:
            pair = i.get(str(user_id))
            if pair is None:
                i[str(user_id)] = {key:val}
            else:
                pair[key] = val

    # Write it out.
    with open(USER_DB, 'w') as f:
        json.dump(d, f)