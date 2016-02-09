#!/usr/bin/env python3.4
from yggdrasil.users import *

def enum_users():
    userdict = {}
    for i, user_id in enumerate(list_users()):
        userdict[str(i)] = user_id
        print('\t({}) {}'.format(i, user_id))
    return userdict

def delete_prompt():
    userdict = enum_users()

    while True:
        resp = input("Delete which user?\nOptions: {#} or {q} (cancel): ")
        if resp.strip() == 'q':
            print("Canceled.", end='\n\n')
            return
        elif resp.strip() in userdict:
            while True:
                yn = input('\nThis will delete user "{}". Are you sure?\nOptions: {{y}} {{n}}: '.format(userdict[resp.strip()]))
                if yn.strip() == 'y':
                    del_user(userdict[resp.strip()])
                    print('User "{}" deleted.'.format(userdict[resp.strip()]), end='\n\n')
                    return
                elif yn.strip() == 'n':
                    print("Delete Aborted.", end='\n\n')
                    return


def add_prompt():
    user_id = add_user()
    print('User "{}" added.'.format(user_id), end='\n\n')

def quit():
    sys.exit(0)

def enum_corpora(all_corpora, user_corpora, i):
    print("Available Corpora:")
    corp_dict = {}
    corpus_keys = sorted(all_corpora.keys())
    for i, corp_id in enumerate([c for c in corpus_keys if c not in user_corpora], start=i):
        print("\t({1}) {0}".format(all_corpora.get(corp_id).get('name'), i))
        corp_dict[str(i)] = corp_id
    return corp_dict

def manage_user(user_id):
    while True:


        add_delete_exit = False
        while not add_delete_exit:

            from sleipnir import dbi
            i = 0
            all_corpora = {c.get('id'):c for c in dbi.list_corpora()}

            if not all_corpora:
                print("No current corpora to add.",end='\n\n')
                add_delete_exit = True
                return
            else:
                user_corpora = get_user_corpora(user_id)

                print("\nCurrent user corpora:")
                deldict = {}
                for corp_id in user_corpora:
                    if all_corpora.get(corp_id):
                        print("\t({}) {}".format(i, all_corpora.get(corp_id).get('name')))
                        deldict[str(i)] = corp_id
                        i+=1

                corpdict = enum_corpora(all_corpora, user_corpora, i=i)
                resp = input("Add/delete corpus for user?\nOptions: {{#}} or {{q}}: ")

                if resp.strip() in corpdict:
                    add_user_corpora(user_id, corpdict[resp.strip()])
                    print('Corpus "{}" added to user "{}"'.format(all_corpora[corpdict[resp.strip()]].get('name'), user_id), end='\n\n')
                    add_delete_exit = True
                    break
                elif resp.strip() in deldict:
                    corp_name = all_corpora[deldict[resp.strip()]].get('name')
                    while True:
                        yn = input('\nThis will remove corpus "{}" from user "{}". Continue?\nOptions {{y}} {{n}}'.format(corp_name, user_id))
                        if yn.strip() == 'y':
                            del_user_corpora(user_id, deldict[resp.strip()])
                            print('Corpus "{}" was removed from user "{}".'.format(corp_name, user_id), end='\n\n')
                            add_delete_exit = True
                            break
                        elif yn.strip() == 'n':
                            print("Aborted.\n")
                            add_delete_exit = True
                            break
                elif resp.strip() == 'q':
                    return


def manage_users():
    while True:
        print("\nCurrent Users:")
        userdict=enum_users()
        resp = input("Manage which user?\nOptions: {{#}} or {{q}}: ")
        if resp.strip() in userdict:
            manage_user(userdict[resp.strip()])
            return
        elif resp.strip() == 'q':
            return



def main_prompt():
    while True:
        print("Current users are:")
        for user in list_users():
            print('\t'+user)
        print()
        actions = {'d':delete_prompt,
                   'a':add_prompt,
                   'q':quit,
                   'm':manage_users}

        resp = input("Action?\nOptions: {d}elete, {a}dd, {m}anage, {q}uit: ")
        if resp.strip() in actions:
            actions[resp]()



if __name__ == '__main__':



    main_prompt()



