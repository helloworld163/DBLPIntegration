# encoding: utf-8

import json
from CDBLPAuthor import CDBLPAuthor

author_list = json.loads(open('author-cache.data', 'r').read())

authors = {}

id = 0
for author in author_list:
    author_name = author['zh'].strip()
    chunk = open('authors/{}-{}-entry.data'.format(id, author_name), 'r')
    try:
        authors[author_name] = json.loads(chunk.read())
    except ValueError:
        print(author_name)

    chunk.close()
    id += 1

cache = open('author-entries-cache.data', 'w')
cache.write(json.dumps(authors))
cache.close()