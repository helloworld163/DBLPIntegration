# encoding: utf-8

from pinyin import PinYin
from btpyparse import parse_str as parse_bibtex
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import json
from DBLPAuthor import DBLPAuthor
from CDBLPAuthor import CDBLPAuthor

class DBLPQuery:

    def __init__(self):
        pass

    @staticmethod
    def get_publications_by_author():
        """
        1. Get author's publications from C-DBLP and DBLP
        2. Merge
        """
        pass

    @staticmethod
    def get_coauthors_by_author():
        """
        1. Get author's coauthors from C-DBLP (co-a1) and DBLP (co-a2)
        2. Merge (for intersections of co-a1 and co-a2, judge then merge)
        """
        pass

    @staticmethod
    def get_venues_by_author():
        """
        1. Get author's publications from C-DBLP and DBLP (get_publications_by_author)
        2. Get venues involved
        3. Merge
        """
        pass

    @staticmethod
    def get_authors_by_venue_year():
        """
        1. Read parameters ([{venue: 'SIGMOD', year: 2012}, ...])
        2. Parse parameters to proper query form (DBLP venue by CompleteSearch, C-DBLP venue by manually specifying)
        3. Get authors from each venues (by year)
        4. Merge authors
        """
        pass

    @staticmethod
    def get_coauthored_publications_by_authors():
        """
        1. Get authors' publications
        2. Merge publications
        """
        pass

    @staticmethod
    def get_sample_users():
        cache = open('author-cache.data', 'w')
        piy = PinYin()
        piy.load_word()
        author_list = []
        res = urlopen('http://easyscholar.ruc.edu.cn/moreuser.html')
        dom = BeautifulSoup(res)
        author_tags = dom.find_all(href=re.compile('^homepage/'))
        for author_tag in author_tags:
            if author_tag.findChild('strong'):
                #print(author_tag.findChild('strong').contents)
                author_name = CDBLPAuthor.getEnglishName(author_tag.findChild('strong').contents[0])
                author_list.append(author_name)
                #print('{} {}'.format(author_name['full_name'], author_name['zh']))
                #print(CDBLPAuthor.getEnglishName(author_tag.findChild('strong').contents[0])['full_name'])
                #print(piy.hanzi2pinyin(author_tag.findChild('strong').contents[0]))

        cache.write(json.dumps(author_list))
        cache.close()
        return author_list

    @staticmethod
    def get_cached_authors():
        cache = open('author-cache.data', 'r')
        author_list = json.loads(cache.read())
        cache.close()
        return author_list
        
#test = PinYin()
#test.load_word()
#print(test.hanzi2pinyin('郑庆华'))
#
#author = CDBLPAuthor("郑庆华")
#l1 = author.get_coauthors()
#
#author_q = DBLPAuthor('z/Zheng:Qinghua', '郑庆华')
#l2 = author_q.get_coauthors()
#
#print(set(l1).intersection(set(l2)))

#author_name = '李丽'
#author_CDBLP = CDBLPAuthor(author_name)
#search_name = '{0} {1}'.format(author_CDBLP.author_name_en['first_name'], author_CDBLP.author_name_en['last_name'])
##print(search_name)
##print(DBLPAuthor.get_authors('{0} {1}'.format(author_CDBLP.author_name_en['first_name'], author_CDBLP.author_name_en['last_name'])))
#author_DBLP = [DBLPAuthor(author_urlpt) for author_urlpt in DBLPAuthor.get_authors(search_name)]
#l2 = author_CDBLP.get_coauthors()
#
#for a in author_DBLP:
#    l1 = a.get_coauthors()
#    print('Coauthors of {0} and {1}:'.format(author_name, a.author_urlpt))
#    print(set(l1).intersection(set(l2)))

print(DBLPQuery.get_cached_authors())