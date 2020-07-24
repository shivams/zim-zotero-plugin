#!/bin/python3

from urllib.request import urlopen
from urllib.parse import urlencode
import re


zotxturl = "http://127.0.0.1:23119/zotxt/"
zotxturlselect = zotxturl + 'select?'
linkurl = "zotero://select/items/"
pattern = re.escape(linkurl) + r'([@]*)(.+)'
pattern = re.compile(pattern)

def main(arg):
    data = {}
    m = pattern.match(arg)
    if m.group(1) == '@':
        data['betterbibtexkey'] = m.group(2)
    else:
        data['key'] = m.group(2)
    data = urlencode(data)
    url = zotxturlselect + data
    try:
        urlopen(url)
    except Exception as e:
        print(f'ERROR: got an exception {e}\n{m.group(0)}\n{url}')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This program use zotxt to select an '
            'entry in Zotero')
    parser.add_argument('url', help='Zotero URL')

    args = parser.parse_args()
    main(args.url)
