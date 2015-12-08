from .config import USER_DB
import json
import logging
DB_LOG = logging.getLogger('DB')

def get_rating(user_id, corp_id, igt_id):
    # Open the JSON file
    with open(USER_DB) as f:
        d = json.load(f)
        c = d.get(corp_id)
        if c is not None:
            i = c.get(igt_id)
            if i is not None:
                return i.get(str(user_id))

def set_rating(user_id, corp_id, igt_id, rating):

    # Load the existing JSON file
    f = open(USER_DB, 'r')
    d = json.load(f)
    f.close()

    # Get the corpus
    c = d.get(corp_id)

    # If the entry doesn't exist, add it.
    if c is None:
        d[corp_id] = {igt_id:{user_id:rating}}

    # Otherwise, get the IGT entry.
    else:
        i = c.get(igt_id)

        # If the igt entry doesn't exist, create it.
        if i is None:
            c[igt_id] = {str(user_id):rating}

        # If it does, set the rating.
        else:
            i[str(user_id)] = rating

    # Write it out.
    with open(USER_DB, 'w') as f:
        json.dump(d, f)