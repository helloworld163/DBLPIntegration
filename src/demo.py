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
import datetime

class DBLPQuery:

    base_url = 'http://dblp.dagstuhl.de'

    @staticmethod
    def author_distinct(cached_list, cached_set, author_name):
        trial = author_name[0]

        if author_name in cached_set:
            d = json.loads(open('author-entries-cache.data', 'r').read())
            print('This is a CDBLP author w/ a English name on file.')
            author_name_zh = ''
            for author_name_comp in cached_list:
                if author_name_comp['full_name'] == author_name.strip() or author_name_comp['zh'] == author_name:
                    author_name_zh = author_name_comp['zh']
                    break

            return {
                'cdblp': d.get(author_name_zh, {}),
                'dblp': DBLPAuthor('{}/{}:{}'.format(author_name_comp['last_name'][0].lower(), author_name_comp['last_name'], author_name_comp['first_name'])).get_author()
            }

        else:
            if 0x3400 < ord(trial) < 0x2b6f8:
                print('This is a CDBLP author w/ a Chinese name.')

                author_cdblp = CDBLPAuthor(author_name)
                author_name_comp = CDBLPAuthor.getEnglishName(author_name)

                res = urlopen('{}/search/author?xauthor={}'.format(DBLPQuery.base_url, quote(author_name_comp['full_name'])))
                dom = BeautifulSoup(res)

                candidate_authors = []
                author_tags = dom.find_all('author')

                for author_tag in author_tags:
                    if author_tag.string == author_name_comp['full_name']:
                        author = DBLPAuthor(author_tag['urlpt'])
                        candidate_authors.append(author)

                # for example, '骞雅楠' => 'Ya-nan Qian' in DBLP
                if len(candidate_authors) == 0 and len(author_name) == 3:
                    res = urlopen('{}/search/author?xauthor={}'.format(DBLPQuery.base_url, quote(author_name_comp['full_name_dash'])))
                    dom = BeautifulSoup(res)

                    author_tags = dom.find_all('author')
                    for author_tag in author_tags:
                        if author_tag.string == author_name_comp['full_name_dash']:
                            author = DBLPAuthor(author_tag['urlpt'])
                            candidate_authors.append(author)

                try:
                    target_author = candidate_authors[0]
                except IndexError:
                    return { 'cdblp': author_cdblp.get_author(), 'dblp': {} }

                coauthors_set_cdblp = set(map(lambda a: a['full_name'], author_cdblp.get_coauthors()))
                coauthors_set_dblp  = set(candidate_authors[0].get_coauthors())
                coauthor_count_max = len(set(coauthors_set_cdblp.intersection(coauthors_set_dblp)))
                overlap = coauthors_set_cdblp.intersection(coauthors_set_dblp)

                if len(candidate_authors) > 1:
                    for candidate in candidate_authors:
                        coauthors_set_dblp  = set(candidate.get_coauthors())
                        coauthor_overlap = coauthors_set_cdblp.intersection(coauthors_set_dblp)

                        if len(coauthor_overlap) >= coauthor_count_max:
                            target_author = candidate
                            overlap = coauthor_overlap

                else:
                    target_author = candidate_authors[0]

                #print(overlap)
                return { 'cdblp': author_cdblp.get_author(), 'dblp': target_author.get_author() }

            else:
                print('This is a non-CDBLP author.')
                candidates = []
                res = urlopen('{}/search/author?xauthor={}'.format(DBLPQuery.base_url, quote(author_name)))
                dom = BeautifulSoup(res)
                for candidate_tag in dom.find_all('author'):
                    if author_name == candidate_tag.string:
                        candidates.append(DBLPAuthor(candidate_tag['urlpt']))

                return { 'cdblp': {}, 'dblp': candidates[0].get_author() }

    @staticmethod
    def get_publications_by_author(cached_list, cached_set, author_name):
        """
        1. Get author's publications from C-DBLP and DBLP
        2. Merge
        """
        publications = { 'dblp': [], 'cdblp': [] }
        author = DBLPQuery.author_distinct(cached_list, cached_set, author_name)

        if author['dblp'].__contains__('publications'):
            publications['dblp'] = author['dblp']['publications']
#            for pub in author['dblp']['publications']:
#                print(pub)

        if author['cdblp'].__contains__('publications'):
            publications['cdblp'] = author['cdblp']['publications']
#            for pub in author['cdblp']['publications']:
#                print(pub)
        return publications

    @staticmethod
    def get_coauthors_by_author(cached_list, cached_set, author_name):
        """
        1. Get author's coauthors from C-DBLP (co-a1) and DBLP (co-a2)
        2. Merge (for intersections of co-a1 and co-a2, judge then merge)
        """
        author = DBLPQuery.author_distinct(cached_list, cached_set, author_name)
        coauthors = {}
        if author['dblp'].__contains__('coauthors'):
            for author_key in author['dblp']['coauthors']:
                coauthors[author_key] = { 'en': author_key, 'zh': '' }

        if author['cdblp'].__contains__('coauthors'):
            for author_key in author['cdblp']['coauthors']:
                if coauthors.__contains__(author_key['full_name']):
                    coauthors[author_key['full_name']]['zh'] = author_key['zh']
                else:
                    coauthors[author_key['full_name']] = { 'en': author_key['full_name'], 'zh': author_key['zh'] }

        return coauthors


    @staticmethod
    def get_venues_by_author(cached_list, cached_set, author_name):
        """
        1. Get author's publications from C-DBLP and DBLP (get_publications_by_author)
        2. Get venues involved
        3. Merge
        """
        author = DBLPQuery.author_distinct(cached_list, cached_set, author_name)
        venues = {}

        if author['dblp'].__contains__('publications'):
            for pub in author['dblp']['publications']:
                if venues.__contains__(pub['venue']):
                    venues[pub['venue']]['count'] += 1
                else:
                    venues[pub['venue']] = { 'type': pub['venue-type'], 'count': 1 }

        if author['cdblp'].__contains__('publications'):
            for pub in author['cdblp']['publications']:
                if venues.__contains__(pub['venue']):
                    venues[pub['venue']]['count'] += 1
                else:
                    venues[pub['venue']] = { 'type': pub['venue-type'], 'count': 1 }

        return venues

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
    def get_coauthored_publications_by_authors(cached_list, cached_set, author1_name, author2_name):
        """
        1. Get authors' publications
        2. Merge publications
        """
        publications = []
        pub1 = DBLPQuery.get_publications_by_author(cached_list, cached_set, author1_name)
        author2 = DBLPQuery.author_distinct(cached_list, cached_set, author2_name)
        #pub2 = DBLPQuery.get_publications_by_author(cached_list, cached_set, author2_name)
        for cdblp_pub in pub1.get('cdblp', []):
            authors = set(cdblp_pub.get('authors', []))
            authors_en = set(map(lambda a: CDBLPAuthor.getEnglishName(a)['full_name'], authors))
            if author2.get('cdblp', {}).get('author_name', {}).get('zh') in authors or author2.get('dblp', {}).get('author_name') in authors_en:
                print(cdblp_pub)

        for dblp_pub in pub1.get('dblp', []):
            authors = set(map(lambda a: a.get('name'), dblp_pub.get('authors', [])))
            if author2.get('dblp', {}).get('author_name') in authors or author2.get('cdblp', {}).get('author_name', {}).get('full_name') in authors:
                print(dblp_pub)



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

cached_author_list = DBLPQuery.get_cached_authors()
name_set = set(map(lambda a: a['full_name'], cached_author_list)).union(set(map(lambda a: a['zh'], cached_author_list)))

#DBLPQuery.get_publications_by_author(name_set, '高文')
#author = DBLPQuery.author_distinct(cached_author_list, name_set, 'Guohui Li')
#try:
#    print(author['dblp'][0].author_urlpt)
#except IndexError as e:
#    print('This author is not existed in DBLP database.')
#
#try:
#    print(author['cdblp'][0].author_name['zh'])
#except IndexError as e:
#    print('This author is not existed in C-DBLP database.')

#DBLPQuery.get_publications_by_author(cached_author_list, name_set, 'Xiaofeng Meng')

#d = DBLPQuery.get_coauthors_by_author(cached_author_list, name_set, '郑庆华')

#d = DBLPQuery.get_venues_by_author(cached_author_list, name_set, 'Xifeng Yan')
#l = []
#for k in d.keys():
#    l.append({ 'venue': k, 'count': d[k]['count'] })
#
#l.sort(key=lambda i: i['count'], reverse=True)
#for i in l:
#    print(i)
#DBLPQuery.get_coauthored_publications_by_authors(cached_author_list, name_set, '田振华', '郑庆华')

# TO-DO
# 1. More queries
# 2. Web interface