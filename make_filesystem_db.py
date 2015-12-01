#!/usr/bin/env python

import sys
import os
import shutil
import json
import uuid
import argparse
import logging

from xigt.codecs import xigtxml

def run(args):
    index_path = os.path.join(args.dbdir, 'index.json')
    if not os.path.isdir(args.dbdir):
        logging.info('Creating database directory: %s' % args.dbdir)
        os.mkdir(args.dbdir)
    if not os.path.isfile(index_path):
        index = {'files': {}}
        json.dump(index, open(index_path, 'w'))
    datadir = os.path.join(args.dbdir, 'data')
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    index = json.load(open(index_path))
    for f in args.files:
        logging.info('Adding %s to database.' % f)
        _id = str(uuid.uuid4())
        path = os.path.join('data', '%s.xml' % _id)
        name, ext = os.path.splitext(os.path.basename(f))
        xc = xigtxml.load(f)
        entry = {'name': name, 'path': path, 'igt_count': len(xc)}
        shutil.copyfile(f, os.path.join(args.dbdir, path))
        index['files'][_id] = entry
    logging.info('Updating index.')
    json.dump(index, open(index_path, 'w'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dbdir', help='Database directory')
    parser.add_argument('files', nargs='*', help='files to add to the db')
    args = parser.parse_args()
    run(args)
