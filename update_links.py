#!/bin/python3

import os
import re
import json
from urllib.request import urlopen
from urllib.parse import urlencode

patternkey = re.compile(r'\[\[zotero://[\d\.:]+/zotxt/select\?(\w*)key=([\w:]+)\|(.*?)\]\]')

zotxtroot = 'http://127.0.0.1:23119/zotxt/items?'

def fetchkey(easykey):
    data = {
            'easykey':easykey,
            'format': 'key'
           }
    url = zotxtroot + urlencode(data)
    resp = json.loads(urlopen(url).read().decode('utf-8'))
    return resp[0]

def matchkey(m):
    if m.group(1) == '':
        key = m.group(2)
    elif m.group(1) == 'easy':
        key = ''
        try:
            key = fetchkey(m.group(2))
        except Exception as e:
            print(f'ERROR: got an exception {e}')
            print(m.group[0])
    elif m.group(1) == 'betterbibtex':
        key = '@' + m.group(2)
    else:
        key = ''
        print(f'ERROR: found something unspecified: {m.group(0)}')
        print(m.group[0])
    return f'[[zotero://select/items/{key}|{m.group(3)}]]'

def updatefile(filename, backup=True):
    backupfile = filename + '.bak'
    os.rename(filename, backupfile)
    with open(backupfile, 'r') as bf, open(filename, 'w') as f:
        for line in bf.readlines():
            line = patternkey.sub(matchkey, line)
            f.write(line)
    if not backup:
        os.remove(backupfile)

def walkdir(dirname, backup=True):
    for dirpath, dirnames, files in os.walk(dirname):
        print(f'Found directory: {dirpath}')
        for filename in files:
            filename = os.path.join(dirpath, filename)
            if not filename.endswith('.txt'):
                print(f'{filename} Skipped')
                continue
            updatefile(filename, backup)
            print(f'{filename} Processed')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This program converts the Zotero links '
            'of the old format into the Zotero own link. Zotero should run.')
    parser.add_argument('-b', '--nobackup', action='store_false',
            help='Do not retain the original files as *.bak')

    def dirpath(string):
        path = os.path.abspath(string)
        if not os.path.isdir(path):
            msg = 'is not a directory'
            raise argparse.ArgumentTypeError(msg)
        return path
    parser.add_argument('dir', type=dirpath, help='Root directory of the zim wiki')

    args = parser.parse_args()

    walkdir(args.dir, args.nobackup)
