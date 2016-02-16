#!/usr/bin/env python3
from argparse import ArgumentParser

from sleipnir import dbi

def prompt_corpora():

    # Main loop
    main_loop = True
    while main_loop:
        corpora = dbi.list_corpora()
        print("Current corpora:")
        corpus_map = {}
        for i, corpus in enumerate(sorted(corpora, key=lambda x: x['name'])):
            corpus_map[i] = corpus
            print('{:>6} {} [{}]'.format('({})'.format(i), corpus['name'], corpus['id']))
        resp = input("Enter a corpus number to delete, or q to quit: ")
        if resp == 'q':
            main_loop = False
        elif resp.strip() and int(resp) in corpus_map:
            r = int(resp)
            print('This will delete the corpus "#{}" with name "{}" and id "{}."'.format(r, corpus_map[r]['name'], corpus_map[r]['id']))
            del_conf = input("Are you sure? [y/n]")
            if del_conf.lower() == 'y':
                dbi.del_corpus(corpus_map[r]['id'])



if __name__ == '__main__':
    p = ArgumentParser()
    args = p.parse_args()

    prompt_corpora()