from yggdrasil.users import *

def delete_prompt():
    userdict = {}
    for i, user_id in enumerate(list_users()):
        userdict[str(i)] = user_id
        print('\t({}) {}'.format(i, user_id))

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

def main_prompt():
    while True:
        print("Current users are:")
        for user in list_users():
            print('\t'+user)
        print()
        actions = {'d':delete_prompt,
                   'a':add_prompt,
                   'q':quit}
        resp = input("Action?\nOptions: {d}elete, {a}dd, {q}uit: ")
        if resp.strip() in actions:
            actions[resp]()



if __name__ == '__main__':



    main_prompt()



