#!/bin/bash

echo $1 | sed 's/zotero/http/g' | xargs curl
