import os
from random import randint

import sys

from .config import USER_DB
import json
import logging
DB_LOG = logging.getLogger('DB')

KEY_RATING = 'rating'
KEY_STATE = 'state'

def list_users():
    json_obj = load_db()
    users = json_obj.get('users')
    return users.keys() if users else []

def load_db():
    """
    :rtype: dict
    """
    if not os.path.exists(USER_DB):
        return {"users":{}}
    else:
        f = open(USER_DB, 'r')
        s = f.read()
        if not s.strip():
            data = {"users":{}}
        else:
            data = json.loads(s)

        if "users" not in data:
            data["users"] = {}
        f.close()
        return data

def dump_db(json_obj):
    if json_obj is not None:
        try:
            json_f = open(USER_DB, 'w')
        except PermissionError as pe:
            DB_LOG.critical('ERROR: Could not open database "{}" for writing.'.format(USER_DB))
            sys.exit(2)
        json.dump(json_obj, json_f)
        json_f.close()
    else:
        raise Exception("JSON object is None")

def gen_id(length=8):
    alphabet = '0123456789abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ret_str = ''
    for i in range(length):
        r = randint(0,61)
        ret_str += alphabet[r]
    return ret_str

def add_user(user_id=None):
    json_obj = load_db()
    if user_id is None:
        user_id = gen_id()
        assert user_id not in list_users()

    json_obj['users'][user_id] = {'corpora':[]}
    dump_db(json_obj)
    return user_id

def del_user(user_id):
    json_obj = load_db()
    try:
        del json_obj['users'][user_id]
    except KeyError:
        DB_LOG.critical('No such userID "{}"'.format(user_id))
        sys.exit(2)
    dump_db(json_obj)

def add_user_corpora(user_id, corp_id):
    json_obj = load_db()
    if user_id not in json_obj["users"]:
        DB_LOG.critical('UserID "{}" does not exist.'.format(user_id))
        sys.exit(2)
    else:
        json_obj["users"][user_id]["corpora"].append(corp_id)
        dump_db(json_obj)

def del_user_corpora(user_id, corp_id):
    json_obj = load_db()
    if user_id not in json_obj["users"]:
        DB_LOG.critical('UserID "{}" does not exist.'.format(user_id))
        sys.exit(2)
    else:
        json_obj["users"][user_id]["corpora"].remove(corp_id)
        dump_db(json_obj)

def get_user_corpora(user_id):
    """
    Get the corpora that are owned by this user.
    """
    json_obj = load_db()
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

def set_rating(user_id, corp_id, igt_id, rating):
    set(user_id, corp_id, igt_id, KEY_RATING, rating)

def get_state(user_id, corp_id, igt_id):
    state = get(user_id, corp_id, igt_id, KEY_STATE)
    if state is not None:
        state = int(state)
    return state

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