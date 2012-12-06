# encoding: utf-8

import threading
import datetime
import json
from CDBLPAuthor import CDBLPAuthor
from time import sleep

class AuthorThread(threading.Thread):

    authors = {}

    def __init__(self, author_name, id):
        threading.Thread.__init__(self)
        self.author_name = author_name
        self.id = id

    def run(self):
        author = CDBLPAuthor(self.author_name.strip())
        #AuthorThread.authors[self.author_name.strip()] = author.get_author()
        chunk = open('authors/{}-{}-entry.data'.format(self.id, self.author_name.strip()), 'w')
        chunk.write(json.dumps(author.get_author()))
        chunk.close()
        print(self.author_name + ' %d is done.' % self.id)

author_list = json.loads(open('author-cache.data', 'r').read())

id = 0
for author in author_list:
    t = AuthorThread(author['zh'], id)
    t.start()
    id += 1