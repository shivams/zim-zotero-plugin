#!/usr/bin/env python
'''
This is for testing communication with zotxt
'''

import requests
import json

root = "http://127.0.0.1:23119/zotxt" #Zotero root url
url = root + '/search?q=mccarthy'
r = requests.get(url)
resp = r.json()

for i in resp:
    key = '0_' + i['id'].split('/')[-1]
    print i['title'] + ">>" + root + '/select?key=' + key


